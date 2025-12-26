"""
ImpactReasoningAgent - LLM-powered impact explanation.

This agent uses Google's Gemini API to convert simulation results into
human-readable impact explanations with strict grounding in provided data.
"""

import logging
import os
from typing import Dict, List
import json

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from .schema import (
    ImpactReasoningInput,
    ImpactReasoningOutput,
    ImpactExplanation,
    NodeMetadata
)

logger = logging.getLogger(__name__)


class ImpactReasoningAgent:
    """
    Explains business and operational impact of supply chain cascades.
    
    Uses Gemini LLM to generate explanations strictly grounded in simulation data.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the ImpactReasoningAgent.
        
        Args:
            api_key: Google API key for Gemini. If None, uses GOOGLE_API_KEY env var.
        """
        self.agent_name = "ImpactReasoningAgent"
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if genai is None:
            logger.warning("google-genai not installed. Agent will use fallback mode.")
            self.client = None
        elif not self.api_key:
            logger.warning("No API key provided. Agent will use fallback mode.")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"{self.agent_name} initialized with Gemini")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt from prompt.md."""
        try:
            import os
            prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load prompt.md: {e}")
            return "You are an impact reasoning agent. Explain supply chain impacts based on provided data only."
    
    def run(self, input_data: ImpactReasoningInput) -> ImpactReasoningOutput:
        """
        Execute impact reasoning.
        
        Args:
            input_data: ImpactReasoningInput with paths and node metadata
            
        Returns:
            ImpactReasoningOutput with explanations and uncertainty notes
        """
        logger.info(f"{self.agent_name} starting execution")
        logger.info(f"  Analyzing {len(input_data.propagation_paths)} paths")
        logger.info(f"  Affected nodes: {len(input_data.affected_nodes)}")
        
        if self.client:
            # Use LLM for reasoning
            output = self._reason_with_llm(input_data)
        else:
            # Fallback to rule-based reasoning
            output = self._reason_fallback(input_data)
        
        logger.info(f"{self.agent_name} completed execution")
        logger.info(f"  Generated {len(output.explanations)} explanations")
        
        return output
    
    def _reason_with_llm(self, input_data: ImpactReasoningInput) -> ImpactReasoningOutput:
        """Use Gemini LLM for impact reasoning."""
        # Prepare structured input for the LLM
        context = self._prepare_context(input_data)
        
        # Create prompt
        user_prompt = f"""
Analyze the following supply chain propagation data and provide structured impact explanations.

{context}

Provide your response as a JSON object with the following structure:
{{
  "explanations": [
    {{
      "path": ["node1", "node2", ...],
      "cause": "description of trigger",
      "effect": "description of downstream impact",
      "uncertainty_notes": "explicit statement of missing data or assumptions"
    }}
  ],
  "summary": "high-level summary of overall impact",
  "data_limitations": ["limitation 1", "limitation 2", ...]
}}
"""
        
        try:
            # Call Gemini API
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON response
            result = json.loads(response.text)
            
            # Convert to schema
            explanations = [
                ImpactExplanation(**exp) for exp in result.get("explanations", [])
            ]
            
            return ImpactReasoningOutput(
                explanations=explanations,
                summary=result.get("summary", "Impact analysis completed"),
                data_limitations=result.get("data_limitations", [])
            )
            
        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}")
            return self._reason_fallback(input_data)
    
    def _reason_fallback(self, input_data: ImpactReasoningInput) -> ImpactReasoningOutput:
        """Fallback rule-based reasoning when LLM is unavailable."""
        explanations = []
        
        # Generate simple explanations for top paths
        for path in input_data.propagation_paths[:10]:  # Limit to top 10
            cause = f"Disruption at {path[0]}"
            
            if len(path) == 2:
                effect = f"Directly affects {path[1]}"
            else:
                intermediates = ", ".join(path[1:-1])
                effect = f"Cascades through {intermediates} to {path[-1]}"
            
            explanations.append(ImpactExplanation(
                path=path,
                cause=cause,
                effect=effect,
                uncertainty_notes="Detailed impact analysis requires domain-specific data (inventory, lead times, criticality)"
            ))
        
        summary = f"Disruption propagates through {len(input_data.propagation_paths)} paths affecting {len(input_data.affected_nodes)} vendors"
        
        return ImpactReasoningOutput(
            explanations=explanations,
            summary=summary,
            data_limitations=[
                "Node metadata incomplete or missing",
                "Inventory levels not provided",
                "Lead times unknown",
                "Business criticality not quantified"
            ]
        )
    
    
    def _prepare_context(self, input_data: ImpactReasoningInput) -> str:
        """Prepare compact context for LLM."""
        parts = []
        
        # Add node metadata if available
        if input_data.node_metadata:
            parts.append("## Nodes:")
            for nid, meta in input_data.node_metadata.items():
                parts.append(f"- {nid}: {meta.name} ({meta.type})")
        
        # Add paths (limit to top 20)
        parts.append(f"\n## Paths ({len(input_data.propagation_paths)}):") 
        for i, path in enumerate(input_data.propagation_paths[:20], 1):
            parts.append(f"{i}. {' → '.join(path)}")
        
        if len(input_data.propagation_paths) > 20:
            parts.append(f"... +{len(input_data.propagation_paths) - 20} more")
        
        # Summary
        parts.append(f"\n## Summary: {len(input_data.affected_nodes)} affected, {len(input_data.propagation_paths)} paths")
        
        return "\n".join(parts)
