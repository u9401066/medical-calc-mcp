"""
Calculator Tool Handlers

Organized by specialty/category for maintainability.
Each module registers its own MCP tools.
"""

from .nephrology import register_nephrology_tools
from .anesthesiology import register_anesthesiology_tools
from .critical_care import register_critical_care_tools
from .pediatric import register_pediatric_tools

__all__ = [
    "register_nephrology_tools",
    "register_anesthesiology_tools",
    "register_critical_care_tools",
    "register_pediatric_tools",
]
