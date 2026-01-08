"""
Rate Limiter

Optional request rate limiting using token bucket algorithm.
Disabled by default - enable via SecurityConfig.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[float] = None, client_id: Optional[str] = None):
        super().__init__(message)
        self.retry_after = retry_after
        self.client_id = client_id


@dataclass
class TokenBucket:
    """
    Token bucket for rate limiting.

    Implements the token bucket algorithm:
    - Tokens are added at a fixed rate (refill_rate per second)
    - Each request consumes one token
    - Requests are rejected when no tokens available
    - Bucket has maximum capacity (burst size)
    """

    capacity: float  # Maximum tokens (burst size)
    tokens: float  # Current available tokens
    refill_rate: float  # Tokens per second
    last_update: float = field(default_factory=time.time)

    def consume(self, tokens: float = 1.0) -> bool:
        """
        Try to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume (default: 1)

        Returns:
            True if tokens consumed successfully, False if rate limited
        """
        now = time.time()

        # Refill tokens based on elapsed time
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_update = now

        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def time_until_available(self, tokens: float = 1.0) -> float:
        """
        Calculate time until tokens become available.

        Args:
            tokens: Number of tokens needed

        Returns:
            Seconds until tokens available
        """
        if self.tokens >= tokens:
            return 0.0

        needed = tokens - self.tokens
        return needed / self.refill_rate


class RateLimiter:
    """
    Rate limiter with per-client tracking.

    Features:
    - Token bucket algorithm for smooth rate limiting
    - Per-client (IP) rate limiting
    - Global rate limiting option
    - Thread-safe
    - Automatic cleanup of inactive clients

    Usage:
        limiter = RateLimiter(requests_per_minute=60, burst=10)

        # Check if request is allowed
        if limiter.is_allowed("client-ip"):
            process_request()
        else:
            raise RateLimitExceeded()

        # Or use check_and_raise (recommended)
        limiter.check_and_raise("client-ip")  # Raises if rate limited
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst: int = 10,
        per_client: bool = True,
        cleanup_interval: float = 300.0,  # 5 minutes
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum sustained request rate
            burst: Maximum burst size (token bucket capacity)
            per_client: If True, rate limit per client; if False, global limit
            cleanup_interval: Seconds between inactive client cleanup
        """
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.per_client = per_client
        self.cleanup_interval = cleanup_interval

        # Calculate tokens per second
        self.refill_rate = requests_per_minute / 60.0

        # Client buckets
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.time()

        # Global bucket (used when per_client=False)
        self._global_bucket = TokenBucket(capacity=float(burst), tokens=float(burst), refill_rate=self.refill_rate)

    def _get_bucket(self, client_id: str) -> TokenBucket:
        """Get or create token bucket for client."""
        if not self.per_client:
            return self._global_bucket

        with self._lock:
            if client_id not in self._buckets:
                self._buckets[client_id] = TokenBucket(capacity=float(self.burst), tokens=float(self.burst), refill_rate=self.refill_rate)
            return self._buckets[client_id]

    def is_allowed(self, client_id: str = "global") -> bool:
        """
        Check if a request is allowed.

        Args:
            client_id: Client identifier (e.g., IP address)

        Returns:
            True if request is allowed, False if rate limited
        """
        self._maybe_cleanup()
        bucket = self._get_bucket(client_id)
        return bucket.consume()

    def check_and_raise(self, client_id: str = "global") -> None:
        """
        Check rate limit and raise exception if exceeded.

        Args:
            client_id: Client identifier (e.g., IP address)

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        bucket = self._get_bucket(client_id)

        if not bucket.consume():
            retry_after = bucket.time_until_available()
            raise RateLimitExceeded(message=f"Rate limit exceeded. Try again in {retry_after:.1f} seconds.", retry_after=retry_after, client_id=client_id)

    def get_remaining(self, client_id: str = "global") -> int:
        """
        Get remaining requests for a client.

        Args:
            client_id: Client identifier

        Returns:
            Number of remaining requests (integer)
        """
        bucket = self._get_bucket(client_id)
        return int(bucket.tokens)

    def get_reset_time(self, client_id: str = "global") -> float:
        """
        Get time until bucket is fully refilled.

        Args:
            client_id: Client identifier

        Returns:
            Seconds until full capacity
        """
        bucket = self._get_bucket(client_id)
        needed = bucket.capacity - bucket.tokens
        if needed <= 0:
            return 0.0
        return needed / bucket.refill_rate

    def _maybe_cleanup(self) -> None:
        """Remove inactive client buckets to free memory."""
        now = time.time()
        if now - self._last_cleanup < self.cleanup_interval:
            return

        with self._lock:
            # Only cleanup if interval has passed (double-check with lock)
            if now - self._last_cleanup < self.cleanup_interval:
                return

            self._last_cleanup = now

            # Remove buckets that are full (inactive clients)
            inactive = [
                client_id
                for client_id, bucket in self._buckets.items()
                if bucket.tokens >= bucket.capacity * 0.99  # Nearly full = inactive
            ]

            for client_id in inactive:
                del self._buckets[client_id]

    def reset(self, client_id: Optional[str] = None) -> None:
        """
        Reset rate limit for a client or all clients.

        Args:
            client_id: Client to reset, or None for all clients
        """
        with self._lock:
            if client_id is None:
                self._buckets.clear()
                self._global_bucket.tokens = self._global_bucket.capacity
            elif client_id in self._buckets:
                self._buckets[client_id].tokens = self._buckets[client_id].capacity

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics."""
        with self._lock:
            return {
                "requests_per_minute": self.requests_per_minute,
                "burst": self.burst,
                "per_client": self.per_client,
                "active_clients": len(self._buckets),
                "global_remaining": int(self._global_bucket.tokens) if not self.per_client else None,
            }
