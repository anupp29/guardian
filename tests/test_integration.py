"""
Integration tests for the full Guardian AI pipeline.

Tests end-to-end orchestration of all agents.
"""

import pytest
import os
from agents.registry import create_registry
from agents.orchestrator.schema import OrchestratorInput, GraphMetadata


def test_full_pipeline():
    """Test complete pipeline execution."""
    registry = create_registry()
    orchestrator = registry.get_orchestrator()
    
    input_data = OrchestratorInput(
        vendor_id="VENDOR_001",
        graph_metadata=GraphMetadata(
            node_count=16,
            edge_count=17,
            graph_type="directed"
        ),
        max_depth=4
    )
    
    output = orchestrator.run(input_data)
    
    # Verify all agents executed
    assert len(output.trace) == 3
    assert output.trace[0].agent_name == "SimulationAgent"
    assert output.trace[1].agent_name == "ImpactReasoningAgent"
    assert output.trace[2].agent_name == "MitigationAgent"
    
    # Verify outputs exist
    assert "simulation_results" in output.model_dump()
    assert "impact_analysis" in output.model_dump()
    assert "mitigations" in output.model_dump()


def test_pipeline_with_custom_graph():
    """Test pipeline with custom graph data."""
    custom_graph = {
        "X": ["Y", "Z"],
        "Y": ["W"],
        "Z": ["W"],
    }
    
    registry = create_registry(graph_data=custom_graph)
    orchestrator = registry.get_orchestrator()
    
    input_data = OrchestratorInput(
        vendor_id="X",
        graph_metadata=GraphMetadata(
            node_count=4,
            edge_count=4,
            graph_type="directed"
        ),
        max_depth=3
    )
    
    output = orchestrator.run(input_data)
    
    # Should have found paths from X
    assert len(output.simulation_results['propagation_paths']) > 0
    assert output.simulation_results['source_vendor_id'] == "X"


def test_pipeline_missing_vendor():
    """Test pipeline with non-existent vendor."""
    registry = create_registry()
    orchestrator = registry.get_orchestrator()
    
    input_data = OrchestratorInput(
        vendor_id="NONEXISTENT",
        graph_metadata=GraphMetadata(
            node_count=16,
            edge_count=17,
            graph_type="directed"
        ),
        max_depth=3
    )
    
    output = orchestrator.run(input_data)
    
    # Should handle gracefully
    assert output.simulation_results['source_vendor_id'] == "NONEXISTENT"
    assert len(output.simulation_results['affected_node_ids']) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
