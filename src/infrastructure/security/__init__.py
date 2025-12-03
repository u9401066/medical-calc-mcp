"""
Security Infrastructure Module

Optional security features for the Medical Calculator MCP Server.
All features are disabled by default and can be enabled via configuration.

Features:
- Rate Limiting: Throttle requests to prevent abuse
- API Authentication: API Key based authentication

Usage:
    from src.infrastructure.security import SecurityConfig, RateLimiter, APIAuthenticator
    
    # Create security config (all disabled by default)
    config = SecurityConfig.from_env()
    
    # Or enable specific features
    config = SecurityConfig(
        rate_limit_enabled=True,
        rate_limit_requests_per_minute=60,
        auth_enabled=True,
        auth_api_keys=["your-api-key"]
    )
"""

from .config import SecurityConfig
from .rate_limiter import RateLimiter, RateLimitExceeded
from .authenticator import APIAuthenticator, AuthenticationError
from .middleware import SecurityMiddleware

__all__ = [
    "SecurityConfig",
    "RateLimiter",
    "RateLimitExceeded", 
    "APIAuthenticator",
    "AuthenticationError",
    "SecurityMiddleware",
]
