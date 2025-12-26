# Guardian AI Examples

This directory contains example scripts demonstrating how to use the Guardian AI agent system.

## Available Examples

### usage_examples.py

Comprehensive examples showing:

1. **Basic Usage** - Run pipeline with default graph
2. **Custom Graph** - Define your own supply chain graph
3. **With LLM Reasoning** - Use Google Gemini for impact analysis
4. **Individual Agents** - Use agents directly without orchestration

## Running Examples

```bash
# Run all examples
python examples/usage_examples.py

# Or run individually in Python
python -c "from examples.usage_examples import example_basic_usage; example_basic_usage()"
```

## Example: Quick Start

```python
from agents.registry import create_registry
from agents.orchestrator.schema import OrchestratorInput, GraphMetadata

# Initialize
registry = create_registry()
orchestrator = registry.get_orchestrator()

# Run
output = orchestrator.run(OrchestratorInput(
    vendor_id="VENDOR_001",
    graph_metadata=GraphMetadata(
        node_count=16,
        edge_count=17,
        graph_type="directed"
    ),
    max_depth=5
))

# Get results
print(f"Affected nodes: {len(output.simulation_results['affected_node_ids'])}")
```

## Example: Custom Graph

```python
custom_graph = {
    "SUPPLIER_A": ["MANUFACTURER_1", "MANUFACTURER_2"],
    "MANUFACTURER_1": ["DISTRIBUTOR_1"],
    "DISTRIBUTOR_1": ["RETAILER_1"],
}

registry = create_registry(graph_data=custom_graph)
orchestrator = registry.get_orchestrator()
# ... run as above
```

## Notes

- Set `GOOGLE_API_KEY` environment variable for LLM-powered reasoning
- Without API key, system uses fallback rule-based reasoning
- All examples use synthetic graphs for demonstration
