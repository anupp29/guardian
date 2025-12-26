"""Pydantic schemas for OrchestratorAgent."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class OrchestratorInput(BaseModel):
    """Input for OrchestratorAgent."""
    
    vendor_id: str = Field(..., description="Starting vendor ID")
    max_depth: int = Field(default=5, ge=1, le=10, description="Max propagation depth")


class TraceMetadata(BaseModel):
    """Execution trace for transparency."""
    
    agent_name: str
    execution_order: int
    input_summary: str
    output_summary: str


class OrchestratorOutput(BaseModel):
    """Unified output from OrchestratorAgent."""
    
    vendor_id: str
    simulation_results: Dict[str, Any]
    impact_analysis: Dict[str, Any]
    mitigations: Dict[str, Any]
    trace: List[TraceMetadata] = Field(default_factory=list)

