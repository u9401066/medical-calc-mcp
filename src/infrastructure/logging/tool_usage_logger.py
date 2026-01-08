"""
Tool Usage Logger - Structured logging for MCP tool usage analytics.

This module provides a structured logging system to track:
- Which tools are being used
- What parameters are provided
- Success/failure rates
- Calculation durations
- Agent patterns (tool sequences)

Design Principles:
- Non-blocking: Logging should never slow down calculations
- Structured: JSON format for easy analysis
- Privacy-aware: Never log PHI (Protected Health Information)
- Configurable: Can be enabled/disabled via environment variables

Usage:
    from src.infrastructure.logging import ToolUsageLogger

    logger = ToolUsageLogger.get_instance()
    
    # Log a tool call
    with logger.log_tool_call("sofa_score", params) as ctx:
        result = calculate(...)
        ctx.set_result(result)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any, Optional
from collections.abc import Generator
from contextlib import contextmanager


class LogLevel(Enum):
    """Log levels for tool usage events."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ToolUsageEvent:
    """
    Structured event for tool usage tracking.
    
    All fields are designed to be PHI-free.
    Parameter values are NOT logged, only parameter names.
    """
    # Event identification
    event_id: str
    timestamp: str
    
    # Tool information
    tool_id: str
    tool_category: str = ""  # e.g., "critical_care", "nephrology"
    
    # Call context
    param_names: list[str] = field(default_factory=list)  # NOT values!
    param_count: int = 0
    
    # Result summary (no actual values)
    success: bool = False
    has_warnings: bool = False
    warning_types: list[str] = field(default_factory=list)
    error_type: Optional[str] = None
    
    # Performance metrics
    duration_ms: float = 0.0
    
    # Session tracking (optional)
    session_id: Optional[str] = None
    sequence_number: int = 0  # Order in session
    previous_tool: Optional[str] = None  # For workflow analysis
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self), default=str)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SessionStats:
    """Statistics for a single session."""
    session_id: str
    start_time: str
    tool_calls: list[str] = field(default_factory=list)
    tool_sequence: list[str] = field(default_factory=list)
    success_count: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0


class ToolUsageLogger:
    """
    Singleton structured logger for tool usage analytics.
    
    Features:
    - Thread-safe singleton pattern
    - Structured JSON output
    - Session tracking for workflow analysis
    - Aggregated statistics
    - PHI-free by design
    
    Configuration via environment variables:
    - TOOL_USAGE_LOGGING_ENABLED: Enable/disable (default: true)
    - TOOL_USAGE_LOG_FILE: File path for JSON logs (optional)
    - TOOL_USAGE_LOG_LEVEL: Minimum log level (default: INFO)
    """
    
    _instance: Optional[ToolUsageLogger] = None
    _lock: Lock = Lock()
    
    def __new__(cls) -> ToolUsageLogger:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        
        self._initialized = True
        self._enabled = os.environ.get("TOOL_USAGE_LOGGING_ENABLED", "true").lower() == "true"
        self._log_level = LogLevel[os.environ.get("TOOL_USAGE_LOG_LEVEL", "INFO")]
        self._log_file = os.environ.get("TOOL_USAGE_LOG_FILE")
        
        # Internal state
        self._event_counter = 0
        self._counter_lock = Lock()
        
        # Session tracking
        self._current_session: Optional[SessionStats] = None
        self._session_lock = Lock()
        
        # Aggregated stats (in-memory)
        self._tool_usage_counts: dict[str, int] = {}
        self._tool_error_counts: dict[str, int] = {}
        self._tool_durations: dict[str, list[float]] = {}
        self._workflow_patterns: dict[str, int] = {}  # "tool_a->tool_b": count
        
        # Python logger for output
        self._logger = logging.getLogger("tool_usage")
        self._logger.setLevel(logging.DEBUG)
        
        # File handler if configured
        if self._log_file:
            handler = logging.FileHandler(self._log_file)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)
    
    @classmethod
    def get_instance(cls) -> ToolUsageLogger:
        """Get the singleton instance."""
        return cls()
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        with self._counter_lock:
            self._event_counter += 1
            return f"evt_{int(time.time())}_{self._event_counter}"
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new session for workflow tracking.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            The session ID
        """
        with self._session_lock:
            sid = session_id or f"sess_{int(time.time())}"
            self._current_session = SessionStats(
                session_id=sid,
                start_time=datetime.now(timezone.utc).isoformat()
            )
            return sid
    
    def end_session(self) -> Optional[SessionStats]:
        """
        End the current session and return stats.
        
        Returns:
            Session statistics if a session was active
        """
        with self._session_lock:
            stats = self._current_session
            self._current_session = None
            return stats
    
    @contextmanager
    def log_tool_call(
        self,
        tool_id: str,
        params: dict[str, Any],
        category: str = "",
    ) -> Generator[_ToolCallContext, None, None]:
        """
        Context manager for logging a tool call.
        
        Args:
            tool_id: The tool being called
            params: Parameters (only names are logged, not values!)
            category: Tool category (e.g., "critical_care")
            
        Yields:
            Context object for setting result information
            
        Example:
            with logger.log_tool_call("sofa_score", params) as ctx:
                result = calculate_sofa(**params)
                ctx.set_result(success=True, has_warnings=bool(result.warnings))
        """
        if not self._enabled:
            yield _ToolCallContext()
            return
        
        start_time = time.perf_counter()
        ctx = _ToolCallContext()
        
        # Get previous tool for workflow analysis
        previous_tool = None
        sequence_number = 0
        session_id = None
        
        with self._session_lock:
            if self._current_session:
                session_id = self._current_session.session_id
                sequence_number = len(self._current_session.tool_calls)
                if self._current_session.tool_sequence:
                    previous_tool = self._current_session.tool_sequence[-1]
                self._current_session.tool_calls.append(tool_id)
                self._current_session.tool_sequence.append(tool_id)
        
        try:
            yield ctx
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Create event
            event = ToolUsageEvent(
                event_id=self._generate_event_id(),
                timestamp=datetime.now(timezone.utc).isoformat(),
                tool_id=tool_id,
                tool_category=category,
                param_names=list(params.keys()),
                param_count=len(params),
                success=ctx.success,
                has_warnings=ctx.has_warnings,
                warning_types=ctx.warning_types,
                error_type=ctx.error_type,
                duration_ms=round(duration_ms, 2),
                session_id=session_id,
                sequence_number=sequence_number,
                previous_tool=previous_tool,
            )
            
            # Update aggregated stats
            self._update_stats(event)
            
            # Log the event
            self._log_event(event)
    
    def _update_stats(self, event: ToolUsageEvent) -> None:
        """Update aggregated statistics."""
        tool_id = event.tool_id
        
        # Usage count
        self._tool_usage_counts[tool_id] = self._tool_usage_counts.get(tool_id, 0) + 1
        
        # Error count
        if not event.success:
            self._tool_error_counts[tool_id] = self._tool_error_counts.get(tool_id, 0) + 1
        
        # Duration tracking
        if tool_id not in self._tool_durations:
            self._tool_durations[tool_id] = []
        self._tool_durations[tool_id].append(event.duration_ms)
        # Keep only last 1000 durations per tool
        if len(self._tool_durations[tool_id]) > 1000:
            self._tool_durations[tool_id] = self._tool_durations[tool_id][-1000:]
        
        # Workflow pattern
        if event.previous_tool:
            pattern = f"{event.previous_tool}->{tool_id}"
            self._workflow_patterns[pattern] = self._workflow_patterns.get(pattern, 0) + 1
        
        # Update session stats
        with self._session_lock:
            if self._current_session:
                self._current_session.total_duration_ms += event.duration_ms
                if event.success:
                    self._current_session.success_count += 1
                else:
                    self._current_session.error_count += 1
    
    def _log_event(self, event: ToolUsageEvent) -> None:
        """Output the event to configured destinations."""
        json_str = event.to_json()
        
        # Log to Python logger (goes to stderr or file)
        if event.success:
            self._logger.info(json_str)
        else:
            self._logger.warning(json_str)
    
    def get_statistics(self) -> dict[str, Any]:
        """
        Get aggregated usage statistics.
        
        Returns:
            Dictionary with usage stats, error rates, durations, and patterns
        """
        stats: dict[str, Any] = {
            "total_calls": sum(self._tool_usage_counts.values()),
            "unique_tools_used": len(self._tool_usage_counts),
            "tool_usage_counts": dict(sorted(
                self._tool_usage_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]),  # Top 20
            "tool_error_rates": {},
            "avg_durations_ms": {},
            "common_workflows": dict(sorted(
                self._workflow_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),  # Top 10 patterns
        }
        
        # Calculate error rates
        for tool_id, count in self._tool_usage_counts.items():
            errors = self._tool_error_counts.get(tool_id, 0)
            stats["tool_error_rates"][tool_id] = round(errors / count * 100, 1) if count > 0 else 0
        
        # Calculate average durations
        for tool_id, durations in self._tool_durations.items():
            if durations:
                stats["avg_durations_ms"][tool_id] = round(sum(durations) / len(durations), 2)
        
        return stats
    
    def reset_statistics(self) -> None:
        """Reset all aggregated statistics."""
        self._tool_usage_counts.clear()
        self._tool_error_counts.clear()
        self._tool_durations.clear()
        self._workflow_patterns.clear()


class _ToolCallContext:
    """Context object for setting tool call results."""
    
    def __init__(self) -> None:
        self.success: bool = False
        self.has_warnings: bool = False
        self.warning_types: list[str] = []
        self.error_type: Optional[str] = None
    
    def set_result(
        self,
        success: bool = True,
        has_warnings: bool = False,
        warning_types: Optional[list[str]] = None,
        error_type: Optional[str] = None,
    ) -> None:
        """
        Set the result of the tool call.
        
        Args:
            success: Whether the call succeeded
            has_warnings: Whether warnings were generated
            warning_types: Types of warnings (e.g., ["boundary_warning"])
            error_type: Type of error if failed (e.g., "validation_error")
        """
        self.success = success
        self.has_warnings = has_warnings
        self.warning_types = warning_types or []
        self.error_type = error_type


# Module-level convenience function
def get_logger() -> ToolUsageLogger:
    """Get the tool usage logger instance."""
    return ToolUsageLogger.get_instance()
