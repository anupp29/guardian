"""
Unit tests for SimulationAgent.

Tests graph traversal, path enumeration, and metrics calculation.
"""

import pytest
import networkx as nx
from agents.simulation.agent import SimulationAgent
from agents.simulation.schema import SimulationInput, GraphMetrics


def test_simulation_basic():
    """Test basic simulation functionality."""
    agent = SimulationAgent()
    
    graph_data = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D"],
    }
    
    input_data = SimulationInput(
        vendor_id="A",
        graph_data=graph_data,
        max_depth=3
    )
    
    output = agent.run(input_data)
    
    assert output.source_vendor_id == "A"
    assert len(output.affected_node_ids) == 3  # B, C, D
    assert all(node in output.affected_node_ids for node in ["B", "C", "D"])
    assert len(output.propagation_paths) > 0


def test_simulation_max_depth():
    """Test that max_depth is respected."""
    agent = SimulationAgent()
    
    # Linear chain: A -> B -> C -> D
    graph_data = {
        "A": ["B"],
        "B": ["C"],
        "C": ["D"],
    }
    
    # Depth 1: should only reach B
    input_data = SimulationInput(
        vendor_id="A",
        graph_data=graph_data,
        max_depth=1
    )
    output = agent.run(input_data)
    assert "B" in output.affected_node_ids
    assert "C" not in output.affected_node_ids
    
    # Depth 2: should reach B and C
    input_data.max_depth = 2
    output = agent.run(input_data)
    assert "B" in output.affected_node_ids
    assert "C" in output.affected_node_ids
    assert "D" not in output.affected_node_ids


def test_simulation_missing_source():
    """Test handling of missing source node."""
    agent = SimulationAgent()
    
    graph_data = {"A": ["B"]}
    
    input_data = SimulationInput(
        vendor_id="Z",  # Not in graph
        graph_data=graph_data,
        max_depth=3
    )
    
    output = agent.run(input_data)
    
    assert output.source_vendor_id == "Z"
    assert len(output.affected_node_ids) == 0
    assert len(output.propagation_paths) == 0
    assert output.metrics.total_affected_nodes == 0


def test_simulation_metrics():
    """Test metrics calculation."""
    agent = SimulationAgent()
    
    graph_data = {
        "A": ["B", "C", "D"],  # Fan-out of 3
        "B": ["E"],
        "C": ["E"],
    }
    
    input_data = SimulationInput(
        vendor_id="A",
        graph_data=graph_data,
        max_depth=5
    )
    
    output = agent.run(input_data)
    
    # Check fan-out metric
    assert output.metrics.max_fan_out >= 1
    assert output.metrics.total_affected_nodes > 0
    assert output.metrics.average_path_length > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
