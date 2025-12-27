# Port 3000 Configuration - Complete Setup

## ✅ All Files Updated to Use Port 3000

### Updated Files

1. **`guardian/agents-v2/vertex_ai_entry.py`**
   - Default port changed from 8080 to 3000
   - Can be overridden with `PORT` environment variable

2. **`guardian/agents-v2/Dockerfile`**
   - Exposes port 3000
   - Container runs on port 3000

3. **`guardian/agents-v2/deploy_vertex_ai.sh`**
   - Container port set to 3000 for Vertex AI deployment

4. **`guardian/agents-v2/deploy_vertex_ai.ps1`**
   - Container port set to 3000 for Vertex AI deployment

5. **`guardian/agents-v2/env.example`**
   - Added `PORT=3000` configuration
   - Added `HOST=0.0.0.0` configuration

6. **Documentation Updated**
   - `DEPLOYMENT.md` - All port references updated
   - `QUICKSTART_VERTEX_AI.md` - Port references updated
   - `DEPLOYMENT_SUMMARY.md` - Architecture diagram updated

## 🚀 Running the ADK Server on Port 3000

### Option 1: Direct ADK Command

```bash
cd guardian
adk web --port 3000
```

### Option 2: Using Helper Scripts

**Linux/Mac:**
```bash
cd guardian/adk-agents
chmod +x start.sh
./start.sh
```

**Windows:**
```powershell
cd guardian/adk-agents
.\start.ps1
```

### Option 3: Python Script

```bash
cd guardian/adk-agents
python run_server.py
```

## 🌐 Access Points

Once the server is running on port 3000:

- **Web UI**: http://127.0.0.1:3000
- **API**: http://127.0.0.1:3000/api
- **Health Check**: http://127.0.0.1:3000/health (for Vertex AI deployment)

## 🔧 Configuration

### Environment Variables

You can override the port using environment variables:

```bash
# Set port via environment
export PORT=3000
python vertex_ai_entry.py

# Or in .env file
PORT=3000
HOST=0.0.0.0
```

### Vertex AI Deployment

When deploying to Vertex AI, the container will:
- Listen on port 3000
- Expose `/health` endpoint for health checks
- Expose `/predict` endpoint for predictions

## ✅ Verification

### Test Local Server

```bash
# Start server
python guardian/agents-v2/vertex_ai_entry.py

# Test health endpoint
curl http://localhost:3000/health

# Test root endpoint
curl http://localhost:3000/
```

### Test ADK Server

```bash
# Start ADK server
cd guardian
adk web --port 3000

# In another terminal, test
curl http://localhost:3000/api/agents
```

## 📋 Composite Agent Configuration

The Guardian Composite Agent is configured in `agent.py`:

- **Name**: `Guardian_Composite_Agent`
- **Model**: `gemini-2.5-flash`
- **Port**: 3000
- **Capabilities**: 
  - Supply-chain simulation
  - Impact reasoning
  - Mitigation prioritization

## 🎯 Next Steps

1. **Start the server**: `adk web --port 3000`
2. **Access the UI**: http://127.0.0.1:3000
3. **Test the agent**: Use the web interface or API
4. **Deploy to Vertex AI**: Use the deployment scripts (they're configured for port 3000)

---

**All systems configured for port 3000!** 🎉





