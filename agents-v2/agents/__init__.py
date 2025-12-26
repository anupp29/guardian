"""
Guardian AI v2 - Multi-Agent System using Google ADK
"""

from .registry import AgentRegistry, get_registry

__version__ = "2.0.0"
__author__ = "Guardian AI Team"
__description__ = "Production-grade agentic decision-support system using Google ADK"

__all__ = [
    "AgentRegistry",
    "get_registry",
]