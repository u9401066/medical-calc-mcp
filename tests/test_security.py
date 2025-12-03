"""
Tests for Security Infrastructure

Tests rate limiting, authentication, and security middleware.
All security features are optional and disabled by default.
"""

import os
import time
import pytest
from unittest.mock import patch

from src.infrastructure.security import (
    SecurityConfig,
    RateLimiter,
    RateLimitExceeded,
    APIAuthenticator,
    AuthenticationError,
    SecurityMiddleware,
)


class TestSecurityConfig:
    """Tests for SecurityConfig"""
    
    def test_default_config_all_disabled(self):
        """Default config should have all security features disabled"""
        config = SecurityConfig()
        
        assert config.rate_limit_enabled is False
        assert config.auth_enabled is False
        assert config.is_security_enabled() is False
    
    def test_config_from_env_defaults(self):
        """from_env should return defaults when no env vars set"""
        # Clear any existing env vars
        env_vars = [
            "SECURITY_RATE_LIMIT_ENABLED",
            "SECURITY_AUTH_ENABLED",
            "SECURITY_API_KEYS",
        ]
        with patch.dict(os.environ, {}, clear=True):
            for var in env_vars:
                os.environ.pop(var, None)
            
            config = SecurityConfig.from_env()
            
            assert config.rate_limit_enabled is False
            assert config.auth_enabled is False
    
    def test_config_from_env_rate_limit_enabled(self):
        """Should enable rate limiting from env"""
        with patch.dict(os.environ, {
            "SECURITY_RATE_LIMIT_ENABLED": "true",
            "SECURITY_RATE_LIMIT_RPM": "100",
            "SECURITY_RATE_LIMIT_BURST": "20",
        }):
            config = SecurityConfig.from_env()
            
            assert config.rate_limit_enabled is True
            assert config.rate_limit_requests_per_minute == 100
            assert config.rate_limit_burst == 20
    
    def test_config_from_env_auth_enabled(self):
        """Should enable authentication from env"""
        with patch.dict(os.environ, {
            "SECURITY_AUTH_ENABLED": "true",
            "SECURITY_API_KEYS": "key1,key2,key3",
        }):
            config = SecurityConfig.from_env()
            
            assert config.auth_enabled is True
            assert config.auth_api_keys == ["key1", "key2", "key3"]
    
    def test_config_validation_auth_no_keys(self):
        """Should warn when auth enabled but no keys"""
        config = SecurityConfig(
            auth_enabled=True,
            auth_api_keys=[]
        )
        
        warnings = config.validate()
        assert len(warnings) == 1
        assert "no API keys" in warnings[0]
    
    def test_config_is_security_enabled(self):
        """is_security_enabled should return True when any feature enabled"""
        config1 = SecurityConfig(rate_limit_enabled=True)
        config2 = SecurityConfig(auth_enabled=True)
        config3 = SecurityConfig()
        
        assert config1.is_security_enabled() is True
        assert config2.is_security_enabled() is True
        assert config3.is_security_enabled() is False


class TestRateLimiter:
    """Tests for RateLimiter"""
    
    def test_basic_rate_limiting(self):
        """Should allow requests up to limit"""
        limiter = RateLimiter(requests_per_minute=60, burst=5)
        
        # First 5 requests should succeed (burst)
        for i in range(5):
            assert limiter.is_allowed("client1") is True
        
        # 6th request should fail (burst exceeded)
        assert limiter.is_allowed("client1") is False
    
    def test_rate_limit_recovery(self):
        """Should recover tokens over time"""
        limiter = RateLimiter(requests_per_minute=6000, burst=1)  # 100/sec
        
        # Use up burst
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False
        
        # Wait for refill
        time.sleep(0.02)  # 20ms should give ~2 tokens at 100/sec
        
        assert limiter.is_allowed("client1") is True
    
    def test_per_client_rate_limiting(self):
        """Should rate limit per client independently"""
        limiter = RateLimiter(requests_per_minute=60, burst=2, per_client=True)
        
        # Client 1 uses up burst
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False
        
        # Client 2 should still have full burst
        assert limiter.is_allowed("client2") is True
        assert limiter.is_allowed("client2") is True
    
    def test_global_rate_limiting(self):
        """Should rate limit globally when per_client=False"""
        limiter = RateLimiter(requests_per_minute=60, burst=2, per_client=False)
        
        # Both clients share the same bucket
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client2") is True
        assert limiter.is_allowed("client1") is False
        assert limiter.is_allowed("client2") is False
    
    def test_check_and_raise(self):
        """check_and_raise should raise RateLimitExceeded"""
        limiter = RateLimiter(requests_per_minute=60, burst=1)
        
        # First request OK
        limiter.check_and_raise("client1")
        
        # Second request should raise
        with pytest.raises(RateLimitExceeded) as exc_info:
            limiter.check_and_raise("client1")
        
        assert exc_info.value.retry_after > 0
        assert exc_info.value.client_id == "client1"
    
    def test_get_remaining(self):
        """Should return remaining requests"""
        limiter = RateLimiter(requests_per_minute=60, burst=5)
        
        assert limiter.get_remaining("client1") == 5
        limiter.is_allowed("client1")
        assert limiter.get_remaining("client1") == 4
    
    def test_reset(self):
        """Should reset rate limit for client"""
        limiter = RateLimiter(requests_per_minute=60, burst=2)
        
        # Use up burst
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        assert limiter.is_allowed("client1") is False
        
        # Reset
        limiter.reset("client1")
        assert limiter.is_allowed("client1") is True


class TestAPIAuthenticator:
    """Tests for APIAuthenticator"""
    
    def test_valid_api_key(self):
        """Should accept valid API key"""
        auth = APIAuthenticator(api_keys=["valid-key-12345"])
        
        assert auth.is_valid("valid-key-12345") is True
    
    def test_invalid_api_key(self):
        """Should reject invalid API key"""
        auth = APIAuthenticator(api_keys=["valid-key-12345"])
        
        assert auth.is_valid("wrong-key") is False
        assert auth.is_valid(None) is False
        assert auth.is_valid("") is False
    
    def test_multiple_api_keys(self):
        """Should accept any valid key from list"""
        auth = APIAuthenticator(api_keys=["key1-valid", "key2-valid", "key3-valid"])
        
        assert auth.is_valid("key1-valid") is True
        assert auth.is_valid("key2-valid") is True
        assert auth.is_valid("key3-valid") is True
        assert auth.is_valid("key4-invalid") is False
    
    def test_authenticate_success(self):
        """authenticate should return AuthResult on success"""
        auth = APIAuthenticator(api_keys=["test-api-key-12345"])
        
        result = auth.authenticate("test-api-key-12345")
        
        assert result.authenticated is True
        assert result.api_key_id == "test****2345"
    
    def test_authenticate_missing_key(self):
        """authenticate should raise for missing key"""
        auth = APIAuthenticator(api_keys=["valid-key-12345"])
        
        with pytest.raises(AuthenticationError) as exc_info:
            auth.authenticate(None)
        
        assert exc_info.value.error_code == "MISSING_API_KEY"
    
    def test_authenticate_invalid_key(self):
        """authenticate should raise for invalid key"""
        auth = APIAuthenticator(api_keys=["valid-key-12345"])
        
        with pytest.raises(AuthenticationError) as exc_info:
            auth.authenticate("wrong-key")
        
        assert exc_info.value.error_code == "INVALID_API_KEY"
    
    def test_extract_key_from_headers(self):
        """Should extract API key from headers"""
        auth = APIAuthenticator(header_name="X-API-Key")
        
        # Standard header
        assert auth.extract_key_from_headers({"X-API-Key": "my-key"}) == "my-key"
        
        # Case insensitive
        assert auth.extract_key_from_headers({"x-api-key": "my-key"}) == "my-key"
        
        # Bearer token
        assert auth.extract_key_from_headers(
            {"Authorization": "Bearer my-token"}
        ) == "my-token"
        
        # ApiKey scheme
        assert auth.extract_key_from_headers(
            {"Authorization": "ApiKey my-token"}
        ) == "my-token"
        
        # No key
        assert auth.extract_key_from_headers({"Other": "value"}) is None
    
    def test_extract_key_from_query(self):
        """Should extract API key from query params"""
        auth = APIAuthenticator(query_param="api_key")
        
        assert auth.extract_key_from_query({"api_key": "my-key"}) == "my-key"
        assert auth.extract_key_from_query({"other": "value"}) is None
    
    def test_extract_key_priority(self):
        """Headers should take priority over query params"""
        auth = APIAuthenticator(api_keys=["header-key", "query-key"])
        
        key = auth.extract_key(
            headers={"X-API-Key": "header-key"},
            query_params={"api_key": "query-key"}
        )
        
        assert key == "header-key"
    
    def test_add_remove_key(self):
        """Should add and remove keys dynamically"""
        auth = APIAuthenticator()
        
        assert auth.is_valid("new-key-12345") is False
        
        auth.add_key("new-key-12345")
        assert auth.is_valid("new-key-12345") is True
        
        auth.remove_key("new-key-12345")
        assert auth.is_valid("new-key-12345") is False
    
    def test_generate_api_key(self):
        """Should generate secure random keys"""
        key1 = APIAuthenticator.generate_api_key()
        key2 = APIAuthenticator.generate_api_key()
        
        assert len(key1) >= 32
        assert key1 != key2  # Should be unique
    
    def test_mask_key(self):
        """Should mask API key for logging"""
        assert APIAuthenticator._mask_key("abcd1234wxyz5678") == "abcd****5678"
        assert APIAuthenticator._mask_key("short") == "****"


class TestSecurityMiddleware:
    """Tests for SecurityMiddleware"""
    
    def test_disabled_by_default(self):
        """Middleware should be disabled by default"""
        middleware = SecurityMiddleware(SecurityConfig())
        
        assert middleware.is_enabled() is False
        
        # Should allow all requests
        ctx = middleware.check_request(client_id="any-client")
        assert ctx.client_id == "any-client"
    
    def test_rate_limiting_only(self):
        """Should enforce rate limiting when enabled"""
        config = SecurityConfig(
            rate_limit_enabled=True,
            rate_limit_requests_per_minute=60,
            rate_limit_burst=2
        )
        middleware = SecurityMiddleware(config)
        
        # First 2 requests OK
        middleware.check_request(client_id="client1")
        middleware.check_request(client_id="client1")
        
        # Third should fail
        with pytest.raises(RateLimitExceeded):
            middleware.check_request(client_id="client1")
    
    def test_auth_only(self):
        """Should enforce authentication when enabled"""
        config = SecurityConfig(
            auth_enabled=True,
            auth_api_keys=["valid-key-12345"]
        )
        middleware = SecurityMiddleware(config)
        
        # Valid key OK
        ctx = middleware.check_request(
            client_id="client1",
            headers={"X-API-Key": "valid-key-12345"}
        )
        assert ctx.api_key_id is not None
        
        # Invalid key fails
        with pytest.raises(AuthenticationError):
            middleware.check_request(
                client_id="client1",
                headers={"X-API-Key": "wrong-key"}
            )
        
        # Missing key fails
        with pytest.raises(AuthenticationError):
            middleware.check_request(client_id="client1")
    
    def test_both_enabled(self):
        """Should enforce both rate limiting and auth"""
        config = SecurityConfig(
            rate_limit_enabled=True,
            rate_limit_requests_per_minute=60,
            rate_limit_burst=2,
            auth_enabled=True,
            auth_api_keys=["valid-key-12345"]
        )
        middleware = SecurityMiddleware(config)
        
        # Auth first, then rate limit
        middleware.check_request(
            client_id="client1",
            headers={"X-API-Key": "valid-key-12345"}
        )
        middleware.check_request(
            client_id="client1",
            headers={"X-API-Key": "valid-key-12345"}
        )
        
        # Rate limit exceeded (auth passes but rate limit fails)
        with pytest.raises(RateLimitExceeded):
            middleware.check_request(
                client_id="client1",
                headers={"X-API-Key": "valid-key-12345"}
            )
        
        # Auth fails before rate limit is checked
        with pytest.raises(AuthenticationError):
            middleware.check_request(
                client_id="client2",
                headers={"X-API-Key": "wrong-key"}
            )
    
    def test_rate_limit_headers(self):
        """Should return rate limit headers"""
        config = SecurityConfig(
            rate_limit_enabled=True,
            rate_limit_requests_per_minute=60,
            rate_limit_burst=10
        )
        middleware = SecurityMiddleware(config)
        
        headers = middleware.get_rate_limit_headers("client1")
        
        assert "X-RateLimit-Limit" in headers
        assert headers["X-RateLimit-Limit"] == "60"
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
    
    def test_rate_limit_headers_disabled(self):
        """Should return empty headers when rate limiting disabled"""
        middleware = SecurityMiddleware(SecurityConfig())
        
        headers = middleware.get_rate_limit_headers("client1")
        assert headers == {}
    
    def test_get_stats(self):
        """Should return middleware statistics"""
        config = SecurityConfig(
            rate_limit_enabled=True,
            auth_enabled=True,
            auth_api_keys=["valid-api-key-12345"]  # Must be at least 8 chars
        )
        middleware = SecurityMiddleware(config)
        
        stats = middleware.get_stats()
        
        assert stats["security_enabled"] is True
        assert stats["rate_limit_enabled"] is True
        assert stats["auth_enabled"] is True
        assert "rate_limiter" in stats
        assert "authenticator" in stats


class TestSecurityIntegration:
    """Integration tests for security features"""
    
    def test_end_to_end_disabled(self):
        """End-to-end test with security disabled"""
        config = SecurityConfig()
        middleware = SecurityMiddleware(config)
        
        # Should process any request without issues
        for i in range(100):
            ctx = middleware.check_request(
                client_id=f"client-{i}",
                headers={"X-API-Key": "any-key"}
            )
            assert ctx is not None
    
    def test_end_to_end_rate_limit(self):
        """End-to-end test with rate limiting"""
        config = SecurityConfig(
            rate_limit_enabled=True,
            rate_limit_requests_per_minute=60,
            rate_limit_burst=5
        )
        middleware = SecurityMiddleware(config)
        
        # 5 requests succeed
        for i in range(5):
            middleware.check_request(client_id="test-client")
        
        # 6th fails
        with pytest.raises(RateLimitExceeded):
            middleware.check_request(client_id="test-client")
        
        # Different client still works
        middleware.check_request(client_id="other-client")
    
    def test_end_to_end_auth(self):
        """End-to-end test with authentication"""
        api_key = APIAuthenticator.generate_api_key()
        
        config = SecurityConfig(
            auth_enabled=True,
            auth_api_keys=[api_key]
        )
        middleware = SecurityMiddleware(config)
        
        # Valid key works
        ctx = middleware.check_request(
            client_id="client",
            headers={"X-API-Key": api_key}
        )
        assert ctx.api_key_id is not None
        
        # Query param also works
        ctx = middleware.check_request(
            client_id="client",
            query_params={"api_key": api_key}
        )
        assert ctx.api_key_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
