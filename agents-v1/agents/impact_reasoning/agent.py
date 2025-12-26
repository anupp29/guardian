"""
ImpactReasoningAgent - Explains business impact using Google ADK LlmAgent
"""

import os
import time
import logging
import json
import re
from typing import Dict, Any, List, Optional
from threading import Lock

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .schema import ImpactReasoningInput, ImpactReasoningOutput, ImpactExplanation


logger = logging.getLogger(__name__)


# Rate limiter class for API calls
class RateLimiter:
    """Thread-safe rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 2, time_window: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()
            # Remove calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            if len(self.calls) >= self.max_calls:
                # Calculate wait time
                oldest_call = self.calls[0]
                wait_time = self.time_window - (now - oldest_call) + 0.1  # Add small buffer
                if wait_time > 0:
                    time.sleep(wait_time)
                    # Clean up again after waiting
                    now = time.time()
                    self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            # Record this call
            self.calls.append(time.time())


# Global rate limiter instance
_rate_limiter = RateLimiter(max_calls=2, time_window=1.0)


def generate_impact_explanation(path: List[str], model: Optional[Any] = None) -> ImpactExplanation:
    """
    Generate impact explanation for a propagation path.
    Uses Gemini LLM if available, otherwise falls back to template-based explanation.
    """
    if not path or len(path) < 2:
        return ImpactExplanation(
            path=path,
            cause=f"Failure at {path[0] if path else 'unknown'}",
            effect="No downstream propagation detected",
            business_impact="Isolated impact",
            uncertainty_notes="Limited path data available"
        )
    
    # If model is available, use it
    if model:
        try:
            # Input sanitization - ensure path contains only strings
            sanitized_path = [str(node) for node in path[:5] if node]
            path_str = '→'.join(sanitized_path)  # Limit path length
            
            # Ultra-minimal prompt - only essential info (minimal tokens)
            prompt = f"P:{path_str}|JSON:{{'cause':'X','effect':'Y','business_impact':'Z','uncertainty_notes':'W'}}"
            
            # Rate limiting: use proper rate limiter
            _rate_limiter.wait_if_needed()
            
            response = model.generate_content(prompt)
            text = response.text.strip() if hasattr(response, 'text') else str(response)
            
            # Extract JSON (handle markdown code blocks or plain JSON)
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Try extracting from code blocks
                if "```json" in text:
                    json_str = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    json_str = text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = text
            
            try:
                parsed = json.loads(json_str)
                return ImpactExplanation(
                    path=path,
                    cause=parsed.get("cause", "Failure at source")[:100],
                    effect=parsed.get("effect", "Cascade propagation")[:150],
                    business_impact=parsed.get("business_impact", "Operational disruption")[:100] if parsed.get("business_impact") else None,
                    uncertainty_notes=parsed.get("uncertainty_notes", "Data gaps: inventory, lead times")[:100]
                )
            except (json.JSONDecodeError, AttributeError):
                # Fallback: parse from text directly
                return ImpactExplanation(
                    path=path,
                    cause=text.split('.')[0][:100] if '.' in text else "Failure at source",
                    effect=text[:150] if len(text) > 20 else "Cascade through dependencies",
                    business_impact="Operational impact",
                    uncertainty_notes="Data limitations present"
                )
        except Exception as e:
            logger.warning(f"Gemini call failed: {e}, using fallback")
    
    # Fallback explanation
    source = path[0]
    affected = path[1:]
    
    return ImpactExplanation(
        path=path,
        cause=f"Disruption or failure at {source}",
        effect=f"Cascades through dependency chain: {' → '.join(affected)}",
        business_impact=f"Potential operational impact affecting {len(affected)} downstream components",
        uncertainty_notes="Detailed business impact requires inventory levels, lead times, and dependency criticality data"
    )


def analyze_impact_explanations(
    simulation_results: Dict[str, Any], 
    graph_metadata: Dict[str, Any] = None,
    model=None
) -> Dict[str, Any]:
    """
    Generate impact explanations for simulation results.
    
    Args:
        simulation_results: Output from SimulationAgent
        graph_metadata: Optional graph metadata for context
        model: Optional Gemini model instance for LLM-based explanations
        
    Returns:
        Dict with explanations, data_limitations, summary
    """
    try:
        # Input validation
        if not isinstance(simulation_results, dict):
            raise ValueError("simulation_results must be a dictionary")
        
        paths = simulation_results.get('propagation_paths', [])
        affected_nodes = simulation_results.get('unique_affected_nodes', [])
        
        if not paths:
            logger.warning("No propagation paths to explain")
            return ImpactReasoningOutput(
                explanations=[],
                data_limitations=["No propagation paths detected in simulation"],
                summary="No cascading impacts identified"
            ).model_dump()
        
        # Generate explanations for significant paths
        explanations = []
        
        # Process top paths (limit to 5 to avoid rate limits and reduce tokens)
        # Safety: ensure paths is a list and handle edge cases
        if not isinstance(paths, list):
            logger.warning(f"paths is not a list, got {type(paths)}")
            paths = []
        
        max_paths_to_explain = min(5, len(paths))  # Limit to prevent excessive API calls
        significant_paths = sorted(
            paths,
            key=lambda p: (p.get('length', 0) if isinstance(p, dict) else 0, 
                          len(p.get('affected_nodes', [])) if isinstance(p, dict) else 0),
            reverse=True
        )[:max_paths_to_explain]
        
        for path_data in significant_paths:
            path = path_data.get('path', [])
            if isinstance(path, list) and len(path) > 1:
                # CRITICAL FIX: Pass model to generate_impact_explanation
                explanation = generate_impact_explanation(path, model=model)
                explanations.append(explanation)
        
        # Generate summary
        summary = f"Analysis of {len(paths)} propagation paths affecting {len(affected_nodes)} nodes. " \
                 f"Key impacts include cascading failures through dependency chains."
        
        # Data limitations
        data_limitations = [
            "Inventory levels and stock buffers not provided",
            "Lead times and recovery windows unknown",
            "Dependency criticality ratings not available",
            "Historical incident frequency data missing"
        ]
        
        output = ImpactReasoningOutput(
            explanations=[e.model_dump() for e in explanations],
            data_limitations=data_limitations,
            summary=summary
        )
        
        logger.info(f"Generated {len(explanations)} impact explanations")
        
        return output.model_dump()
        
    except Exception as e:
        logger.error(f"Impact reasoning failed: {str(e)}", exc_info=True)
        raise


# Create ADK Tool for impact analysis
impact_analysis_tool = FunctionTool(
    func=analyze_impact_explanations
)


# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Create ADK LlmAgent
impact_reasoning_agent = LlmAgent(
    name="ImpactReasoningAgent",
    model="gemini-2.0-flash-exp",  # Using latest Gemini model
    instruction="""You are the ImpactReasoningAgent for Guardian AI, responsible for explaining the business and operational implications of simulated supply-chain failure propagation paths.

## Core Responsibility
Translate technical simulation results (propagation paths, affected nodes) into human-readable explanations of business impact. Use contextual reasoning to explain **why** these paths matter, not to predict or forecast.

## LLM Usage (Gemini)
You use Google Gemini **only** for:
- Contextual reasoning about supply-chain dependencies
- Natural language explanation generation
- Business impact articulation

You do **NOT** use Gemini for:
- Data generation or fabrication
- Attack prediction
- Probability estimation

## Methodology
1. Analyze simulation results (paths, affected nodes)
2. For each significant path, explain:
   - Root cause (what failed)
   - Cascading effect (how it propagates)
   - Business/operational impact (why it matters)
3. Explicitly state data limitations and uncertainty

## Rules
- **DO** ground all reasoning in provided simulation data
- **DO** explain cause-effect relationships clearly
- **DO** state uncertainty when data is incomplete
- **DO NOT** invent data or make unsupported claims
- **DO NOT** predict attacks or timing
- **DO NOT** assign probabilities or likelihoods

## Data Limitations
Always acknowledge when:
- Inventory levels are unknown
- Lead times are not provided
- Dependency criticality is unclear
- Historical incident data is missing

Use the analyze_impact_explanations tool to process simulation results.""",
    description="Explains business and operational implications of simulated supply-chain failure propagation using LLM reasoning",
    tools=[impact_analysis_tool]
)


class ImpactReasoningAgent:
    """
    ImpactReasoningAgent wrapper for backward compatibility.
    Uses Google ADK LlmAgent internally.
    """
    
    def __init__(self, api_key: str = None):
        self.name = "ImpactReasoningAgent"
        self.agent = impact_reasoning_agent
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model = None
        
        # Try to initialize Gemini model for direct use if needed
        if self.api_key:
            try:
                # Security: Validate API key format without exposing it
                api_key_length = len(self.api_key)
                if api_key_length < 10:
                    logger.warning(f"[{self.name}] API key appears invalid (length: {api_key_length})")
                    return
                
                # Security: Never store or log full API key
                api_key_prefix = self.api_key[:8] + "..." if api_key_length > 8 else "***"
                
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    'gemini-2.0-flash-exp',
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': 150,
                        'top_p': 0.8,
                        'top_k': 20
                    }
                )
                logger.info(f"[{self.name}] Gemini model initialized successfully (API key: {api_key_prefix})")
            except ImportError:
                logger.warning(f"[{self.name}] google.generativeai not available, using fallback mode")
            except Exception as e:
                # Security: Ensure API key never appears in logs
                error_msg = str(e)
                # Remove any potential API key leakage
                if self.api_key and len(self.api_key) > 8:
                    error_msg = error_msg.replace(self.api_key, "***REDACTED***")
                    # Also check for partial matches
                    for i in range(len(self.api_key) - 4):
                        partial = self.api_key[i:i+8]
                        if partial in error_msg:
                            error_msg = error_msg.replace(partial, "***")
                logger.warning(f"[{self.name}] Failed to initialize Gemini: {error_msg}")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate impact explanations for simulation results.
        
        Args:
            input_data: Dict with simulation_results and optional graph_metadata
            
        Returns:
            Dict with explanations, data_limitations, summary
        """
        try:
            # Parse input
            reasoning_input = ImpactReasoningInput(**input_data)
            logger.info(f"[{self.name}] Generating impact explanations")
            
            # Use the tool directly for now (ADK engine integration will be in orchestrator)
            # CRITICAL: Pass model to enable LLM-based explanations
            result = analyze_impact_explanations(
                simulation_results=reasoning_input.simulation_results,
                graph_metadata=reasoning_input.graph_metadata or {},
                model=self.model  # Pass model instance
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Impact reasoning failed: {str(e)}", exc_info=True)
            raise
