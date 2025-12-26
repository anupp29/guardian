# Guardian AI v1 - Quick Start Guide

## 🚀 Installation

```bash
cd v1
pip install -r requirements.txt
```

## ⚙️ Configuration (Optional)

Set Google API key for Gemini-powered impact reasoning:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Note:** System works without API key (uses fallback reasoning).

## ▶️ Run Pipeline

### Basic Usage

```bash
python -m agents.run_pipeline
```

### With Parameters

```bash
# Specify vendor and depth
python -m agents.run_pipeline VENDOR_001 5

# With custom graph file
python -m agents.run_pipeline VENDOR_001 3 --graph-file graph.json

# Custom output file
python -m agents.run_pipeline VENDOR_001 3 --output-file results.json
```

## ✅ Verify Setup

```bash
python verify_setup.py
```

## 📊 Expected Output

```
================================================================================
  GUARDIAN AI - SUPPLY CHAIN RISK SIMULATION
================================================================================

✅ Pipeline executed successfully

EXECUTION TRACE
--------------------------------------------------------------------------------
[1] SimulationAgent
    Input: vendor_id=VENDOR_001, max_depth=3
    Output: Found 17 paths affecting 12 nodes
    Time: 45.23ms

[2] ImpactReasoningAgent
    Input: 17 paths, 12 nodes
    Output: Generated 10 impact explanations
    Time: 1234.56ms

[3] MitigationAgent
    Input: 12 affected nodes
    Output: Ranked 8 mitigation actions
    Time: 234.12ms

💾 Results saved to: guardian_output_VENDOR_001.json
```

## 🏗️ Architecture

```
OrchestratorAgent
    ↓
SimulationAgent → ImpactReasoningAgent → MitigationAgent
```

## 📁 Key Files

- `agents/run_pipeline.py` - Main entry point
- `agents/registry.py` - Agent registry
- `agents/*/agent.py` - Agent implementations
- `agents/*/schema.py` - Pydantic models
- `agents/*/prompt.md` - System prompts

## 🔍 Troubleshooting

### Import Errors
```bash
# Make sure you're in the v1 directory
cd v1
python -m agents.run_pipeline
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Gemini API Issues
- System works without API key (fallback mode)
- Check `GOOGLE_API_KEY` environment variable
- Verify API key is valid

## 📚 Next Steps

1. Run verification: `python verify_setup.py`
2. Execute pipeline: `python -m agents.run_pipeline VENDOR_001 3`
3. Review output: `cat guardian_output_VENDOR_001.json`
4. Check logs: `tail -f guardian_ai.log`

---

For detailed documentation, see [README.md](README.md)

