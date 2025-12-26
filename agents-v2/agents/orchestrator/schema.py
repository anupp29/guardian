"""
Pydantic schemas for OrchestratorAgent
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ExecutionTrace(BaseModel):
    """Execution trace for a single agent"""
    agent_name: str = Field(..., description="Name of the executed agent")
    input_summary: str = Field(..., description="Summary of agent input")
    output_summary: str = Field(..., description="Summary of agent output")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")


class OrchestratorInput(BaseModel):
    """Input schema for OrchestratorAgent"""
    vendor_id: str = Field(..., description="Starting vendor/component ID for simulation")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum traversal depth")
    graph_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional graph structure")


class OrchestratorOutput(BaseModel):
    """Output schema for OrchestratorAgent"""
    success: bool = Field(..., description="Whether pipeline executed successfully")
    execution_trace: List[ExecutionTrace] = Field(default_factory=list, description="Execution trace for all agents")
    simulation_results: Optional[Dict[str, Any]] = Field(default=None, description="Results from SimulationAgent")
    impact_explanations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Results from ImpactReasoningAgent")
    mitigation_recommendations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Results from MitigationAgent")
    error_message: Optional[str] = Field(default=None, description="Error message if pipeline failed")