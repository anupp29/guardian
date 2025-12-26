"""
Pydantic schemas for MitigationAgent
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MitigationAction(BaseModel):
    """Single mitigation action recommendation"""
    
    action_type: str = Field(..., description="Type: 'isolate_node', 'remove_edge', 'add_redundancy'")
    target: str = Field(..., description="Target node or edge ID")
    description: str = Field(..., description="Human-readable action description")
    risk_reduction: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Estimated risk reduction (0.0 to 1.0)"
    )
    affected_paths_reduced: int = Field(
        ...,
        description="Number of propagation paths that would be eliminated"
    )
    implementation_complexity: Optional[str] = Field(
        None,
        description="Complexity rating: 'low', 'medium', 'high'"
    )
    trade_offs: Optional[str] = Field(
        None,
        description="Trade-offs or side effects of this mitigation"
    )


class MitigationInput(BaseModel):
    """Input schema for MitigationAgent"""
    
    simulation_results: Dict[str, Any] = Field(
        ...,
        description="Output from SimulationAgent"
    )
    impact_explanations: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Output from ImpactReasoningAgent (optional)"
    )
    graph_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional graph metadata"
    )


class MitigationOutput(BaseModel):
    """Output schema for MitigationAgent"""
    
    ranked_mitigations: List[MitigationAction] = Field(
        default_factory=list,
        description="Mitigation actions ranked by risk reduction"
    )
    total_paths_original: int = Field(..., description="Original number of propagation paths")
    total_paths_reducible: int = Field(
        ...,
        description="Maximum paths that could be eliminated"
    )

