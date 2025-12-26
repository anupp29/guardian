"""Pydantic schemas for SimulationAgent."""

from typing import List, Dict
from pydantic import BaseModel, Field


class SimulationInput(BaseModel):
    """Input for SimulationAgent."""
    
    vendor_id: str = Field(..., description="Source vendor ID")
    graph_data: Dict[str, List[str]] = Field(..., description="Adjacency list graph")
    max_depth: int = Field(default=5, ge=1, le=10, description="Max depth")


class PropagationPath(BaseModel):
    """Single propagation path."""
    
    path: List[str] = Field(..., description="Node IDs in path")
    length: int = Field(..., description="Path length (edges)")


class GraphMetrics(BaseModel):
    """Graph metrics."""
    
    total_affected_nodes: int
    max_fan_out: int
    average_path_length: float


class SimulationOutput(BaseModel):
    """Output from SimulationAgent."""
    
    source_vendor_id: str
    propagation_paths: List[PropagationPath] = Field(default_factory=list)
    affected_node_ids: List[str] = Field(default_factory=list)
    metrics: GraphMetrics

