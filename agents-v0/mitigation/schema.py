"""Pydantic schemas for MitigationAgent."""

from typing import List, Dict
from pydantic import BaseModel, Field


class MitigationInput(BaseModel):
    """Input for MitigationAgent."""
    
    graph_data: Dict[str, List[str]]
    source_vendor_id: str
    affected_nodes: List[str]
    propagation_paths: List[List[str]]


class MitigationAction(BaseModel):
    """Mitigation action with effectiveness metrics."""
    
    action_type: str = Field(..., description="e.g., 'isolate_node', 'add_redundancy'")
    target: str
    description: str
    risk_reduction: float = Field(..., ge=0, le=1)
    affected_paths_reduced: int


class MitigationOutput(BaseModel):
    """Output from MitigationAgent."""
    
    ranked_mitigations: List[MitigationAction] = Field(default_factory=list)
    total_paths_before: int
    methodology: str

