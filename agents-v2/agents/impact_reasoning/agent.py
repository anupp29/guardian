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


class RateLimiter:
    """Thread-safe rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 2, time_window: float = 1.0):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            if len(self.calls) >= self.max_calls:
                oldest_call = self.calls[0]
                wait_time = self.time_window - (now - oldest_call) + 0.1
                if wait_time > 0:
                    time.sleep(wait_time)
                    now = time.time()
                    self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            self.calls.append(time.time())


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
    
    if model:
        try:
            sanitized_path = [str(node) for node in path[:5] if node]
            path_str = '→'.join(sanitized_path)
            
            prompt = f"P:{path_str}|JSON:{{'cause':'X','effect':'Y','business_impact':'Z','uncertainty_notes':'W'}}"
            
            _rate_limiter.wait_if_needed()
            
            response = model.generate_content(prompt)
            text = response.text.strip() if hasattr(response, 'text') else str(response)
            
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
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
    """
    try:
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
        
        explanations = []
        
        if not isinstance(paths, list):
            logger.warning(f"paths is not a list, got {type(paths)}")
            paths = []
        
        max_paths_to_explain = min(5, len(paths))
        significant_paths = sorted(
            paths,
            key=lambda p: (p.get('length', 0) if isinstance(p, dict) else 0, 
                          len(p.get('affected_nodes', [])) if isinstance(p, dict) else 0),
            reverse=True
        )[:max_paths_to_explain]
        
        for path_data in significant_paths:
            path = path_data.get('path', [])
            if isinstance(path, list) and len(path) > 1:
                explanation = generate_impact_explanation(path, model=model)
                explanations.append(explanation)
        
        summary = f"Analysis of {len(paths)} propagation paths affecting {len(affected_nodes)} nodes. " \
                 f"Key impacts include cascading failures through dependency chains."
        
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


class ImpactReasoningAgent:
    """
    ImpactReasoningAgent using Google ADK LlmAgent.
    Explains business and operational implications using Gemini.
    """
    
    def __init__(self, api_key: str = None):
        self.name = "ImpactReasoningAgent"
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model = None
        
        # Create ADK LlmAgent
        self.agent = LlmAgent(
            name="ImpactReasoningAgent",
            model="gemini-2.0-flash-exp",
            instruction=self._load_prompt(),
            description="Explains business and operational implications of simulated supply-chain failure propagation using LLM reasoning",
            tools=[impact_analysis_tool]
        )
        
        # Initialize Gemini model for direct use if needed
        if self.api_key:
            try:
                api_key_length = len(self.api_key)
                if api_key_length < 10:
                    logger.warning(f"[{self.name}] API key appears invalid (length: {api_key_length})")
                    return
                
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
                error_msg = str(e)
                if self.api_key and len(self.api_key) > 8:
                    error_msg = error_msg.replace(self.api_key, "***REDACTED***")
                    for i in range(len(self.api_key) - 4):
                        partial = self.api_key[i:i+8]
                        if partial in error_msg:
                            error_msg = error_msg.replace(partial, "***")
                logger.warning(f"[{self.name}] Failed to initialize Gemini: {error_msg}")
    
    def _load_prompt(self) -> str:
        """Load system prompt from prompt.md"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return """You are the ImpactReasoningAgent for Guardian AI. Translate technical simulation results into human-readable explanations of business impact using contextual reasoning."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate impact explanations for simulation results.
        """
        try:
            reasoning_input = ImpactReasoningInput(**input_data)
            logger.info(f"[{self.name}] Generating impact explanations")
            
            result = analyze_impact_explanations(
                simulation_results=reasoning_input.simulation_results,
                graph_metadata=reasoning_input.graph_metadata or {},
                model=self.model
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Impact reasoning failed: {str(e)}", exc_info=True)
            raise


# Create global instance for registry
impact_reasoning_agent = ImpactReasoningAgent()