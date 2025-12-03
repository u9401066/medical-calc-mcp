"""
Security Configuration

Configuration for optional security features.
All features are disabled by default.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SecurityConfig:
    """
    Security configuration for the MCP server.
    
    All security features are DISABLED by default.
    Enable via environment variables or programmatically.
    
    Environment Variables:
        SECURITY_RATE_LIMIT_ENABLED: "true" or "false" (default: "false")
        SECURITY_RATE_LIMIT_RPM: requests per minute (default: 60)
        SECURITY_RATE_LIMIT_BURST: burst size (default: 10)
        SECURITY_AUTH_ENABLED: "true" or "false" (default: "false")
        SECURITY_API_KEYS: comma-separated API keys
        SECURITY_LOG_REQUESTS: "true" or "false" (default: "false")
    
    Example:
        # Enable rate limiting only
        export SECURITY_RATE_LIMIT_ENABLED=true
        export SECURITY_RATE_LIMIT_RPM=100
        
        # Enable authentication only
        export SECURITY_AUTH_ENABLED=true
        export SECURITY_API_KEYS=key1,key2,key3
        
        # Enable both
        export SECURITY_RATE_LIMIT_ENABLED=true
        export SECURITY_AUTH_ENABLED=true
        export SECURITY_API_KEYS=my-secret-key
    """
    
    # Rate Limiting Configuration
    rate_limit_enabled: bool = False
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10  # Allow burst of requests
    rate_limit_by_ip: bool = True  # Rate limit per IP address
    
    # Authentication Configuration
    auth_enabled: bool = False
    auth_api_keys: List[str] = field(default_factory=list)
    auth_header_name: str = "X-API-Key"  # HTTP header for API key
    auth_query_param: str = "api_key"    # Query parameter alternative
    
    # Logging Configuration
    log_requests: bool = False  # Log all requests for audit
    log_auth_failures: bool = True  # Log authentication failures
    
    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """
        Create configuration from environment variables.
        
        Returns:
            SecurityConfig with values from environment or defaults
        """
        def parse_bool(value: Optional[str], default: bool = False) -> bool:
            if value is None:
                return default
            return value.lower() in ("true", "1", "yes", "on")
        
        def parse_int(value: Optional[str], default: int) -> int:
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                return default
        
        def parse_list(value: Optional[str]) -> List[str]:
            if value is None or value.strip() == "":
                return []
            return [k.strip() for k in value.split(",") if k.strip()]
        
        return cls(
            # Rate Limiting
            rate_limit_enabled=parse_bool(
                os.getenv("SECURITY_RATE_LIMIT_ENABLED"), False
            ),
            rate_limit_requests_per_minute=parse_int(
                os.getenv("SECURITY_RATE_LIMIT_RPM"), 60
            ),
            rate_limit_burst=parse_int(
                os.getenv("SECURITY_RATE_LIMIT_BURST"), 10
            ),
            rate_limit_by_ip=parse_bool(
                os.getenv("SECURITY_RATE_LIMIT_BY_IP"), True
            ),
            # Authentication
            auth_enabled=parse_bool(
                os.getenv("SECURITY_AUTH_ENABLED"), False
            ),
            auth_api_keys=parse_list(
                os.getenv("SECURITY_API_KEYS")
            ),
            auth_header_name=os.getenv("SECURITY_AUTH_HEADER", "X-API-Key"),
            auth_query_param=os.getenv("SECURITY_AUTH_PARAM", "api_key"),
            # Logging
            log_requests=parse_bool(
                os.getenv("SECURITY_LOG_REQUESTS"), False
            ),
            log_auth_failures=parse_bool(
                os.getenv("SECURITY_LOG_AUTH_FAILURES"), True
            ),
        )
    
    def is_security_enabled(self) -> bool:
        """Check if any security feature is enabled."""
        return self.rate_limit_enabled or self.auth_enabled
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of warnings/errors.
        
        Returns:
            List of warning messages (empty if valid)
        """
        warnings = []
        
        if self.auth_enabled and not self.auth_api_keys:
            warnings.append(
                "Authentication is enabled but no API keys are configured. "
                "Set SECURITY_API_KEYS environment variable."
            )
        
        if self.rate_limit_enabled and self.rate_limit_requests_per_minute < 1:
            warnings.append(
                "Rate limit requests per minute must be at least 1."
            )
        
        if self.rate_limit_burst < 1:
            warnings.append(
                "Rate limit burst must be at least 1."
            )
        
        return warnings
    
    def __str__(self) -> str:
        """Human-readable configuration summary."""
        lines = ["Security Configuration:"]
        
        if not self.is_security_enabled():
            lines.append("  All security features DISABLED (default)")
            return "\n".join(lines)
        
        if self.rate_limit_enabled:
            lines.append(f"  Rate Limiting: ENABLED")
            lines.append(f"    - {self.rate_limit_requests_per_minute} requests/minute")
            lines.append(f"    - Burst: {self.rate_limit_burst}")
            lines.append(f"    - Per IP: {self.rate_limit_by_ip}")
        else:
            lines.append("  Rate Limiting: disabled")
        
        if self.auth_enabled:
            lines.append(f"  Authentication: ENABLED")
            lines.append(f"    - {len(self.auth_api_keys)} API key(s) configured")
            lines.append(f"    - Header: {self.auth_header_name}")
        else:
            lines.append("  Authentication: disabled")
        
        return "\n".join(lines)
