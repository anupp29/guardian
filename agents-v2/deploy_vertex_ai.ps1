# Guardian AI v2 - Vertex AI Deployment Script (PowerShell)
# This script builds and deploys the agents-v2 to Vertex AI

$ErrorActionPreference = "Stop"

# Load environment variables from .env file
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env" -ForegroundColor Green
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    Write-Host "Warning: .env file not found. Using environment variables or defaults." -ForegroundColor Yellow
}

# Required variables
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "" }
$REGION = if ($env:GCP_REGION) { $env:GCP_REGION } else { "us-central1" }
$REPO = if ($env:GCP_ARTIFACT_REGISTRY_REPO) { $env:GCP_ARTIFACT_REGISTRY_REPO } else { "guardian-ai" }
$LOCATION = if ($env:GCP_ARTIFACT_REGISTRY_LOCATION) { $env:GCP_ARTIFACT_REGISTRY_LOCATION } else { "us-central1" }
$IMAGE_NAME = if ($env:IMAGE_NAME) { $env:IMAGE_NAME } else { "guardian-agents-v2" }
$IMAGE_TAG = if ($env:IMAGE_TAG) { $env:IMAGE_TAG } else { "latest" }

if (-not $PROJECT_ID) {
    Write-Host "Error: GCP_PROJECT_ID is required" -ForegroundColor Red
    Write-Host "Please set it in .env file or as environment variable:"
    Write-Host "  `$env:GCP_PROJECT_ID = 'your-project-id'"
    exit 1
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "Guardian AI v2 - Vertex AI Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Project ID: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Image: $IMAGE_NAME`:$IMAGE_TAG"
Write-Host ""

# Step 1: Enable required APIs
Write-Host "Step 1: Enabling required Google Cloud APIs..." -ForegroundColor Yellow
gcloud services enable `
    aiplatform.googleapis.com `
    artifactregistry.googleapis.com `
    cloudbuild.googleapis.com `
    containerregistry.googleapis.com `
    --project=$PROJECT_ID

# Step 2: Create Artifact Registry repository
Write-Host "Step 2: Setting up Artifact Registry..." -ForegroundColor Yellow
$repoExists = gcloud artifacts repositories describe $REPO `
    --location=$LOCATION `
    --project=$PROJECT_ID `
    2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating Artifact Registry repository: $REPO"
    gcloud artifacts repositories create $REPO `
        --repository-format=docker `
        --location=$LOCATION `
        --description="Guardian AI v2 Docker images" `
        --project=$PROJECT_ID
} else {
    Write-Host "Artifact Registry repository already exists"
}

# Step 3: Configure Docker authentication
Write-Host "Step 3: Configuring Docker authentication..." -ForegroundColor Yellow
gcloud auth configure-docker "${LOCATION}-docker.pkg.dev" --quiet

# Step 4: Build Docker image
Write-Host "Step 4: Building Docker image..." -ForegroundColor Yellow
$IMAGE_URI = "${LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t $IMAGE_URI -f Dockerfile .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

# Step 5: Push image to Artifact Registry
Write-Host "Step 5: Pushing image to Artifact Registry..." -ForegroundColor Yellow
docker push $IMAGE_URI

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push failed!" -ForegroundColor Red
    exit 1
}

# Step 6: Create Vertex AI Model
Write-Host "Step 6: Creating Vertex AI Model..." -ForegroundColor Yellow
$MODEL_NAME = "guardian-agents-v2"
$MODEL_DISPLAY_NAME = "Guardian AI v2 Multi-Agent System"

# Check if model exists
$existingModel = gcloud ai models list `
    --region=$REGION `
    --project=$PROJECT_ID `
    --filter="displayName:$MODEL_DISPLAY_NAME" `
    --format="value(name)" | Select-Object -First 1

if ($existingModel) {
    Write-Host "Model already exists, using existing model"
    $MODEL_ID = $existingModel
} else {
    Write-Host "Creating new Vertex AI Model..."
    $MODEL_ID = gcloud ai models upload `
        --region=$REGION `
        --project=$PROJECT_ID `
        --display-name="$MODEL_DISPLAY_NAME" `
        --container-image-uri=$IMAGE_URI `
        --container-ports=3000 `
        --container-health-route=/health `
        --container-predict-route=/predict `
        --format="value(name)"
}

Write-Host "Model ID: $MODEL_ID"

# Step 7: Deploy model to endpoint
Write-Host "Step 7: Deploying model to Vertex AI Endpoint..." -ForegroundColor Yellow
$ENDPOINT_NAME = "guardian-agents-v2-endpoint"
$ENDPOINT_DISPLAY_NAME = "Guardian AI v2 Endpoint"

# Check if endpoint exists
$ENDPOINT_ID = gcloud ai endpoints list `
    --region=$REGION `
    --project=$PROJECT_ID `
    --filter="displayName:$ENDPOINT_DISPLAY_NAME" `
    --format="value(name)" | Select-Object -First 1

if (-not $ENDPOINT_ID) {
    Write-Host "Creating new endpoint..."
    $ENDPOINT_ID = gcloud ai endpoints create `
        --region=$REGION `
        --project=$PROJECT_ID `
        --display-name="$ENDPOINT_DISPLAY_NAME" `
        --format="value(name)"
    Write-Host "Created endpoint: $ENDPOINT_ID"
} else {
    Write-Host "Using existing endpoint: $ENDPOINT_ID"
}

# Deploy model to endpoint
$MACHINE_TYPE = if ($env:VERTEX_AI_MACHINE_TYPE) { $env:VERTEX_AI_MACHINE_TYPE } else { "n1-standard-4" }
$MIN_REPLICAS = if ($env:VERTEX_AI_MIN_REPLICAS) { $env:VERTEX_AI_MIN_REPLICAS } else { "1" }
$MAX_REPLICAS = if ($env:VERTEX_AI_MAX_REPLICAS) { $env:VERTEX_AI_MAX_REPLICAS } else { "3" }

Write-Host "Deploying model to endpoint..."
gcloud ai endpoints deploy-model $ENDPOINT_ID `
    --region=$REGION `
    --project=$PROJECT_ID `
    --model=$MODEL_ID `
    --display-name="$MODEL_DISPLAY_NAME" `
    --machine-type=$MACHINE_TYPE `
    --min-replica-count=$MIN_REPLICAS `
    --max-replica-count=$MAX_REPLICAS `
    --traffic-split=100

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Model ID: $MODEL_ID"
Write-Host "Endpoint ID: $ENDPOINT_ID"
Write-Host "Image URI: $IMAGE_URI"
Write-Host ""
Write-Host "To test the deployment, use:"
Write-Host "  python test_vertex_ai.py --endpoint-id=$ENDPOINT_ID --region=$REGION"
Write-Host ""

