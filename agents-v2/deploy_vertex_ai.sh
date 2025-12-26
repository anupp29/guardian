#!/bin/bash
# Guardian AI v2 - Vertex AI Deployment Script
# This script builds and deploys the agents-v2 to Vertex AI

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    echo -e "${GREEN}Loading environment variables from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found. Using environment variables or defaults.${NC}"
fi

# Required variables
PROJECT_ID=${GCP_PROJECT_ID:-}
REGION=${GCP_REGION:-us-central1}
REPO=${GCP_ARTIFACT_REGISTRY_REPO:-guardian-ai}
LOCATION=${GCP_ARTIFACT_REGISTRY_LOCATION:-us-central1}
IMAGE_NAME=${IMAGE_NAME:-guardian-agents-v2}
IMAGE_TAG=${IMAGE_TAG:-latest}

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID is required${NC}"
    echo "Please set it in .env file or export it:"
    echo "  export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Guardian AI v2 - Vertex AI Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Image: $IMAGE_NAME:$IMAGE_TAG"
echo ""

# Step 1: Enable required APIs
echo -e "${YELLOW}Step 1: Enabling required Google Cloud APIs...${NC}"
gcloud services enable \
    aiplatform.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    --project=$PROJECT_ID

# Step 2: Create Artifact Registry repository (if it doesn't exist)
echo -e "${YELLOW}Step 2: Setting up Artifact Registry...${NC}"
if ! gcloud artifacts repositories describe $REPO \
    --location=$LOCATION \
    --project=$PROJECT_ID &>/dev/null; then
    echo "Creating Artifact Registry repository: $REPO"
    gcloud artifacts repositories create $REPO \
        --repository-format=docker \
        --location=$LOCATION \
        --description="Guardian AI v2 Docker images" \
        --project=$PROJECT_ID
else
    echo "Artifact Registry repository already exists"
fi

# Step 3: Configure Docker authentication
echo -e "${YELLOW}Step 3: Configuring Docker authentication...${NC}"
gcloud auth configure-docker ${LOCATION}-docker.pkg.dev --quiet

# Step 4: Build Docker image
echo -e "${YELLOW}Step 4: Building Docker image...${NC}"
IMAGE_URI="${LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t $IMAGE_URI -f Dockerfile .

# Step 5: Push image to Artifact Registry
echo -e "${YELLOW}Step 5: Pushing image to Artifact Registry...${NC}"
docker push $IMAGE_URI

# Step 6: Create Vertex AI Model (if it doesn't exist)
echo -e "${YELLOW}Step 6: Creating Vertex AI Model...${NC}"
MODEL_NAME="guardian-agents-v2"
MODEL_DISPLAY_NAME="Guardian AI v2 Multi-Agent System"

# Check if model already exists
if gcloud ai models list \
    --region=$REGION \
    --project=$PROJECT_ID \
    --filter="displayName:$MODEL_DISPLAY_NAME" \
    --format="value(name)" | grep -q .; then
    echo "Model already exists, skipping creation"
    MODEL_ID=$(gcloud ai models list \
        --region=$REGION \
        --project=$PROJECT_ID \
        --filter="displayName:$MODEL_DISPLAY_NAME" \
        --format="value(name)" | head -1)
else
    echo "Creating new Vertex AI Model..."
    MODEL_ID=$(gcloud ai models upload \
        --region=$REGION \
        --project=$PROJECT_ID \
        --display-name="$MODEL_DISPLAY_NAME" \
        --container-image-uri=$IMAGE_URI \
    --container-ports=3000 \
    --container-health-route=/health \
    --container-predict-route=/predict \
        --format="value(name)")
fi

echo "Model ID: $MODEL_ID"

# Step 7: Deploy model to endpoint
echo -e "${YELLOW}Step 7: Deploying model to Vertex AI Endpoint...${NC}"
ENDPOINT_NAME="guardian-agents-v2-endpoint"
ENDPOINT_DISPLAY_NAME="Guardian AI v2 Endpoint"

# Check if endpoint exists
ENDPOINT_ID=$(gcloud ai endpoints list \
    --region=$REGION \
    --project=$PROJECT_ID \
    --filter="displayName:$ENDPOINT_DISPLAY_NAME" \
    --format="value(name)" | head -1)

if [ -z "$ENDPOINT_ID" ]; then
    echo "Creating new endpoint..."
    ENDPOINT_ID=$(gcloud ai endpoints create \
        --region=$REGION \
        --project=$PROJECT_ID \
        --display-name="$ENDPOINT_DISPLAY_NAME" \
        --format="value(name)")
    echo "Created endpoint: $ENDPOINT_ID"
else
    echo "Using existing endpoint: $ENDPOINT_ID"
fi

# Deploy model to endpoint
MACHINE_TYPE=${VERTEX_AI_MACHINE_TYPE:-n1-standard-4}
MIN_REPLICAS=${VERTEX_AI_MIN_REPLICAS:-1}
MAX_REPLICAS=${VERTEX_AI_MAX_REPLICAS:-3}

echo "Deploying model to endpoint..."
gcloud ai endpoints deploy-model $ENDPOINT_ID \
    --region=$REGION \
    --project=$PROJECT_ID \
    --model=$MODEL_ID \
    --display-name="$MODEL_DISPLAY_NAME" \
    --machine-type=$MACHINE_TYPE \
    --min-replica-count=$MIN_REPLICAS \
    --max-replica-count=$MAX_REPLICAS \
    --traffic-split=100

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Model ID: $MODEL_ID"
echo "Endpoint ID: $ENDPOINT_ID"
echo "Image URI: $IMAGE_URI"
echo ""
echo "To test the deployment, use:"
echo "  python test_vertex_ai.py --endpoint-id=$ENDPOINT_ID --region=$REGION"
echo ""
echo "To view logs:"
echo "  gcloud ai endpoints describe $ENDPOINT_ID --region=$REGION --project=$PROJECT_ID"
echo ""

