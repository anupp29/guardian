"""
OrchestratorAgent - Pipeline coordinator for Guardian AI.
Pure coordination - no reasoning, no data transformation.
"""

import logging
from typing import Dict, Any

from .schema import OrchestratorInput, OrchestratorOutput, TraceMetadata
from ..simulation.agent import SimulationAgent
from ..simulation.schema import SimulationInput
from ..impact_reasoning.agent import ImpactReasoningAgent
from ..impact_reasoning.schema import ImpactReasoningInput
from ..mitigation.agent import MitigationAgent
from ..mitigation.schema import MitigationInput

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Coordinates Guardian AI agent pipeline in deterministic sequence."""
    
    def __init__(
        self,
        simulation_agent: SimulationAgent = None,
        impact_agent: ImpactReasoningAgent = None,
        mitigation_agent: MitigationAgent = None,
        graph_data: Dict[str, list] = None
    ):
        self.agent_name = "OrchestratorAgent"
        self.simulation_agent = simulation_agent or SimulationAgent()
        self.impact_agent = impact_agent or ImpactReasoningAgent()
        self.mitigation_agent = mitigation_agent or MitigationAgent()
        self.graph_data = graph_data or self._create_sample_graph()
        
        logger.info(f"{self.agent_name} initialized with {len(self.graph_data)} nodes")
    
    
    def run(self, input_data: OrchestratorInput) -> OrchestratorOutput:
        """Execute the full Guardian AI pipeline."""
        logger.info(f"Pipeline: vendor={input_data.vendor_id}, depth={input_data.max_depth}")
        
        trace = []
        
        # Step 1: SimulationAgent
        simulation_input = SimulationInput(
            vendor_id=input_data.vendor_id,
            graph_data=self.graph_data,
            max_depth=input_data.max_depth
        )
        simulation_output = self.simulation_agent.run(simulation_input)
        
        trace.append(TraceMetadata(
            agent_name="SimulationAgent",
            execution_order=1,
            input_summary=f"vendor_id={input_data.vendor_id}, max_depth={input_data.max_depth}",
            output_summary=f"Found {len(simulation_output.propagation_paths)} paths affecting {len(simulation_output.affected_node_ids)} nodes"
        ))
        
        
        # Step 2: ImpactReasoningAgent
        impact_input = ImpactReasoningInput(
            propagation_paths=[p.path for p in simulation_output.propagation_paths],
            affected_nodes=simulation_output.affected_node_ids,
            node_metadata={}
        )
        impact_output = self.impact_agent.run(impact_input)
        
        trace.append(TraceMetadata(
            agent_name="ImpactReasoningAgent",
            execution_order=2,
            input_summary=f"{len(impact_input.propagation_paths)} paths, {len(impact_input.affected_nodes)} nodes",
            output_summary=f"Generated {len(impact_output.explanations)} impact explanations"
        ))
        
        
        # Step 3: MitigationAgent
        mitigation_input = MitigationInput(
            graph_data=self.graph_data,
            source_vendor_id=input_data.vendor_id,
            affected_nodes=simulation_output.affected_node_ids,
            propagation_paths=[p.path for p in simulation_output.propagation_paths]
        )
        mitigation_output = self.mitigation_agent.run(mitigation_input)
        
        trace.append(TraceMetadata(
            agent_name="MitigationAgent",
            execution_order=3,
            input_summary=f"{len(mitigation_input.affected_nodes)} affected nodes",
            output_summary=f"Ranked {len(mitigation_output.ranked_mitigations)} mitigation actions"
        ))
        
        # Aggregate outputs
        logger.info("Pipeline complete")
        return OrchestratorOutput(
            vendor_id=input_data.vendor_id,
            simulation_results=simulation_output.model_dump(),
            impact_analysis=impact_output.model_dump(),
            mitigations=mitigation_output.model_dump(),
            trace=trace
        )
    
    def _create_sample_graph(self) -> Dict[str, list]:
        """
        Create a sample supply chain dependency graph.
        
        This is a synthetic graph for demonstration. In production,
        this would be loaded from a real data source.
        """
        return {
            "VENDOR_001": ["VENDOR_002", "VENDOR_003", "VENDOR_004"],
            "VENDOR_002": ["VENDOR_005", "VENDOR_006"],
            "VENDOR_003": ["VENDOR_006", "VENDOR_007"],
            "VENDOR_004": ["VENDOR_008"],
            "VENDOR_005": ["VENDOR_009", "VENDOR_010"],
            "VENDOR_006": ["VENDOR_010", "VENDOR_011"],
            "VENDOR_007": ["VENDOR_011", "VENDOR_012"],
            "VENDOR_008": ["VENDOR_013"],
            "VENDOR_009": ["VENDOR_014"],
            "VENDOR_010": ["VENDOR_014", "VENDOR_015"],
            "VENDOR_011": ["VENDOR_015"],
            "VENDOR_012": ["VENDOR_016"],
            "VENDOR_013": ["VENDOR_017"],
            "VENDOR_014": ["VENDOR_017"],
            "VENDOR_015": ["VENDOR_018"],
            "VENDOR_016": ["VENDOR_018"],
        }
