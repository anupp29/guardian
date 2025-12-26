"""
Pydantic schemas for ImpactReasoningAgent
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ImpactExplanation(BaseModel):
    """Single impact explanation for a propagation path"""
    
    path: List[str] = Field(..., description="The propagation path being explained")
    cause: str = Field(..., description="Root cause description")
    effect: str = Field(..., description="Cascading effect description")
    business_impact: Optional[str] = Field(
        None,
        description="Business or operational consequences"
    )
    uncertainty_notes: Optional[str] = Field(
        None,
        description="Explicit notes about data limitations or uncertainty"
    )


class ImpactReasoningInput(BaseModel):
    """Input schema for ImpactReasoningAgent"""
    
    simulation_results: Dict[str, Any] = Field(
        ...,
        description="Output from SimulationAgent"
    )
    graph_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional graph metadata for context"
    )


class ImpactReasoningOutput(BaseModel):
    """Output schema for ImpactReasoningAgent"""
    
    explanations: List[ImpactExplanation] = Field(
        default_factory=list,
        description="Human-readable impact explanations"
    )
    data_limitations: List[str] = Field(
        default_factory=list,
        description="Explicit list of data limitations"
    )
    summary: Optional[str] = Field(
        None,
        description="High-level summary of impacts"
    )

