"""
Unit tests for MitigationAgent.

Tests mitigation ranking and risk reduction calculations.
"""

import pytest
from agents.mitigation.agent import MitigationAgent
from agents.mitigation.schema import MitigationInput


def test_mitigation_basic():
    """Test basic mitigation functionality."""
    agent = MitigationAgent()
    
    graph_data = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["F"],
    }
    
    input_data = MitigationInput(
        graph_data=graph_data,
        source_vendor_id="A",
        affected_nodes=["B", "C", "D", "E", "F"],
        propagation_paths=[
            ["A", "B"],
            ["A", "C"],
            ["A", "B", "D"],
        ]
    )
    
    output = agent.run(input_data)
    
    assert output.total_paths_before == 3
    assert len(output.ranked_mitigations) > 0
    # Mitigations should be sorted by risk reduction
    if len(output.ranked_mitigations) > 1:
        assert output.ranked_mitigations[0].risk_reduction >= output.ranked_mitigations[1].risk_reduction


def test_mitigation_hub_detection():
    """Test that hubs are identified and prioritized."""
    agent = MitigationAgent()
    
    # B is a critical hub
    graph_data = {
        "A": ["B"],
        "B": ["C", "D", "E", "F"],  # High fan-out
        "C": ["G"],
    }
    
    input_data = MitigationInput(
        graph_data=graph_data,
        source_vendor_id="A",
        affected_nodes=["B", "C", "D", "E", "F", "G"],
        propagation_paths=[
            ["A", "B"],
            ["A", "B", "C"],
            ["A", "B", "D"],
        ]
    )
    
    output = agent.run(input_data)
    
    # B should be a top mitigation target
    assert len(output.ranked_mitigations) > 0
    top_target = output.ranked_mitigations[0].target
    # B should be prioritized due to high fan-out
    assert "B" in [m.target for m in output.ranked_mitigations[:3]]


def test_mitigation_no_affected():
    """Test handling when no nodes are affected."""
    agent = MitigationAgent()
    
    graph_data = {"A": ["B"]}
    
    input_data = MitigationInput(
        graph_data=graph_data,
        source_vendor_id="A",
        affected_nodes=[],
        propagation_paths=[]
    )
    
    output = agent.run(input_data)
    
    assert len(output.ranked_mitigations) == 0
    assert output.total_paths_before == 0


def test_mitigation_descriptions():
    """Test that mitigation descriptions are generated."""
    agent = MitigationAgent()
    
    graph_data = {
        "A": ["B", "C"],
        "B": ["D"],
    }
    
    input_data = MitigationInput(
        graph_data=graph_data,
        source_vendor_id="A",
        affected_nodes=["B", "C", "D"],
        propagation_paths=[["A", "B"], ["A", "C"]]
    )
    
    output = agent.run(input_data)
    
    for mitigation in output.ranked_mitigations:
        assert len(mitigation.description) > 0
        assert mitigation.target in mitigation.description


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
