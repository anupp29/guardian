"""
Pydantic schemas for MitigationAgent
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MitigationAction(BaseModel):
    """A single mitigation action with effectiveness metrics"""
    action_type: str = Field(..., description="Type of mitigation (isolate_node, remove_edge, add_redundancy)")
    target: str = Field(..., description="Target node/edge for the mitigation")
    description: str = Field(..., description="Human-readable description of the action")
    risk_reduction: float = Field(..., ge=0.0, le=1.0, description="Risk reduction ratio (0.0 to 1.0)")
    affected_paths_reduced: int = Field(..., ge=0, description="Number of propagation paths eliminated")
    implementation_complexity: str = Field(..., description="Estimated complexity (low, medium, high)")
    trade_offs: str = Field(..., description="Potential trade-offs or side effects")


class MitigationInput(BaseModel):
    """Input schema for MitigationAgent"""
    simulation_results: Dict[str, Any] = Field(..., description="Output from SimulationAgent")
    impact_explanations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Output from ImpactReasoningAgent")
    graph_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional graph metadata")


class MitigationOutput(BaseModel):
    """Output schema for MitigationAgent"""
    ranked_mitigations: List[Dict[str, Any]] = Field(..., description="Mitigation actions ranked by effectiveness")
    total_paths_original: int = Field(..., description="Total number of original propagation paths")
    total_paths_reducible: int = Field(..., description="Total number of paths that can be reduced by all mitigations")