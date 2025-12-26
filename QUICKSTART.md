# Quick Start Guide

## Installation

```bash
# Clone the repository
cd guardian

# Install dependencies
pip install -r requirements.txt

# (Optional) Set up Google API key for LLM reasoning
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Basic Usage

```bash
# Run the pipeline with default settings
python agents/run_pipeline.py

# Specify vendor and depth
python agents/run_pipeline.py VENDOR_005 4
```

## View Results

Output is saved to `guardian_output_VENDOR_XXX.json`:

```bash
# Pretty print the output
python -m json.tool guardian_output_VENDOR_001.json

# View logs
cat guardian_ai.log
```

## Run Examples

```bash
# All usage examples
python examples/usage_examples.py

# Run tests
pytest tests/ -v
```

## Architecture Overview

```
User Input (vendor_id)
        ↓
OrchestratorAgent (coordinates)
        ↓
SimulationAgent (graph analysis)
        ↓
ImpactReasoningAgent (LLM explanation)
        ↓
MitigationAgent (risk reduction)
        ↓
Structured JSON Output
```

## Output Structure

```json
{
  "vendor_id": "VENDOR_001",
  "simulation_results": {
    "propagation_paths": [...],
    "affected_node_ids": [...],
    "metrics": {...}
  },
  "impact_analysis": {
    "explanations": [...],
    "summary": "...",
    "data_limitations": [...]
  },
  "mitigations": {
    "ranked_mitigations": [...],
    "total_paths_before": N,
    "methodology": "..."
  },
  "trace": [...]
}
```

## Next Steps

1. Review the [README.md](../README.md) for full documentation
2. Check [examples/](../examples/) for usage patterns
3. Run tests: `pytest tests/ -v`
4. Customize the graph in `orchestrator/agent.py`
