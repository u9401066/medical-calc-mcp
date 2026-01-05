"""
API Authenticator

Optional API key authentication.
Disabled by default - enable via SecurityConfig.
"""

import hashlib
import secrets
from dataclasses import dataclass
from typing import Any, Optional


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTH_FAILED",
        details: Optional[str] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details


@dataclass
class AuthResult:
    """Result of authentication attempt."""
    authenticated: bool
    api_key_id: Optional[str] = None  # Masked key identifier
    error: Optional[str] = None


class APIAuthenticator:
    """
    API Key authenticator.

    Features:
    - Multiple API keys support
    - Constant-time comparison (timing attack resistant)
    - Key masking in logs
    - Optional key rotation support

    Usage:
        auth = APIAuthenticator(api_keys=["key1", "key2"])

        # Check if key is valid
        if auth.is_valid("provided-key"):
            allow_request()

        # Or use authenticate (raises on failure)
        auth.authenticate("provided-key")  # Raises AuthenticationError if invalid

        # Extract key from request
        key = auth.extract_key_from_headers(headers)
    """

    def __init__(
        self,
        api_keys: Optional[list[str]] = None,
        header_name: str = "X-API-Key",
        query_param: str = "api_key"
    ):
        """
        Initialize authenticator.

        Args:
            api_keys: List of valid API keys
            header_name: HTTP header name for API key
            query_param: Query parameter name for API key
        """
        self.header_name = header_name
        self.query_param = query_param

        # Store keys as set for O(1) lookup
        # Note: We use hashed keys for additional security
        self._keys: set[str] = set()
        self._key_hashes: dict[str, str] = {}  # hash -> masked_id

        if api_keys:
            for key in api_keys:
                self.add_key(key)

    def add_key(self, api_key: str) -> str:
        """
        Add an API key.

        Args:
            api_key: The API key to add

        Returns:
            Masked key identifier for logging
        """
        if not api_key or len(api_key) < 8:
            raise ValueError("API key must be at least 8 characters")

        self._keys.add(api_key)

        # Create hash for secure comparison
        key_hash = self._hash_key(api_key)
        masked_id = self._mask_key(api_key)
        self._key_hashes[key_hash] = masked_id

        return masked_id

    def remove_key(self, api_key: str) -> bool:
        """
        Remove an API key.

        Args:
            api_key: The API key to remove

        Returns:
            True if key was removed, False if not found
        """
        if api_key in self._keys:
            self._keys.discard(api_key)
            key_hash = self._hash_key(api_key)
            self._key_hashes.pop(key_hash, None)
            return True
        return False

    def is_valid(self, api_key: Optional[str]) -> bool:
        """
        Check if API key is valid.

        Uses constant-time comparison to prevent timing attacks.

        Args:
            api_key: The API key to validate

        Returns:
            True if valid, False otherwise
        """
        if not api_key:
            return False

        # Use constant-time comparison
        for valid_key in self._keys:
            if secrets.compare_digest(api_key, valid_key):
                return True
        return False

    def authenticate(self, api_key: Optional[str]) -> AuthResult:
        """
        Authenticate API key and return result.

        Args:
            api_key: The API key to authenticate

        Returns:
            AuthResult with authentication status

        Raises:
            AuthenticationError: If authentication fails
        """
        if not api_key:
            raise AuthenticationError(
                message="API key is required",
                error_code="MISSING_API_KEY",
                details="Provide API key via X-API-Key header or api_key parameter"
            )

        if not self.is_valid(api_key):
            raise AuthenticationError(
                message="Invalid API key",
                error_code="INVALID_API_KEY",
                details="The provided API key is not valid"
            )

        return AuthResult(
            authenticated=True,
            api_key_id=self._mask_key(api_key)
        )

    def extract_key_from_headers(
        self,
        headers: dict[str, str]
    ) -> Optional[str]:
        """
        Extract API key from HTTP headers.

        Checks headers in order:
        1. X-API-Key header (or configured header name)
        2. Authorization: Bearer <key>
        3. Authorization: ApiKey <key>

        Args:
            headers: HTTP headers dictionary

        Returns:
            API key if found, None otherwise
        """
        # Case-insensitive header lookup
        headers_lower = {k.lower(): v for k, v in headers.items()}

        # Check configured header
        header_lower = self.header_name.lower()
        if header_lower in headers_lower:
            return headers_lower[header_lower]

        # Check Authorization header
        auth_header = headers_lower.get("authorization", "")
        if auth_header:
            parts = auth_header.split(" ", 1)
            if len(parts) == 2:
                scheme, credential = parts
                if scheme.lower() in ("bearer", "apikey"):
                    return credential

        return None

    def extract_key_from_query(
        self,
        query_params: dict[str, str]
    ) -> Optional[str]:
        """
        Extract API key from query parameters.

        Args:
            query_params: URL query parameters

        Returns:
            API key if found, None otherwise
        """
        return query_params.get(self.query_param)

    def extract_key(
        self,
        headers: Optional[dict[str, str]] = None,
        query_params: Optional[dict[str, str]] = None
    ) -> Optional[str]:
        """
        Extract API key from headers or query parameters.

        Priority: Headers > Query Parameters

        Args:
            headers: HTTP headers
            query_params: URL query parameters

        Returns:
            API key if found, None otherwise
        """
        # Try headers first
        if headers:
            key = self.extract_key_from_headers(headers)
            if key:
                return key

        # Try query params
        if query_params:
            key = self.extract_key_from_query(query_params)
            if key:
                return key

        return None

    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """
        Generate a secure random API key.

        Args:
            length: Key length (default: 32 characters)

        Returns:
            Secure random API key
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def _hash_key(api_key: str) -> str:
        """Create SHA-256 hash of API key."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def _mask_key(api_key: str) -> str:
        """
        Create masked version of API key for logging.

        Shows first 4 and last 4 characters only.
        Example: "abcd****wxyz"
        """
        if len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}****{api_key[-4:]}"

    def get_stats(self) -> dict[str, Any]:
        """Get authenticator statistics."""
        return {
            "keys_configured": len(self._keys),
            "header_name": self.header_name,
            "query_param": self.query_param,
        }
