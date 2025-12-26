"""
Pydantic schemas for OrchestratorAgent
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class OrchestratorInput(BaseModel):
    """Input schema for OrchestratorAgent"""
    
    vendor_id: str = Field(..., description="Starting vendor ID for simulation")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum propagation depth")
    graph_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional graph metadata (nodes, edges, attributes)"
    )


class ExecutionTrace(BaseModel):
    """Single agent execution trace entry"""
    
    agent_name: str = Field(..., description="Name of the agent")
    input_summary: str = Field(..., description="Brief summary of inputs")
    output_summary: str = Field(..., description="Brief summary of outputs")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")


class OrchestratorOutput(BaseModel):
    """Output schema for OrchestratorAgent"""
    
    success: bool = Field(..., description="Whether pipeline executed successfully")
    execution_trace: List[ExecutionTrace] = Field(
        default_factory=list,
        description="Ordered trace of agent executions"
    )
    simulation_results: Optional[Dict[str, Any]] = Field(
        None,
        description="Results from SimulationAgent"
    )
    impact_explanations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Results from ImpactReasoningAgent"
    )
    mitigation_recommendations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Results from MitigationAgent"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if pipeline failed"
    )

