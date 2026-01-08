"""
Security Middleware

Combines rate limiting and authentication into a single middleware.
All features are optional and disabled by default.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional

from .authenticator import APIAuthenticator, AuthenticationError
from .config import SecurityConfig
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class RequestContext:
    """Context for a request being processed."""

    client_id: str = "unknown"
    api_key_id: Optional[str] = None
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class SecurityMiddleware:
    """
    Security middleware that combines rate limiting and authentication.

    All features are OPTIONAL and DISABLED by default.
    Configure via SecurityConfig or environment variables.

    Usage:
        # Create with default config (all disabled)
        middleware = SecurityMiddleware()

        # Or with custom config
        config = SecurityConfig(
            rate_limit_enabled=True,
            auth_enabled=True,
            auth_api_keys=["my-key"]
        )
        middleware = SecurityMiddleware(config)

        # Check request
        try:
            ctx = middleware.check_request(
                client_id="192.168.1.1",
                headers={"X-API-Key": "my-key"}
            )
            # Request allowed, ctx contains request context
        except (RateLimitExceeded, AuthenticationError) as e:
            # Request denied
            handle_error(e)
    """

    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        Initialize security middleware.

        Args:
            config: Security configuration (defaults from environment if None)
        """
        self.config = config or SecurityConfig.from_env()

        # Initialize rate limiter (if enabled)
        self._rate_limiter: Optional[RateLimiter] = None
        if self.config.rate_limit_enabled:
            self._rate_limiter = RateLimiter(
                requests_per_minute=self.config.rate_limit_requests_per_minute, burst=self.config.rate_limit_burst, per_client=self.config.rate_limit_by_ip
            )
            logger.info(f"Rate limiting enabled: {self.config.rate_limit_requests_per_minute} req/min, burst={self.config.rate_limit_burst}")

        # Initialize authenticator (if enabled)
        self._authenticator: Optional[APIAuthenticator] = None
        if self.config.auth_enabled:
            self._authenticator = APIAuthenticator(
                api_keys=self.config.auth_api_keys, header_name=self.config.auth_header_name, query_param=self.config.auth_query_param
            )
            logger.info(f"Authentication enabled: {len(self.config.auth_api_keys)} API key(s) configured")

        # Validate configuration
        warnings = self.config.validate()
        for warning in warnings:
            logger.warning(f"Security config warning: {warning}")

        # Log overall status
        if not self.config.is_security_enabled():
            logger.info("Security middleware: All features DISABLED (default)")
        else:
            logger.info(f"Security middleware initialized:\n{self.config}")

    def check_request(
        self, client_id: str = "unknown", headers: Optional[dict[str, str]] = None, query_params: Optional[dict[str, str]] = None
    ) -> RequestContext:
        """
        Check if a request is allowed.

        This method should be called before processing each request.
        It checks authentication first, then rate limiting.

        Args:
            client_id: Client identifier (e.g., IP address)
            headers: HTTP request headers
            query_params: URL query parameters

        Returns:
            RequestContext with request information

        Raises:
            AuthenticationError: If authentication fails (when enabled)
            RateLimitExceeded: If rate limit exceeded (when enabled)
        """
        ctx = RequestContext(client_id=client_id)

        # Log request (if enabled)
        if self.config.log_requests:
            logger.debug(f"Request from {client_id}")

        # Check authentication first (if enabled)
        if self._authenticator is not None:
            api_key = self._authenticator.extract_key(headers, query_params)
            try:
                result = self._authenticator.authenticate(api_key)
                ctx.api_key_id = result.api_key_id
            except AuthenticationError as e:
                if self.config.log_auth_failures:
                    logger.warning(f"Auth failed for {client_id}: {e.error_code}")
                raise

        # Check rate limit (if enabled)
        if self._rate_limiter is not None:
            self._rate_limiter.check_and_raise(client_id)

        return ctx

    def is_enabled(self) -> bool:
        """Check if any security feature is enabled."""
        return self.config.is_security_enabled()

    def get_rate_limit_headers(self, client_id: str = "unknown") -> dict[str, str]:
        """
        Get rate limit headers for HTTP response.

        Returns standard rate limit headers:
        - X-RateLimit-Limit: Maximum requests per period
        - X-RateLimit-Remaining: Remaining requests
        - X-RateLimit-Reset: Seconds until reset

        Args:
            client_id: Client identifier

        Returns:
            Dictionary of rate limit headers (empty if rate limiting disabled)
        """
        if self._rate_limiter is None:
            return {}

        return {
            "X-RateLimit-Limit": str(self.config.rate_limit_requests_per_minute),
            "X-RateLimit-Remaining": str(self._rate_limiter.get_remaining(client_id)),
            "X-RateLimit-Reset": str(int(self._rate_limiter.get_reset_time(client_id))),
        }

    def get_stats(self) -> dict[str, Any]:
        """Get security middleware statistics."""
        stats: dict[str, Any] = {
            "security_enabled": self.config.is_security_enabled(),
            "rate_limit_enabled": self.config.rate_limit_enabled,
            "auth_enabled": self.config.auth_enabled,
        }

        if self._rate_limiter:
            stats["rate_limiter"] = self._rate_limiter.get_stats()

        if self._authenticator:
            stats["authenticator"] = self._authenticator.get_stats()

        return stats

    def reset_rate_limit(self, client_id: Optional[str] = None) -> None:
        """
        Reset rate limit for a client or all clients.

        Args:
            client_id: Client to reset, or None for all
        """
        if self._rate_limiter:
            self._rate_limiter.reset(client_id)

    # Decorator for protecting functions
    def protect(self, get_client_id: Optional[Callable[..., str]] = None) -> Callable[..., Any]:
        """
        Decorator to protect a function with security checks.

        Usage:
            @middleware.protect()
            def my_handler(request):
                ...

            # With custom client ID extraction
            @middleware.protect(get_client_id=lambda req: req.remote_addr)
            def my_handler(request):
                ...

        Args:
            get_client_id: Function to extract client ID from arguments

        Returns:
            Decorated function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Extract client ID
                client_id = "unknown"
                if get_client_id:
                    try:
                        client_id = get_client_id(*args, **kwargs)
                    except Exception:
                        pass

                # Check security (may raise exceptions)
                self.check_request(client_id=client_id)

                # Call original function
                return func(*args, **kwargs)

            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper

        return decorator


# Convenience function to create middleware from environment
def create_security_middleware() -> SecurityMiddleware:
    """
    Create security middleware from environment variables.

    All features are disabled by default.
    Set environment variables to enable:

        SECURITY_RATE_LIMIT_ENABLED=true
        SECURITY_RATE_LIMIT_RPM=60
        SECURITY_AUTH_ENABLED=true
        SECURITY_API_KEYS=key1,key2

    Returns:
        Configured SecurityMiddleware
    """
    config = SecurityConfig.from_env()
    return SecurityMiddleware(config)
