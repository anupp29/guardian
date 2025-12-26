"""Agent Registry for Guardian AI - centralizes agent initialization."""

import logging
from typing import Dict, Optional

from .orchestrator.agent import OrchestratorAgent
from .simulation.agent import SimulationAgent
from .impact_reasoning.agent import ImpactReasoningAgent
from .mitigation.agent import MitigationAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for Guardian AI agents."""
    
    def __init__(self, google_api_key: Optional[str] = None, graph_data: Optional[Dict] = None):
        logger.info("Initializing AgentRegistry")
        
        self.simulation_agent = SimulationAgent()
        self.impact_agent = ImpactReasoningAgent(api_key=google_api_key)
        self.mitigation_agent = MitigationAgent()
        
        self.orchestrator = OrchestratorAgent(
            simulation_agent=self.simulation_agent,
            impact_agent=self.impact_agent,
            mitigation_agent=self.mitigation_agent,
            graph_data=graph_data
        )
        
        logger.info("AgentRegistry initialized")
    
    
    def get_orchestrator(self) -> OrchestratorAgent:
        return self.orchestrator
    
    def get_simulation_agent(self) -> SimulationAgent:
        return self.simulation_agent
    
    def get_impact_agent(self) -> ImpactReasoningAgent:
        return self.impact_agent
    
    def get_mitigation_agent(self) -> MitigationAgent:
        return self.mitigation_agent


def create_registry(
    google_api_key: Optional[str] = None,
    graph_data: Optional[Dict] = None
) -> AgentRegistry:
    """Factory function to create an agent registry."""
    return AgentRegistry(google_api_key=google_api_key, graph_data=graph_data)
