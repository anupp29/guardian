# 🚀 Quick Start - Vertex AI Deployment

Get Guardian AI v2 deployed to Vertex AI in minutes!

## ⚡ Fast Track (5 minutes)

### 1. Setup (One-time)

```bash
# Clone and navigate
cd guardian/agents-v2

# Copy environment template
cp env.example .env

# Edit .env with your values
# Set at minimum: GCP_PROJECT_ID
```

### 2. Authenticate

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Deploy

**Linux/Mac:**
```bash
./deploy_vertex_ai.sh
```

**Windows:**
```powershell
.\deploy_vertex_ai.ps1
```

### 4. Test

```bash
python test_vertex_ai.py \
    --endpoint-id=YOUR_ENDPOINT_ID \
    --project-id=YOUR_PROJECT_ID
```

## 📝 Detailed Steps

### Prerequisites Check

```bash
# Check gcloud
gcloud --version

# Check Docker
docker --version
docker ps

# Check Python
python --version  # Should be 3.10+
```

### Environment Configuration

Edit `.env` file:

```bash
# Minimum required
GCP_PROJECT_ID=your-project-id-here
GCP_REGION=us-central1

# Optional but recommended
GOOGLE_API_KEY=your-api-key
GEMINI_API_KEY=your-api-key
```

### Manual Deployment (if script fails)

```bash
# 1. Build image
docker build -t guardian-agents-v2 -f Dockerfile .

# 2. Tag for Artifact Registry
IMAGE_URI="us-central1-docker.pkg.dev/YOUR_PROJECT/guardian-ai/guardian-agents-v2:latest"
docker tag guardian-agents-v2 $IMAGE_URI

# 3. Push
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push $IMAGE_URI

# 4. Upload model
gcloud ai models upload \
    --region=us-central1 \
    --display-name="Guardian AI v2" \
    --container-image-uri=$IMAGE_URI \
    --container-ports=3000 \
    --container-health-route=/health \
    --container-predict-route=/predict

# 5. Create endpoint
ENDPOINT_ID=$(gcloud ai endpoints create \
    --region=us-central1 \
    --display-name="Guardian AI v2 Endpoint" \
    --format="value(name)")

# 6. Deploy
gcloud ai endpoints deploy-model $ENDPOINT_ID \
    --region=us-central1 \
    --model=MODEL_ID \
    --display-name="Guardian AI v2" \
    --machine-type=n1-standard-4
```

## 🧪 Testing Locally

Before deploying, test locally:

```bash
# Test entry point
python vertex_ai_entry.py test

# Test health
python vertex_ai_entry.py health

# Run local server
python vertex_ai_entry.py
# Then in another terminal:
curl http://localhost:3000/health
```

## 🔍 Verify Deployment

```bash
# List endpoints
gcloud ai endpoints list --region=us-central1

# Describe endpoint
gcloud ai endpoints describe ENDPOINT_ID --region=us-central1

# View logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" --limit=10
```

## 📊 Example Usage

```python
from google.cloud import aiplatform

# Initialize
aiplatform.init(project="your-project", location="us-central1")
endpoint = aiplatform.Endpoint("your-endpoint-id")

# Make prediction
response = endpoint.predict(instances=[{
    "vendor_id": "VENDOR_001",
    "max_depth": 2
}])

print(response.predictions[0])
```

## 🆘 Troubleshooting

### "Permission denied" errors
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT \
    --member="user:YOUR_EMAIL" \
    --role="roles/aiplatform.admin"
```

### "Image not found" errors
```bash
# Verify image exists
gcloud artifacts docker images list \
    us-central1-docker.pkg.dev/YOUR_PROJECT/guardian-ai
```

### "Endpoint not responding"
```bash
# Check endpoint status
gcloud ai endpoints describe ENDPOINT_ID --region=us-central1

# View recent logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" \
    --limit=50 --format=json
```

## 📚 Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed documentation
- Set up monitoring and alerts
- Configure auto-scaling
- Create CI/CD pipeline

---

**Need help?** Check the full [DEPLOYMENT.md](DEPLOYMENT.md) guide.

