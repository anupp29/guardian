"""
OrchestratorAgent - Coordinates pipeline execution using Google ADK multi-agent system
"""

import os
import time
import logging
from typing import Dict, Any, Optional

from google.adk.agents import LlmAgent

# Engine is optional - may not be available in all google-adk versions
try:
    from google.adk.core import Engine
    ENGINE_AVAILABLE = True
except ImportError:
    ENGINE_AVAILABLE = False
    Engine = None  # type: ignore

from .schema import OrchestratorInput, OrchestratorOutput, ExecutionTrace


logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    OrchestratorAgent using Google ADK multi-agent system.
    Coordinates SimulationAgent, ImpactReasoningAgent, and MitigationAgent.
    """
    
    def __init__(self):
        self.name = "OrchestratorAgent"
        self.engine = None
        
        # Create ADK multi-agent orchestrator
        self.agent = LlmAgent(
            name="OrchestratorAgent",
            model="gemini-2.0-flash-exp",
            instruction=self._load_prompt(),
            description="Coordinates execution of specialized agents in a deterministic pipeline for supply chain risk simulation"
        )
    
    def _load_prompt(self) -> str:
        """Load system prompt from prompt.md"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return """You are the OrchestratorAgent for Guardian AI. Coordinate specialized agents in a deterministic pipeline:
            SimulationAgent → ImpactReasoningAgent → MitigationAgent. Validate inputs, preserve outputs, log execution trace."""
    
    def _initialize_engine(self):
        """Initialize ADK Engine if needed and available"""
        if self.engine is None and ENGINE_AVAILABLE and Engine is not None:
            try:
                self.engine = Engine()
            except Exception as e:
                logger.warning(f"Failed to initialize ADK Engine: {e}")
                self.engine = None
    
    def run(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        """
        Execute the full pipeline: Simulation → Impact → Mitigation
        
        Args:
            input_data: OrchestratorInput with vendor_id, max_depth, etc.
            
        Returns:
            OrchestratorOutput with aggregated results and execution trace
        """
        execution_trace = []
        simulation_results = None
        impact_explanations = None
        mitigation_recommendations = None
        error_message = None
        
        try:
            # Input validation
            if not isinstance(input_data, OrchestratorInput):
                raise TypeError("input_data must be an OrchestratorInput instance")
            if not input_data.vendor_id or not isinstance(input_data.vendor_id, str):
                raise ValueError("vendor_id must be a non-empty string")
            if not isinstance(input_data.max_depth, int) or input_data.max_depth < 1:
                raise ValueError("max_depth must be a positive integer")
            
            logger.info(f"[{self.name}] Starting pipeline for vendor_id={input_data.vendor_id}, max_depth={input_data.max_depth}")
            
            # Initialize engine
            self._initialize_engine()
            
            # Step 1: SimulationAgent
            try:
                from ..simulation.agent import SimulationAgent
                sim_agent = SimulationAgent()
                
                sim_input = {
                    "vendor_id": input_data.vendor_id,
                    "max_depth": input_data.max_depth,
                    "graph_metadata": input_data.graph_metadata
                }
                
                start_time = time.time()
                sim_result = sim_agent.run(sim_input)
                exec_time = (time.time() - start_time) * 1000
                
                execution_trace.append(ExecutionTrace(
                    agent_name="SimulationAgent",
                    input_summary=f"vendor_id={input_data.vendor_id}, max_depth={input_data.max_depth}",
                    output_summary=f"Found {len(sim_result.get('propagation_paths', []))} paths affecting {sim_result.get('total_affected_nodes', 0)} nodes",
                    execution_time_ms=exec_time
                ))
                
                simulation_results = sim_result
                logger.info(f"[{self.name}] SimulationAgent completed successfully")
                
            except Exception as e:
                error_message = f"SimulationAgent failed: {str(e)}"
                logger.error(f"[{self.name}] {error_message}")
                return OrchestratorOutput(
                    success=False,
                    execution_trace=execution_trace,
                    error_message=error_message
                )
            
            # Step 2: ImpactReasoningAgent
            try:
                from ..impact_reasoning.agent import ImpactReasoningAgent
                impact_agent = ImpactReasoningAgent()
                
                impact_input = {
                    "simulation_results": simulation_results,
                    "graph_metadata": input_data.graph_metadata
                }
                
                start_time = time.time()
                impact_result = impact_agent.run(impact_input)
                exec_time = (time.time() - start_time) * 1000
                
                execution_trace.append(ExecutionTrace(
                    agent_name="ImpactReasoningAgent",
                    input_summary=f"{len(simulation_results.get('propagation_paths', []))} paths, {simulation_results.get('total_affected_nodes', 0)} nodes",
                    output_summary=f"Generated {len(impact_result.get('explanations', []))} impact explanations",
                    execution_time_ms=exec_time
                ))
                
                impact_explanations = impact_result.get('explanations', [])
                logger.info(f"[{self.name}] ImpactReasoningAgent completed successfully")
                
            except Exception as e:
                error_message = f"ImpactReasoningAgent failed: {str(e)}"
                logger.error(f"[{self.name}] {error_message}")
                return OrchestratorOutput(
                    success=False,
                    execution_trace=execution_trace,
                    simulation_results=simulation_results,
                    error_message=error_message
                )
            
            # Step 3: MitigationAgent
            try:
                from ..mitigation.agent import MitigationAgent
                mit_agent = MitigationAgent()
                
                mit_input = {
                    "simulation_results": simulation_results,
                    "impact_explanations": impact_explanations,
                    "graph_metadata": input_data.graph_metadata
                }
                
                start_time = time.time()
                mit_result = mit_agent.run(mit_input)
                exec_time = (time.time() - start_time) * 1000
                
                execution_trace.append(ExecutionTrace(
                    agent_name="MitigationAgent",
                    input_summary=f"{simulation_results.get('total_affected_nodes', 0)} affected nodes",
                    output_summary=f"Ranked {len(mit_result.get('ranked_mitigations', []))} mitigation actions",
                    execution_time_ms=exec_time
                ))
                
                mitigation_recommendations = mit_result.get('ranked_mitigations', [])
                logger.info(f"[{self.name}] MitigationAgent completed successfully")
                
            except Exception as e:
                error_message = f"MitigationAgent failed: {str(e)}"
                logger.error(f"[{self.name}] {error_message}")
                return OrchestratorOutput(
                    success=False,
                    execution_trace=execution_trace,
                    simulation_results=simulation_results,
                    impact_explanations=impact_explanations,
                    error_message=error_message
                )
            
            logger.info(f"[{self.name}] Pipeline completed successfully")
            return OrchestratorOutput(
                success=True,
                execution_trace=execution_trace,
                simulation_results=simulation_results,
                impact_explanations=impact_explanations,
                mitigation_recommendations=mitigation_recommendations
            )
            
        except Exception as e:
            error_message = f"OrchestratorAgent failed: {str(e)}"
            logger.error(f"[{self.name}] {error_message}", exc_info=True)
            return OrchestratorOutput(
                success=False,
                execution_trace=execution_trace,
                error_message=error_message
            )


# Create global instance for registry
orchestrator_agent = OrchestratorAgent()