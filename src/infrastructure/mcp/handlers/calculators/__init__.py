"""
Calculator Tool Handlers

Organized by specialty/category for maintainability.
Each module registers its own MCP tools.
"""

from .nephrology import register_nephrology_tools
from .anesthesiology import register_anesthesiology_tools
from .critical_care import register_critical_care_tools
from .pediatric import register_pediatric_tools
from .pulmonology import register_pulmonology_tools
from .cardiology import register_cardiology_tools
from .emergency import register_emergency_tools
from .hepatology import register_hepatology_tools
from .surgery import register_surgery_tools
from .acid_base import register_acid_base_tools
from .hematology import register_hematology_tools
from .neurology import register_neurology_tools

__all__ = [
    "register_nephrology_tools",
    "register_anesthesiology_tools",
    "register_critical_care_tools",
    "register_pediatric_tools",
    "register_pulmonology_tools",
    "register_cardiology_tools",
    "register_emergency_tools",
    "register_hepatology_tools",
    "register_surgery_tools",
    "register_acid_base_tools",
    "register_hematology_tools",
    "register_neurology_tools",
]
