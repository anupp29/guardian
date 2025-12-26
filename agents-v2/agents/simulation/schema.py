"""
Pydantic schemas for SimulationAgent
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PropagationPath(BaseModel):
    """A single propagation path through the supply chain"""
    path: List[str] = Field(..., description="Ordered list of node IDs in the path")
    length: int = Field(..., description="Number of edges in the path")
    affected_nodes: List[str] = Field(..., description="All nodes affected by this path (excluding source)")


class SimulationInput(BaseModel):
    """Input schema for SimulationAgent"""
    vendor_id: str = Field(..., description="Starting vendor/component ID")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum traversal depth")
    graph_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional graph structure")


class SimulationOutput(BaseModel):
    """Output schema for SimulationAgent"""
    source_vendor_id: str = Field(..., description="Starting vendor ID")
    propagation_paths: List[PropagationPath] = Field(..., description="All enumerated propagation paths")
    total_affected_nodes: int = Field(..., description="Total number of unique affected nodes")
    unique_affected_nodes: List[str] = Field(..., description="List of unique affected node IDs")
    metrics: Dict[str, Any] = Field(..., description="Graph metrics and statistics")