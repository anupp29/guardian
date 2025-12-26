# 🛡️ Guardian AI v2 - Production-Grade Multi-Agent System

> **Enterprise-ready supply chain risk simulation powered by Google ADK**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-red.svg)](https://cloud.google.com/vertex-ai/docs/adk)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 Overview

Guardian AI v2 is a **production-grade multi-agent system** that simulates supply chain failure propagation using Google's Agent Development Kit (ADK). It combines deterministic graph traversal, LLM-powered impact reasoning, and quantitative risk mitigation to deliver actionable insights for supply chain security.

### ✨ Key Features

- 🤖 **Multi-Agent Architecture** - Four specialized agents orchestrated via Google ADK
- 🔄 **Deterministic Simulation** - Graph-based failure propagation analysis
- 🧠 **LLM-Powered Reasoning** - Gemini-powered business impact explanations
- 📊 **Quantitative Mitigation** - Data-driven risk reduction recommendations
- 🔍 **Full Traceability** - Complete execution trace for transparency
- ⚡ **Production Ready** - Error handling, validation, and logging built-in

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    GUARDIAN AI v2 ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   User Input │
    │ (vendor_id,  │
    │  max_depth)  │
    └──────┬───────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────────┐
    │           ORCHESTRATOR AGENT (Google ADK LlmAgent)      │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ • Validates Input                                │  │
    │  │ • Coordinates Pipeline                            │  │
    │  │ • Aggregates Results                             │  │
    │  │ • Manages Execution Trace                        │  │
    │  └──────────────────────────────────────────────────┘  │
    └──────┬──────────────────────────────────────────────────┘
           │
           │ Sequential Execution Pipeline
           │
    ┌──────┴──────────────────────────────────────────────────┐
    │                                                           │
    ▼                                                           ▼
┌──────────────────────┐                              ┌──────────────────────┐
│  SIMULATION AGENT    │                              │ IMPACT REASONING     │
│  (Google ADK Agent)  │                              │ AGENT                │
│                      │                              │ (Google ADK LlmAgent)│
│  ┌────────────────┐ │                              │                      │
│  │ • Graph Build  │ │                              │  ┌────────────────┐  │
│  │ • Path Enum    │ │                              │  │ • LLM Analysis │  │
│  │ • Metrics Calc │ │                              │  │ • Business     │  │
│  └────────────────┘ │                              │  │   Impact       │  │
│                      │                              │  │ • Uncertainty  │  │
│  Output:            │                              │  └────────────────┘  │
│  • Propagation Paths│                              │                      │
│  • Affected Nodes   │                              │  Output:            │
│  • Graph Metrics    │                              │  • Explanations     │
└──────────┬───────────┘                              │  • Data Limitations│
           │                                          └──────────┬───────────┘
           │                                                     │
           └──────────────────┬──────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │  MITIGATION AGENT    │
                    │  (Google ADK Agent)  │
                    │                      │
                    │  ┌────────────────┐ │
                    │  │ • Node Isolation│ │
                    │  │ • Edge Removal  │ │
                    │  │ • Risk Ranking  │ │
                    │  └────────────────┘ │
                    │                      │
                    │  Output:            │
                    │  • Ranked Actions  │
                    │  • Risk Reduction  │
                    │  • Trade-offs       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   FINAL OUTPUT       │
                    │  • Execution Trace   │
                    │  • Simulation Results│
                    │  • Impact Analysis   │
                    │  • Mitigations       │
                    └──────────────────────┘
```

---

## 🔄 Agent Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EXECUTION PIPELINE FLOW                          │
└─────────────────────────────────────────────────────────────────────┘

Step 1: INPUT VALIDATION
    ┌─────────────────────┐
    │ OrchestratorAgent    │
    │ • Validates vendor_id│
    │ • Checks max_depth   │
    │ • Prepares metadata  │
    └──────────┬───────────┘
               │
               ▼
Step 2: SIMULATION
    ┌─────────────────────┐
    │ SimulationAgent      │
    │                      │
    │ 1. Build Graph       │
    │    ┌──────────────┐  │
    │    │ NetworkX     │  │
    │    │ DiGraph      │  │
    │    └──────────────┘  │
    │                      │
    │ 2. Enumerate Paths   │
    │    ┌──────────────┐  │
    │    │ BFS Traversal│  │
    │    │ Max Depth    │  │
    │    └──────────────┘  │
    │                      │
    │ 3. Calculate Metrics │
    │    • Path Count      │
    │    • Affected Nodes  │
    │    • Graph Stats     │
    └──────────┬───────────┘
               │
               │ Output: {propagation_paths, affected_nodes, metrics}
               │
               ▼
Step 3: IMPACT REASONING
    ┌─────────────────────┐
    │ ImpactReasoningAgent│
    │                      │
    │ 1. Analyze Paths    │
    │    ┌──────────────┐  │
    │    │ Gemini LLM   │  │
    │    │ Reasoning    │  │
    │    └──────────────┘  │
    │                      │
    │ 2. Generate          │
    │    Explanations      │
    │    • Cause           │
    │    • Effect          │
    │    • Business Impact │
    │                      │
    │ 3. Document          │
    │    Limitations       │
    └──────────┬───────────┘
               │
               │ Output: {explanations, summary, data_limitations}
               │
               ▼
Step 4: MITIGATION ANALYSIS
    ┌─────────────────────┐
    │ MitigationAgent     │
    │                      │
    │ 1. Identify          │
    │    Candidates        │
    │    • High-impact     │
    │      nodes           │
    │    • Critical edges  │
    │                      │
    │ 2. Evaluate Actions  │
    │    ┌──────────────┐  │
    │    │ Re-simulate   │  │
    │    │ Modified Graph│  │
    │    │ Measure Risk  │  │
    │    │ Reduction     │  │
    │    └──────────────┘  │
    │                      │
    │ 3. Rank by           │
    │    Effectiveness     │
    └──────────┬───────────┘
               │
               │ Output: {ranked_mitigations, risk_reduction}
               │
               ▼
Step 5: AGGREGATION
    ┌─────────────────────┐
    │ OrchestratorAgent   │
    │                      │
    │ • Combines Results   │
    │ • Creates Trace      │
    │ • Formats Output     │
    └─────────────────────┘
```

---

## 🤖 Agent Details

### 1. OrchestratorAgent 🎯

**Type:** Google ADK LlmAgent  
**Model:** `gemini-2.0-flash-exp`  
**Role:** Pipeline coordinator

**Responsibilities:**
- ✅ Input validation and sanitization
- ✅ Sequential agent execution
- ✅ Result aggregation
- ✅ Execution trace management
- ✅ Error handling and recovery

**Key Features:**
- Preserves all agent outputs without modification
- Maintains full execution trace with timing
- Handles partial failures gracefully

### 2. SimulationAgent 🔬

**Type:** Google ADK Agent  
**Tools:** `simulate_propagation` FunctionTool  
**Role:** Graph traversal and path enumeration

**Responsibilities:**
- ✅ Build NetworkX directed graph from metadata
- ✅ Enumerate all propagation paths (BFS)
- ✅ Calculate graph metrics
- ✅ Identify affected nodes

**Algorithm:**
```
1. Parse graph_metadata → NetworkX DiGraph
2. BFS from source vendor up to max_depth
3. Record all paths: [source → node1 → node2 → ...]
4. Collect unique affected nodes
5. Calculate: path_count, avg_length, max_fan_out
```

**Output Schema:**
```python
{
    "source_vendor_id": str,
    "propagation_paths": List[PropagationPath],
    "total_affected_nodes": int,
    "unique_affected_nodes": List[str],
    "metrics": {
        "max_fan_out": int,
        "average_path_length": float,
        "max_path_length": int,
        "total_paths": int
    }
}
```

### 3. ImpactReasoningAgent 🧠

**Type:** Google ADK LlmAgent  
**Model:** `gemini-2.0-flash-exp`  
**Tools:** `analyze_impact_explanations` FunctionTool  
**Role:** Business impact explanation

**Responsibilities:**
- ✅ Analyze propagation paths
- ✅ Generate human-readable explanations
- ✅ Translate technical results to business impact
- ✅ Document data limitations

**LLM Usage:**
- Uses Gemini for contextual reasoning
- Explains **why** paths matter, not **what** will happen
- Grounds all reasoning in provided data
- Explicitly states uncertainty

**Output Schema:**
```python
{
    "explanations": [
        {
            "path": List[str],
            "cause": str,
            "effect": str,
            "business_impact": str,
            "uncertainty_notes": str
        }
    ],
    "data_limitations": List[str],
    "summary": str
}
```

### 4. MitigationAgent ⚡

**Type:** Google ADK Agent  
**Tools:** `evaluate_mitigations` FunctionTool  
**Role:** Risk reduction analysis

**Responsibilities:**
- ✅ Identify mitigation candidates
- ✅ Evaluate effectiveness via re-simulation
- ✅ Rank actions by risk reduction
- ✅ Explain trade-offs

**Mitigation Types:**
1. **Node Isolation** - Remove critical nodes
2. **Edge Removal** - Break dependency links

**Evaluation Method:**
```
For each candidate mitigation:
    1. Create modified graph (remove node/edge)
    2. Re-run simulation
    3. Compare path counts
    4. Calculate risk_reduction = (original - new) / original
    5. Rank by risk_reduction (descending)
```

**Output Schema:**
```python
{
    "ranked_mitigations": [
        {
            "action_type": str,  # "isolate_node" | "remove_edge"
            "target": str,
            "description": str,
            "risk_reduction": float,  # 0.0 to 1.0
            "affected_paths_reduced": int,
            "implementation_complexity": str,  # "low" | "medium" | "high"
            "trade_offs": str
        }
    ],
    "total_paths_original": int,
    "total_paths_reducible": int
}
```

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd guardian/agents-v2

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Vertex AI Deployment

**Ready for production deployment on Google Cloud Vertex AI!**

### Quick Deploy

```bash
# 1. Configure environment
cp env.example .env
# Edit .env with your GCP_PROJECT_ID

# 2. Deploy
./deploy_vertex_ai.sh  # Linux/Mac
# or
.\deploy_vertex_ai.ps1  # Windows
```

### Documentation

- **[Quick Start Guide](QUICKSTART_VERTEX_AI.md)** - Get deployed in 5 minutes
- **[Full Deployment Guide](DEPLOYMENT.md)** - Complete deployment documentation
- **[Deployment Summary](DEPLOYMENT_SUMMARY.md)** - Overview of deployment setup

### Features

✅ Production-ready Docker container  
✅ Automated deployment scripts  
✅ Health checks and monitoring  
✅ Auto-scaling support  
✅ Complete testing suite  

See [DEPLOYMENT.md](DEPLOYMENT.md) for details.

### Dependencies

```
pydantic>=2.0.0          # Data validation
networkx>=3.0            # Graph operations
google-adk>=1.0.0        # Agent Development Kit (MANDATORY)
google-generativeai>=0.3.0  # Gemini API
fastapi>=0.100.0         # Optional: Web interface
uvicorn>=0.23.0          # Optional: ASGI server
```

### Optional: Google API Key

For LLM-powered impact reasoning, set your Google API key:

```bash
export GOOGLE_API_KEY="your-api-key-here"
# or
export GEMINI_API_KEY="your-api-key-here"
```

**Note:** The system works without an API key but will use fallback reasoning.

---

## 🚀 Quick Start

### Basic Usage

```python
from agents.registry import get_registry
from agents.orchestrator import OrchestratorInput

# Get registry
registry = get_registry()

# Get orchestrator agent
orchestrator = registry.get_agent("OrchestratorAgent")

# Prepare input
input_data = OrchestratorInput(
    vendor_id="VENDOR_001",
    max_depth=3,
    graph_metadata=None  # Uses sample graph if None
)

# Run pipeline
result = orchestrator.run(input_data)

# Check results
if result.success:
    print(f"Found {len(result.simulation_results['propagation_paths'])} paths")
    print(f"Affected {result.simulation_results['total_affected_nodes']} nodes")
    print(f"Generated {len(result.impact_explanations)} explanations")
    print(f"Ranked {len(result.mitigation_recommendations)} mitigations")
else:
    print(f"Error: {result.error_message}")
```

### Using Individual Agents

```python
from agents.simulation import SimulationAgent, SimulationInput

# Use SimulationAgent directly
sim_agent = SimulationAgent()
result = sim_agent.run({
    "vendor_id": "VENDOR_001",
    "max_depth": 2
})

print(f"Paths: {len(result['propagation_paths'])}")
print(f"Affected: {result['total_affected_nodes']} nodes")
```

### Custom Graph

```python
custom_graph = {
    "nodes": [
        {"id": "VENDOR_A"},
        {"id": "VENDOR_B"},
        {"id": "VENDOR_C"}
    ],
    "edges": [
        {"source": "VENDOR_A", "target": "VENDOR_B"},
        {"source": "VENDOR_B", "target": "VENDOR_C"}
    ]
}

input_data = OrchestratorInput(
    vendor_id="VENDOR_A",
    max_depth=3,
    graph_metadata=custom_graph
)
```

---

## 📊 Example Output

```json
{
  "success": true,
  "execution_trace": [
    {
      "agent_name": "SimulationAgent",
      "input_summary": "vendor_id=VENDOR_001, max_depth=3",
      "output_summary": "Found 17 paths affecting 12 nodes",
      "execution_time_ms": 45.23
    },
    {
      "agent_name": "ImpactReasoningAgent",
      "input_summary": "17 paths, 12 nodes",
      "output_summary": "Generated 5 impact explanations",
      "execution_time_ms": 1234.56
    },
    {
      "agent_name": "MitigationAgent",
      "input_summary": "12 affected nodes",
      "output_summary": "Ranked 8 mitigation actions",
      "execution_time_ms": 234.12
    }
  ],
  "simulation_results": {
    "source_vendor_id": "VENDOR_001",
    "propagation_paths": [
      {
        "path": ["VENDOR_001", "VENDOR_002", "VENDOR_004"],
        "length": 2,
        "affected_nodes": ["VENDOR_002", "VENDOR_004"]
      }
    ],
    "total_affected_nodes": 12,
    "metrics": {
      "max_fan_out": 3,
      "average_path_length": 2.1,
      "max_path_length": 4,
      "total_paths": 17
    }
  },
  "impact_explanations": [
    {
      "path": ["VENDOR_001", "VENDOR_002"],
      "cause": "Disruption at VENDOR_001",
      "effect": "Cascades to VENDOR_002",
      "business_impact": "Operational disruption affecting downstream services",
      "uncertainty_notes": "Inventory levels and lead times unknown"
    }
  ],
  "mitigation_recommendations": [
    {
      "action_type": "isolate_node",
      "target": "VENDOR_002",
      "description": "Isolate VENDOR_002 to break 8 propagation paths",
      "risk_reduction": 0.47,
      "affected_paths_reduced": 8,
      "implementation_complexity": "medium",
      "trade_offs": "May impact services directly dependent on VENDOR_002"
    }
  ]
}
```

---

## 🔍 Key Design Principles

### 1. **Deterministic Core** 🎯
- Graph traversal is deterministic and reproducible
- No probabilistic predictions or timing assumptions
- Results are based on graph structure alone

### 2. **Agent Separation** 🔄
- Each agent has a single, well-defined responsibility
- No agent modifies another agent's output
- Clear data flow between agents

### 3. **LLM for Explanation, Not Decision** 🧠
- Gemini is used for **explanation generation**, not data creation
- All reasoning is grounded in provided simulation data
- Explicit uncertainty documentation

### 4. **Quantitative Mitigation** 📊
- Mitigations are evaluated by **measurable risk reduction**
- Re-simulation provides objective effectiveness metrics
- Ranking is data-driven, not heuristic-based

### 5. **Full Transparency** 🔍
- Complete execution trace with timing
- All intermediate results preserved
- Error messages include context

---

## 🧪 Testing

### Run Test Suite

```bash
cd guardian/v2
python test_local.py
```

### Expected Output

```
======================================================================
Guardian v2 Local Testing
======================================================================

[OK] Registry imports
[OK] Orchestrator imports
[OK] Simulation imports
[OK] ImpactReasoning imports
[OK] Mitigation imports

[OK] Registry instantiation
[OK] SimulationAgent instantiation
[OK] ImpactReasoningAgent instantiation
[OK] MitigationAgent instantiation
[OK] OrchestratorAgent instantiation

[SUCCESS] All tests passed!
```

---

## 📁 Project Structure

```
guardian/v2/
├── agents/
│   ├── __init__.py
│   ├── registry.py              # Central agent registry
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── agent.py             # OrchestratorAgent implementation
│   │   ├── schema.py            # Pydantic models
│   │   └── prompt.md            # System prompt
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── agent.py             # SimulationAgent implementation
│   │   ├── schema.py
│   │   └── prompt.md
│   ├── impact_reasoning/
│   │   ├── __init__.py
│   │   ├── agent.py             # ImpactReasoningAgent implementation
│   │   ├── schema.py
│   │   └── prompt.md
│   └── mitigation/
│       ├── __init__.py
│       ├── agent.py             # MitigationAgent implementation
│       ├── schema.py
│       └── prompt.md
├── requirements.txt             # Python dependencies
├── test_local.py                # Local test suite
└── README.md                    # This file
```

---

## 🎓 Presentation Highlights

### What Makes This Impressive

1. **Production-Grade Architecture**
   - Error handling, validation, logging
   - Type-safe with Pydantic schemas
   - Modular and extensible design

2. **Google ADK Integration**
   - Uses official Google ADK framework
   - Multi-agent orchestration
   - Tool-based agent capabilities

3. **Deterministic + LLM Hybrid**
   - Graph simulation is deterministic
   - LLM adds contextual reasoning
   - Best of both worlds

4. **Quantitative Risk Analysis**
   - Measurable risk reduction metrics
   - Data-driven mitigation ranking
   - Objective evaluation methodology

5. **Full Traceability**
   - Complete execution trace
   - Timing information
   - Intermediate results preserved

### Demo Flow

```
1. Show input → OrchestratorAgent
2. Display simulation results (paths, nodes)
3. Show impact explanations (LLM-generated)
4. Present ranked mitigations
5. Highlight execution trace
```

---

## 🔧 Advanced Usage

### Custom Agent Configuration

```python
from agents.impact_reasoning import ImpactReasoningAgent

# Initialize with custom API key
agent = ImpactReasoningAgent(api_key="your-key")

# Use directly
result = agent.run({
    "simulation_results": {...},
    "graph_metadata": {...}
})
```

### Access ADK Agents Directly

```python
from agents.registry import get_registry

registry = get_registry()

# Get ADK agent instance
adk_agent = registry.get_adk_agent("SimulationAgent")

# Use ADK agent directly
response = adk_agent.run(...)
```

### Error Handling

```python
try:
    result = orchestrator.run(input_data)
    if not result.success:
        print(f"Pipeline failed: {result.error_message}")
        if result.simulation_results:
            print("Partial results available")
except Exception as e:
    print(f"Error: {e}")
```

---

## 📚 API Reference

### OrchestratorAgent

```python
class OrchestratorAgent:
    def run(self, input_data: OrchestratorInput) -> OrchestratorOutput
```

### SimulationAgent

```python
class SimulationAgent:
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]
```

### ImpactReasoningAgent

```python
class ImpactReasoningAgent:
    def __init__(self, api_key: str = None)
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]
```

### MitigationAgent

```python
class MitigationAgent:
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]
```

### AgentRegistry

```python
class AgentRegistry:
    def get_agent(self, agent_name: str) -> Any
    def get_adk_agent(self, agent_name: str) -> Any
    def get_engine(self) -> Optional[Any]
    def list_agents(self) -> List[str]
    def list_adk_agents(self) -> List[str]
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'google.adk.core'`
- **Solution:** Engine is optional. The system works without it.

**Issue:** `FileNotFoundError: prompt.md`
- **Solution:** Ensure you're running from the correct directory or use relative imports.

**Issue:** LLM calls failing
- **Solution:** Check `GOOGLE_API_KEY` environment variable. System works with fallback reasoning.

**Issue:** Graph not found
- **Solution:** Provide `graph_metadata` or system will use sample graph.

---

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows existing patterns
- Tests pass (`python test_local.py`)
- Type hints are included
- Documentation is updated

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Google ADK** - Agent Development Kit framework
- **NetworkX** - Graph analysis library
- **Pydantic** - Data validation
- **Gemini** - LLM reasoning capabilities

---

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review test examples

---

**Built with ❤️ using Google ADK**

*Guardian AI v2 - Production-ready multi-agent supply chain risk simulation*

