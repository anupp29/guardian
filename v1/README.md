# Guardian AI v1 - Multi-Agent System

**Production-grade agentic decision-support system using Google ADK**

## 🎯 Overview

Guardian AI v1 implements a complete multi-agent system for supply chain risk simulation and mitigation. The system is built using **Google's Agent Development Kit (ADK)** with strict role separation and structured communication. All agents are implemented using ADK's `Agent` and `LlmAgent` classes with proper tool integration and multi-agent coordination.

## 🏗️ Architecture

### 4-Agent System

```
OrchestratorAgent
    ↓
SimulationAgent → ImpactReasoningAgent → MitigationAgent
```

### Agent Responsibilities

| Agent | Role | Technology | ADK Type |
|-------|------|------------|----------|
| **OrchestratorAgent** | Pipeline coordination | Google ADK Multi-Agent | `LlmAgent` with `sub_agents` |
| **SimulationAgent** | Graph-based failure propagation | NetworkX + ADK | `Agent` with tools |
| **ImpactReasoningAgent** | Business impact explanation | Google Gemini 2.0 Flash + ADK | `LlmAgent` with tools |
| **MitigationAgent** | Structural mitigation ranking | NetworkX + ADK | `Agent` with tools |

## 📁 Folder Structure

```
v1/
├── agents/
│   ├── __init__.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompt.md
│   │   └── schema.py
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompt.md
│   │   └── schema.py
│   ├── impact_reasoning/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompt.md
│   │   └── schema.py
│   ├── mitigation/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── prompt.md
│   │   └── schema.py
│   ├── registry.py
│   └── run_pipeline.py
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Installation

```bash
cd v1
pip install -r requirements.txt

# Required: Set Google API key for Gemini (used by ImpactReasoningAgent)
export GOOGLE_API_KEY="your-api-key-here"
# OR
export GEMINI_API_KEY="your-api-key-here"
```

**Note:** This project uses **Google ADK (Agent Development Kit)** as the mandatory framework. All agents are built using ADK's `Agent` and `LlmAgent` classes. See [Google ADK Documentation](https://google.github.io/adk-docs/) for more details.

### Run Pipeline

```bash
# Basic usage (uses sample graph)
python -m agents.run_pipeline

# Specify vendor and depth
python -m agents.run_pipeline VENDOR_001 5

# With custom graph file
python -m agents.run_pipeline VENDOR_001 3 --graph-file graph.json

# Save output to specific file
python -m agents.run_pipeline VENDOR_001 3 --output-file results.json
```

### Expected Output

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

## 🔧 Agent Details

### 1. OrchestratorAgent

**Purpose:** Coordinate pipeline execution using Google ADK multi-agent system.

**ADK Implementation:**
- Uses `LlmAgent` with `sub_agents` parameter
- Coordinates SimulationAgent, ImpactReasoningAgent, and MitigationAgent
- Uses ADK Engine for agent orchestration

**Key Features:**
- Validates inputs
- Executes agents in strict order
- Aggregates outputs
- Provides execution trace

**Files:**
- `agents/orchestrator/agent.py` - ADK implementation with multi-agent coordination
- `agents/orchestrator/schema.py` - Pydantic models
- `agents/orchestrator/prompt.md` - System prompt

### 2. SimulationAgent

**Purpose:** Enumerate failure propagation paths in supply-chain graphs.

**ADK Implementation:**
- Uses `Agent` class (non-LLM agent)
- Implements `simulate_propagation` tool using ADK `Tool` class
- Exposes graph traversal functionality as ADK tools

**Key Features:**
- Deterministic BFS traversal
- Path enumeration
- Graph metrics calculation
- No probabilities or timing

**Files:**
- `agents/simulation/agent.py` - ADK Agent with tools
- `agents/simulation/schema.py` - Pydantic models
- `agents/simulation/prompt.md` - System prompt

### 3. ImpactReasoningAgent

**Purpose:** Explain business and operational implications using Gemini via ADK.

**ADK Implementation:**
- Uses `LlmAgent` class with Gemini 2.0 Flash model
- Implements `analyze_impact_explanations` tool using ADK `Tool` class
- Leverages ADK's LLM integration for reasoning

**Key Features:**
- Gemini-powered explanations via ADK
- Cause-effect reasoning
- Explicit uncertainty statements
- Fallback reasoning if API unavailable

**Files:**
- `agents/impact_reasoning/agent.py` - ADK LlmAgent with tools
- `agents/impact_reasoning/schema.py` - Pydantic models
- `agents/impact_reasoning/prompt.md` - System prompt

### 4. MitigationAgent

**Purpose:** Rank structural mitigations by risk reduction.

**ADK Implementation:**
- Uses `Agent` class (non-LLM agent)
- Implements `evaluate_mitigations` tool using ADK `Tool` class
- Uses graph simulation tools for risk reduction calculation

**Key Features:**
- Re-simulates modified graphs
- Measures path reduction
- Ranks by quantitative metrics
- Complexity estimation

**Files:**
- `agents/mitigation/agent.py` - ADK Agent with tools
- `agents/mitigation/schema.py` - Pydantic models
- `agents/mitigation/prompt.md` - System prompt

## 📊 Output Format

### JSON Structure

```json
{
  "success": true,
  "execution_trace": [
    {
      "agent_name": "SimulationAgent",
      "input_summary": "vendor_id=VENDOR_001, max_depth=3",
      "output_summary": "Found 17 paths affecting 12 nodes",
      "execution_time_ms": 45.23
    }
  ],
  "simulation_results": {
    "source_vendor_id": "VENDOR_001",
    "propagation_paths": [...],
    "total_affected_nodes": 12,
    "metrics": {...}
  },
  "impact_explanations": [...],
  "mitigation_recommendations": [...]
}
```

## 🧪 Testing

```bash
# Run pipeline with different configurations
python -m agents.run_pipeline VENDOR_001 3
python -m agents.run_pipeline VENDOR_005 4

# Check logs
tail -f guardian_ai.log

# Verify output
python -m json.tool guardian_output_VENDOR_001.json
```

## 🔐 Environment Variables

- `GOOGLE_API_KEY` - Optional. If not set, ImpactReasoningAgent uses fallback reasoning.

## 📝 Key Design Principles

1. **Google ADK First:** All agents built using Google ADK framework (mandatory requirement)
2. **Strict Role Separation:** Each agent has a single, well-defined responsibility
3. **Deterministic Core:** Simulation uses pure graph theory
4. **Responsible AI:** LLM only explains, never decides
5. **Transparency:** Full execution trace provided
6. **Tool-Based Architecture:** All agent capabilities exposed as ADK Tools
7. **Multi-Agent Coordination:** Orchestrator uses ADK's `sub_agents` for coordination

## 🎓 Hackathon Presentation Points

### Architecture Highlights
- ✅ **Built with Google ADK** - All agents use ADK's Agent/LlmAgent classes
- ✅ **Multi-Agent System** - Orchestrator coordinates sub-agents using ADK's `sub_agents`
- ✅ **Tool-Based Design** - All capabilities exposed as ADK Tools
- ✅ Separation of concerns with clear agent boundaries
- ✅ Deterministic simulation core (no speculation)
- ✅ Responsible AI (LLM for explanation only)
- ✅ Full transparency with execution traces

### Judge-Ready Talking Points
- "We use graph theory to enumerate structural risk paths"
- "LLMs explain impacts based strictly on provided data"
- "Mitigations ranked by measurable graph reduction"
- "System explicitly states data limitations and uncertainty"

## 🚧 Future Enhancements

- [ ] Real supply chain data integration
- [ ] FastAPI web interface
- [ ] Path visualization
- [ ] Multi-scenario batch analysis
- [ ] Historical trend analysis

## 📚 Documentation

- System prompts: `agents/*/prompt.md`
- Pydantic schemas: `agents/*/schema.py`
- Agent implementations: `agents/*/agent.py`

## 🤝 Contributing

This is a hackathon demonstration project. For production use, consider:
- Integrating real supply chain data sources
- Adding authentication/authorization
- Implementing rate limiting for API calls
- Adding comprehensive test coverage
- Setting up CI/CD pipelines

---

**Guardian AI v1** - Transparent, explainable supply chain risk analysis through agentic AI.

