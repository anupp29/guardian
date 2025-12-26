# Guardian Composite Agent - ADK

Composite agent that performs supply-chain simulation, impact reasoning, and mitigation prioritization using Google ADK.

## 🚀 Quick Start

### Run ADK Web Server

```bash
# Using ADK CLI directly
cd guardian
adk web --port 3000

# Or use the helper script
cd guardian/adk-agents
python run_server.py
```

### Access the Server

Once running, access at:
- **Web UI**: http://127.0.0.1:3000
- **API**: http://127.0.0.1:3000/api

## 🤖 Agent Configuration

The composite agent is defined in `agent.py`:

```python
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name='Guardian_Composite_Agent',
    model='gemini-2.5-flash',
    description='Composite agent that performs supply-chain simulation, impact reasoning, and mitigation prioritization in a single execution, while maintaining strict logical separation of responsibilities.',
    sub_agents=[],
    instruction='...',
    tools=[],
)
```

## 📋 Agent Capabilities

The Guardian Composite Agent performs three logically separate steps:

### STEP 1: Simulation
- Analyzes the provided supply-chain graph
- Enumerates deterministic propagation paths starting from the given vendor
- Does NOT predict attacks, probabilities, or timelines

### STEP 2: Impact Reasoning
- Explains consequences based strictly on simulation output
- Uses cause → effect language
- Explicitly states uncertainty where data is missing

### STEP 3: Mitigation Prioritization
- Proposes structural mitigation actions
- Ranks them based on how much they reduce cascade reach
- Does NOT suggest automation or products

## 🔧 Configuration

### Port Configuration

Default port is **3000**. To change:

```bash
# Via environment variable
export ADK_PORT=3000
adk web

# Via command line
adk web --port 3000
```

### Model Configuration

The agent uses `gemini-2.5-flash` by default. To change, edit `agent.py`:

```python
root_agent = LlmAgent(
    model='your-model-name',
    ...
)
```

## 📊 Output Format

The agent returns JSON with this structure:

```json
{
  "simulation_results": {
    "propagation_paths": [...],
    "affected_nodes": [...],
    "metrics": {...}
  },
  "impact_explanation": {
    "explanations": [...],
    "data_limitations": [...],
    "summary": "..."
  },
  "mitigation_recommendations": {
    "ranked_mitigations": [...],
    "risk_reduction": {...}
  }
}
```

## 🧪 Testing

### Test Locally

```bash
# Start server
adk web --port 3000

# In another terminal, test with curl
curl -X POST http://127.0.0.1:3000/api/agents/Guardian_Composite_Agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_id": "VENDOR_001",
    "max_depth": 2
  }'
```

### Test with Python

```python
from google.adk.agents import LlmAgent
from guardian.adk_agents.agent import root_agent

# Use the agent
result = root_agent.run({
    "vendor_id": "VENDOR_001",
    "max_depth": 2
})

print(result)
```

## 🐛 Troubleshooting

### Port Already in Use

If you get `[Errno 10048]` error:

```bash
# Find process using port 3000
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/Mac

# Kill the process or use a different port
adk web --port 3001
```

### ADK Not Found

```bash
pip install google-adk
```

### Import Errors

Make sure you're in the correct directory:

```bash
cd guardian
adk web --port 3000
```

## 📚 Related Documentation

- [Guardian AI v2 README](../agents-v2/README.md)
- [Vertex AI Deployment](../agents-v2/DEPLOYMENT.md)
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/adk)


