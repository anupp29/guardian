"""
Agent Registry - Central registry for all agents using Google ADK
"""

import logging
from typing import Dict, Any

# Engine removed - not available in google-adk

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
        self._engine = None  # Engine not available in google-adk
        self._initialized = False
    
    def _initialize_agents(self):
        """Lazy initialization of all agents"""
        if self._initialized:
            return
        
        logger.info("Initializing agent registry with Google ADK")
        
        # Initialize ADK Engine
        self._engine = Engine()
        logger.info("ADK Engine initialized")
        
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
    
    def get_engine(self):
        """
        Get ADK Engine instance.
        
        Returns:
            ADK Engine instance
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
