"""
Pydantic schemas for ImpactReasoningAgent
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ImpactExplanation(BaseModel):
    """Explanation of impact for a single propagation path"""
    path: List[str] = Field(..., description="The propagation path being explained")
    cause: str = Field(..., description="Root cause description")
    effect: str = Field(..., description="Cascading effect description")
    business_impact: Optional[str] = Field(default=None, description="Business/operational impact")
    uncertainty_notes: str = Field(..., description="Data limitations and uncertainty")


class ImpactReasoningInput(BaseModel):
    """Input schema for ImpactReasoningAgent"""
    simulation_results: Dict[str, Any] = Field(..., description="Output from SimulationAgent")
    graph_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional graph metadata for context")


class ImpactReasoningOutput(BaseModel):
    """Output schema for ImpactReasoningAgent"""
    explanations: List[Dict[str, Any]] = Field(..., description="Impact explanations for significant paths")
    data_limitations: List[str] = Field(..., description="List of data limitations affecting analysis")
    summary: str = Field(..., description="High-level summary of impact analysis")