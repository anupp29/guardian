"""
Agent Registry - Central registry for all agents using Google ADK
"""

import logging
from typing import Dict, Any, Optional

# Engine is optional - may not be available in all google-adk versions
try:
    from google.adk.core import Engine
    ENGINE_AVAILABLE = True
except ImportError:
    ENGINE_AVAILABLE = False
    Engine = None  # type: ignore

from .orchestrator.agent import OrchestratorAgent, orchestrator_agent
from .simulation.agent import SimulationAgent, simulation_agent
from .impact_reasoning.agent import ImpactReasoningAgent, impact_reasoning_agent
from .mitigation.agent import MitigationAgent, mitigation_agent


logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Central registry for all Guardian AI agents using Google ADK.
    Provides singleton access to agent instances and ADK Engine.
    """
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._adk_agents: Dict[str, Any] = {}
        self._engine: Optional[Any] = None
        self._initialized = False
    
    def _initialize_agents(self):
        """Lazy initialization of all agents"""
        if self._initialized:
            return
        
        logger.info("Initializing agent registry with Google ADK")
        
        # Initialize ADK Engine (if available)
        if ENGINE_AVAILABLE and Engine is not None:
            try:
                self._engine = Engine()
                logger.info("ADK Engine initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize ADK Engine: {e}")
                self._engine = None
        else:
            logger.info("ADK Engine not available in this google-adk version")
        
        # Initialize wrapper agents (for backward compatibility)
        self._agents["OrchestratorAgent"] = OrchestratorAgent()
        self._agents["SimulationAgent"] = SimulationAgent()
        self._agents["ImpactReasoningAgent"] = ImpactReasoningAgent()
        self._agents["MitigationAgent"] = MitigationAgent()
        
        # Store ADK agent instances
        self._adk_agents["OrchestratorAgent"] = orchestrator_agent
        self._adk_agents["SimulationAgent"] = simulation_agent
        self._adk_agents["ImpactReasoningAgent"] = impact_reasoning_agent
        self._adk_agents["MitigationAgent"] = mitigation_agent
        
        self._initialized = True
        logger.info(f"Registered {len(self._agents)} agents with Google ADK")
    
    def get_agent(self, agent_name: str):
        """
        Get agent instance by name (wrapper for backward compatibility).
        
        Args:
            agent_name: Name of the agent (e.g., "SimulationAgent")
            
        Returns:
            Agent instance (wrapper class)
            
        Raises:
            ValueError: If agent not found
        """
        if not self._initialized:
            self._initialize_agents()
        
        if agent_name not in self._agents:
            raise ValueError(f"Agent '{agent_name}' not found in registry. Available: {list(self._agents.keys())}")
        
        return self._agents[agent_name]
    
    def get_adk_agent(self, agent_name: str):
        """
        Get ADK agent instance by name.
        
        Args:
            agent_name: Name of the agent (e.g., "SimulationAgent")
            
        Returns:
            ADK Agent instance
            
        Raises:
            ValueError: If agent not found
        """
        if not self._initialized:
            self._initialize_agents()
        
        if agent_name not in self._adk_agents:
            raise ValueError(f"ADK Agent '{agent_name}' not found in registry. Available: {list(self._adk_agents.keys())}")
        
        return self._adk_agents[agent_name]
    
    def get_engine(self) -> Optional[Any]:
        """
        Get ADK Engine instance (if available).
        
        Returns:
            ADK Engine instance or None if not available
        """
        if not self._initialized:
            self._initialize_agents()
        
        return self._engine
    
    def list_agents(self) -> list:
        """List all registered agent names"""
        if not self._initialized:
            self._initialize_agents()
        return list(self._agents.keys())
    
    def list_adk_agents(self) -> list:
        """List all registered ADK agent names"""
        if not self._initialized:
            self._initialize_agents()
        return list(self._adk_agents.keys())


# Global registry instance
_registry = None


def get_registry() -> AgentRegistry:
    """Get global agent registry instance"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry

