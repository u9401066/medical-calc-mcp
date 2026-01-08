"""
Logging infrastructure for the Medical Calculator MCP Server.

This module provides structured logging capabilities:
- ToolUsageLogger: Track tool usage patterns and analytics
- Session management for workflow analysis
- PHI-free logging by design

Usage:
    from src.infrastructure.logging import get_logger
    
    logger = get_logger()
    with logger.log_tool_call("sofa_score", params) as ctx:
        result = calculate(...)
        ctx.set_result(success=True)
"""

from .tool_usage_logger import (
    ToolUsageLogger,
    ToolUsageEvent,
    SessionStats,
    LogLevel,
    get_logger,
)

__all__ = [
    "ToolUsageLogger",
    "ToolUsageEvent",
    "SessionStats",
    "LogLevel",
    "get_logger",
]
