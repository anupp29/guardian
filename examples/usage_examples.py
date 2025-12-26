"""
Example usage script for Guardian AI.

Demonstrates how to use the agent system programmatically.
"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.registry import create_registry
from agents.orchestrator.schema import OrchestratorInput, GraphMetadata


def example_basic_usage():
    """Basic usage example with default graph."""
    print("="*80)
    print("EXAMPLE 1: Basic Usage")
    print("="*80)
    
    # Initialize agent registry
    registry = create_registry()
    orchestrator = registry.get_orchestrator()
    
    # Prepare input
    input_data = OrchestratorInput(
        vendor_id="VENDOR_001",
        graph_metadata=GraphMetadata(
            node_count=16,
            edge_count=17,
            graph_type="directed"
        ),
        max_depth=4
    )
    
    # Run pipeline
    output = orchestrator.run(input_data)
    
    # Print results
    print(f"\n✅ Simulation complete!")
    print(f"   Affected nodes: {len(output.simulation_results['affected_node_ids'])}")
    print(f"   Propagation paths: {len(output.simulation_results['propagation_paths'])}")
    print(f"   Top mitigation: {output.mitigations['ranked_mitigations'][0]['target'] if output.mitigations['ranked_mitigations'] else 'None'}")


def example_custom_graph():
    """Example with custom supply chain graph."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Graph")
    print("="*80)
    
    # Define a custom supply chain graph
    custom_graph = {
        "SUPPLIER_A": ["MANUFACTURER_1", "MANUFACTURER_2"],
        "MANUFACTURER_1": ["DISTRIBUTOR_1"],
        "MANUFACTURER_2": ["DISTRIBUTOR_1", "DISTRIBUTOR_2"],
        "DISTRIBUTOR_1": ["RETAILER_1", "RETAILER_2"],
        "DISTRIBUTOR_2": ["RETAILER_3"],
    }
    
    # Initialize with custom graph
    registry = create_registry(graph_data=custom_graph)
    orchestrator = registry.get_orchestrator()
    
    # Prepare input
    input_data = OrchestratorInput(
        vendor_id="SUPPLIER_A",
        graph_metadata=GraphMetadata(
            node_count=len(custom_graph),
            edge_count=sum(len(v) for v in custom_graph.values()),
            graph_type="directed"
        ),
        max_depth=3
    )
    
    # Run pipeline
    output = orchestrator.run(input_data)
    
    # Print sample paths
    print(f"\n✅ Analysis complete for custom graph!")
    print(f"\nSample propagation paths:")
    for i, path_data in enumerate(output.simulation_results['propagation_paths'][:5], 1):
        path_str = " → ".join(path_data['path'])
        print(f"   {i}. {path_str}")


def example_with_llm():
    """Example using Gemini LLM for impact reasoning."""
    print("\n" + "="*80)
    print("EXAMPLE 3: With LLM Reasoning")
    print("="*80)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY not set - using fallback reasoning")
        print("   Set API key with: export GOOGLE_API_KEY='your-key'")
    else:
        print(f"\n✅ Using Google Gemini for impact reasoning")
    
    # Initialize with API key
    registry = create_registry(google_api_key=api_key)
    orchestrator = registry.get_orchestrator()
    
    # Prepare input
    input_data = OrchestratorInput(
        vendor_id="VENDOR_001",
        graph_metadata=GraphMetadata(
            node_count=16,
            edge_count=17,
            graph_type="directed"
        ),
        max_depth=3
    )
    
    # Run pipeline
    output = orchestrator.run(input_data)
    
    # Print impact analysis
    print(f"\nImpact Analysis Summary:")
    print(f"   {output.impact_analysis['summary']}")
    
    print(f"\nSample Explanations:")
    for i, exp in enumerate(output.impact_analysis['explanations'][:3], 1):
        print(f"\n   {i}. Cause: {exp['cause']}")
        print(f"      Effect: {exp['effect']}")


def example_individual_agents():
    """Example using individual agents directly."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Using Individual Agents")
    print("="*80)
    
    from agents.simulation.agent import SimulationAgent
    from agents.simulation.schema import SimulationInput
    
    # Use simulation agent directly
    sim_agent = SimulationAgent()
    
    sample_graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D", "E"],
    }
    
    sim_input = SimulationInput(
        vendor_id="A",
        graph_data=sample_graph,
        max_depth=3
    )
    
    sim_output = sim_agent.run(sim_input)
    
    print(f"\n✅ Direct agent usage:")
    print(f"   Source: {sim_output.source_vendor_id}")
    print(f"   Affected: {sim_output.affected_node_ids}")
    print(f"   Paths found: {len(sim_output.propagation_paths)}")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_custom_graph()
    example_with_llm()
    example_individual_agents()
    
    print("\n" + "="*80)
    print("✅ All examples completed successfully!")
    print("="*80)
