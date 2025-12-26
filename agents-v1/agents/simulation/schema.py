"""
Pydantic schemas for SimulationAgent
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PropagationPath(BaseModel):
    """Single propagation path from source to affected nodes"""
    
    path: List[str] = Field(..., description="Ordered list of node IDs in the path")
    length: int = Field(..., description="Path length (number of edges)")
    affected_nodes: List[str] = Field(..., description="All nodes affected by this path")


class SimulationInput(BaseModel):
    """Input schema for SimulationAgent"""
    
    vendor_id: str = Field(..., description="Starting vendor/component ID")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum traversal depth")
    graph_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Graph structure: nodes, edges, attributes"
    )


class SimulationOutput(BaseModel):
    """Output schema for SimulationAgent"""
    
    source_vendor_id: str = Field(..., description="Starting vendor ID")
    propagation_paths: List[PropagationPath] = Field(
        default_factory=list,
        description="All enumerated propagation paths"
    )
    total_affected_nodes: int = Field(..., description="Total unique nodes affected")
    unique_affected_nodes: List[str] = Field(
        default_factory=list,
        description="List of all unique affected node IDs"
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Graph metrics: max_fan_out, avg_path_length, etc."
    )

