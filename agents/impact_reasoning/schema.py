"""Pydantic schemas for ImpactReasoningAgent."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class NodeMetadata(BaseModel):
    """Node metadata."""
    
    node_id: str
    name: str
    type: str
    criticality: Optional[str] = None


class ImpactReasoningInput(BaseModel):
    """Input for ImpactReasoningAgent."""
    
    propagation_paths: List[List[str]]
    affected_nodes: List[str]
    node_metadata: Dict[str, NodeMetadata] = Field(default_factory=dict)


class ImpactExplanation(BaseModel):
    """Impact explanation with uncertainty."""
    
    path: List[str]
    cause: str
    effect: str
    uncertainty_notes: Optional[str] = None


class ImpactReasoningOutput(BaseModel):
    """Output from ImpactReasoningAgent."""
    
    explanations: List[ImpactExplanation] = Field(default_factory=list)
    summary: str
    data_limitations: List[str] = Field(default_factory=list)

