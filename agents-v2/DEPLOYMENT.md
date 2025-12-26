# 🚀 Guardian AI v2 - Vertex AI Deployment Guide

Complete guide for deploying Guardian AI v2 to Google Cloud Vertex AI.

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured
   ```bash
   gcloud --version
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. **Docker** installed and running
4. **Python 3.10+** for local testing
5. **Required APIs enabled** (deployment script handles this)

## 🔧 Setup

### 1. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp env.example .env
```

Edit `.env` and set:
- `GCP_PROJECT_ID`: Your Google Cloud Project ID
- `GCP_REGION`: Preferred region (default: us-central1)
- `GOOGLE_API_KEY` or `GEMINI_API_KEY`: For Gemini API access
- Other optional settings as needed

### 2. Authenticate with Google Cloud

**Option A: Application Default Credentials (Recommended)**
```bash
gcloud auth application-default login
```

**Option B: Service Account**
1. Create a service account in Google Cloud Console
2. Grant roles: `Vertex AI User`, `Artifact Registry Writer`, `Storage Admin`
3. Download JSON key
4. Set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json` in `.env`

### 3. Enable Required APIs

The deployment script automatically enables these, but you can do it manually:

```bash
gcloud services enable \
    aiplatform.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com
```

## 🚀 Deployment

### Quick Deploy (Linux/Mac)

```bash
chmod +x deploy_vertex_ai.sh
./deploy_vertex_ai.sh
```

### Quick Deploy (Windows PowerShell)

```powershell
.\deploy_vertex_ai.ps1
```

### Manual Deployment Steps

If you prefer manual control:

#### Step 1: Build Docker Image

```bash
# Set variables
PROJECT_ID=your-project-id
REGION=us-central1
REPO=guardian-ai
LOCATION=us-central1
IMAGE_NAME=guardian-agents-v2
IMAGE_TAG=latest

# Configure Docker
gcloud auth configure-docker ${LOCATION}-docker.pkg.dev

# Build and push
IMAGE_URI="${LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t $IMAGE_URI -f Dockerfile .
docker push $IMAGE_URI
```

#### Step 2: Create Artifact Registry Repository

```bash
gcloud artifacts repositories create $REPO \
    --repository-format=docker \
    --location=$LOCATION \
    --description="Guardian AI v2 Docker images"
```

#### Step 3: Upload Model to Vertex AI

```bash
gcloud ai models upload \
    --region=$REGION \
    --display-name="Guardian AI v2 Multi-Agent System" \
    --container-image-uri=$IMAGE_URI \
    --container-ports=3000 \
    --container-health-route=/health \
    --container-predict-route=/predict
```

#### Step 4: Create Endpoint and Deploy

```bash
# Create endpoint
ENDPOINT_ID=$(gcloud ai endpoints create \
    --region=$REGION \
    --display-name="Guardian AI v2 Endpoint" \
    --format="value(name)")

# Deploy model
gcloud ai endpoints deploy-model $ENDPOINT_ID \
    --region=$REGION \
    --model=MODEL_ID \
    --display-name="Guardian AI v2" \
    --machine-type=n1-standard-4 \
    --min-replica-count=1 \
    --max-replica-count=3
```

## 🧪 Testing

### Test Local Entry Point

```bash
python vertex_ai_entry.py test
```

### Test Health Check

```bash
python vertex_ai_entry.py health
```

### Test Vertex AI Deployment

```bash
python test_vertex_ai.py \
    --endpoint-id=YOUR_ENDPOINT_ID \
    --project-id=YOUR_PROJECT_ID \
    --location=us-central1 \
    --vendor-id=VENDOR_001 \
    --max-depth=2
```

## 📊 Monitoring

### View Endpoint Status

```bash
gcloud ai endpoints describe ENDPOINT_ID \
    --region=us-central1 \
    --project=YOUR_PROJECT_ID
```

### View Logs

```bash
# Cloud Logging
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" \
    --limit=50 \
    --format=json
```

### View Metrics

Visit [Vertex AI Console](https://console.cloud.google.com/vertex-ai) to view:
- Request latency
- Error rates
- Traffic patterns
- Resource utilization

## 🔄 Updating Deployment

### Update Model Version

1. Build new image with new tag:
   ```bash
   docker build -t $IMAGE_URI:v2 -f Dockerfile .
   docker push $IMAGE_URI:v2
   ```

2. Upload new model version:
   ```bash
   gcloud ai models upload \
       --region=$REGION \
       --container-image-uri=$IMAGE_URI:v2 \
       ...
   ```

3. Deploy to endpoint with traffic split:
   ```bash
   gcloud ai endpoints deploy-model $ENDPOINT_ID \
       --model=NEW_MODEL_ID \
       --traffic-split=50 \
       ...
   ```

### Rollback

```bash
# Set traffic to 0% for new version
gcloud ai endpoints update $ENDPOINT_ID \
    --region=$REGION \
    --traffic-split=OLD_MODEL_ID=100,NEW_MODEL_ID=0
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Vertex AI Endpoint                      │
│  ┌───────────────────────────────────────────┐  │
│  │  Guardian AI v2 Container                 │  │
│  │  ┌─────────────────────────────────────┐ │  │
│  │  │  OrchestratorAgent                  │ │  │
│  │  │  ┌──────────┐  ┌──────────┐        │ │  │
│  │  │  │ Simulation│  │  Impact  │        │ │  │
│  │  │  │  Agent   │→ │ Reasoning│        │ │  │
│  │  │  └──────────┘  │  Agent   │        │ │  │
│  │  │                 └─────┬────┘        │ │  │
│  │  │                       │             │ │  │
│  │  │                 ┌─────▼────┐        │ │  │
│  │  │                 │Mitigation│        │ │  │
│  │  │                 │  Agent   │        │ │  │
│  │  │                 └──────────┘        │ │  │
│  │  └─────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 🔒 Security Best Practices

1. **Use Service Accounts**: Don't use personal credentials in production
2. **Least Privilege**: Grant minimum required permissions
3. **Secrets Management**: Use Google Secret Manager for API keys
4. **Network Security**: Use VPC for private endpoints
5. **Image Scanning**: Enable Artifact Registry vulnerability scanning

## 💰 Cost Optimization

1. **Auto-scaling**: Configure min/max replicas based on traffic
2. **Machine Types**: Use appropriate machine types (n1-standard-2 for dev)
3. **Traffic Splitting**: Use for A/B testing without full deployment
4. **Monitoring**: Set up alerts for unexpected costs

## 🐛 Troubleshooting

### Build Failures

```bash
# Check Docker is running
docker ps

# Check gcloud authentication
gcloud auth list

# Check Artifact Registry permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

### Deployment Failures

```bash
# Check model upload status
gcloud ai models list --region=us-central1

# Check endpoint status
gcloud ai endpoints list --region=us-central1

# View detailed logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Model" --limit=20
```

### Prediction Errors

```bash
# Test locally first
python vertex_ai_entry.py test

# Check container logs
gcloud ai endpoints describe ENDPOINT_ID --region=us-central1

# Verify environment variables
gcloud ai models describe MODEL_ID --region=us-central1
```

## 📚 Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/adk)
- [Artifact Registry Guide](https://cloud.google.com/artifact-registry/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## ✅ Deployment Checklist

- [ ] Environment variables configured in `.env`
- [ ] Google Cloud authentication set up
- [ ] Required APIs enabled
- [ ] Docker image built successfully
- [ ] Image pushed to Artifact Registry
- [ ] Model uploaded to Vertex AI
- [ ] Endpoint created
- [ ] Model deployed to endpoint
- [ ] Test prediction successful
- [ ] Monitoring configured
- [ ] Documentation updated

## 🎯 Next Steps

After successful deployment:

1. **Set up monitoring** alerts
2. **Configure auto-scaling** based on traffic
3. **Create CI/CD pipeline** for automated deployments
4. **Set up staging environment** for testing
5. **Document API usage** for your team

---

**Need Help?** Check the [README.md](README.md) or open an issue.

