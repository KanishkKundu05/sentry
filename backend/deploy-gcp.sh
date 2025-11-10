#!/bin/bash

# ============================================================================
# Suna Backend - Google Cloud Platform Deployment Script
# ============================================================================
# This script helps deploy the Suna backend to Google Cloud Platform
# It sets up Cloud Run services, Cloud Memorystore (Redis), and networking
# ============================================================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - EDIT THESE VALUES
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
REGION="${GCP_REGION:-us-central1}"
REDIS_TIER="${REDIS_TIER:-BASIC}"
REDIS_MEMORY="${REDIS_MEMORY:-1}"

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Suna Backend - Google Cloud Deployment      ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✓ gcloud CLI found${NC}"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated. Running gcloud auth login...${NC}"
    gcloud auth login
fi

echo -e "${GREEN}✓ Authenticated${NC}"

# Set project
echo -e "${YELLOW}Setting project to: ${PROJECT_ID}${NC}"
gcloud config set project "$PROJECT_ID"

echo ""
echo -e "${BLUE}=== Step 1: Enable Required APIs ===${NC}"
echo "Enabling Cloud Run, VPC, Memorystore, Secret Manager, and Cloud Build APIs..."

gcloud services enable \
    run.googleapis.com \
    vpcaccess.googleapis.com \
    redis.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com

echo -e "${GREEN}✓ APIs enabled${NC}"

echo ""
echo -e "${BLUE}=== Step 2: Create VPC Connector ===${NC}"
echo "Creating VPC connector for Cloud Run to access Redis..."

# Check if connector already exists
if gcloud compute networks vpc-access connectors describe suna-vpc-connector --region="$REGION" &> /dev/null; then
    echo -e "${YELLOW}VPC connector 'suna-vpc-connector' already exists${NC}"
else
    gcloud compute networks vpc-access connectors create suna-vpc-connector \
        --region="$REGION" \
        --network=default \
        --range=10.8.0.0/28 \
        --min-instances=2 \
        --max-instances=10
    
    echo -e "${GREEN}✓ VPC connector created${NC}"
fi

echo ""
echo -e "${BLUE}=== Step 3: Create Cloud Memorystore (Redis) ===${NC}"
echo "Creating Redis instance (this may take 5-10 minutes)..."

# Check if Redis instance already exists
if gcloud redis instances describe suna-redis --region="$REGION" &> /dev/null; then
    echo -e "${YELLOW}Redis instance 'suna-redis' already exists${NC}"
    REDIS_HOST=$(gcloud redis instances describe suna-redis --region="$REGION" --format="value(host)")
    REDIS_PORT=$(gcloud redis instances describe suna-redis --region="$REGION" --format="value(port)")
else
    gcloud redis instances create suna-redis \
        --region="$REGION" \
        --tier="$REDIS_TIER" \
        --size="$REDIS_MEMORY" \
        --network=default \
        --redis-version=redis_7_0
    
    echo -e "${GREEN}✓ Redis instance created${NC}"
    
    # Get Redis connection details
    REDIS_HOST=$(gcloud redis instances describe suna-redis --region="$REGION" --format="value(host)")
    REDIS_PORT=$(gcloud redis instances describe suna-redis --region="$REGION" --format="value(port)")
fi

echo -e "${GREEN}Redis Host: ${REDIS_HOST}${NC}"
echo -e "${GREEN}Redis Port: ${REDIS_PORT}${NC}"

echo ""
echo -e "${BLUE}=== Step 4: Create Secrets in Secret Manager ===${NC}"
echo "Checking which secrets need to be created..."

# Function to create secret if it doesn't exist
create_secret_if_missing() {
    local secret_name=$1
    local secret_description=$2
    
    if gcloud secrets describe "$secret_name" &> /dev/null; then
        echo -e "${YELLOW}Secret '$secret_name' already exists - skipping${NC}"
        return 0
    else
        echo ""
        echo -e "${GREEN}Creating secret: $secret_name${NC}"
        echo -e "${YELLOW}$secret_description${NC}"
        echo -e "${BLUE}Enter value (input hidden for security):${NC}"
        read -s secret_value
        echo ""
        
        if [ -z "$secret_value" ]; then
            echo -e "${RED}Error: Empty value provided. Skipping $secret_name${NC}"
            return 1
        fi
        
        echo -n "$secret_value" | gcloud secrets create "$secret_name" --data-file=-
        echo -e "${GREEN}✓ Secret '$secret_name' created${NC}"
        echo ""
    fi
}

# Create required secrets
create_secret_if_missing "SUPABASE_URL" "Your Supabase URL (e.g., https://xxx.supabase.co)"
create_secret_if_missing "SUPABASE_SERVICE_ROLE_KEY" "Your Supabase SERVICE ROLE key (starts with eyJ...)"
create_secret_if_missing "SUPABASE_ANON_KEY" "Your Supabase ANON key (starts with eyJ...)"
create_secret_if_missing "SUPABASE_JWT_SECRET" "Your Supabase JWT secret"
create_secret_if_missing "OPENAI_API_KEY" "Your OpenAI API key (starts with sk-...)"
create_secret_if_missing "ANTHROPIC_API_KEY" "Your Anthropic API key (starts with sk-ant-...)"

echo -e "${GREEN}✓ All secrets configured${NC}"

echo ""
echo -e "${BLUE}=== Step 5: Grant Secret Access Permissions ===${NC}"
echo "Granting Cloud Run service account access to secrets..."

# Get the project number
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Service Account: $SERVICE_ACCOUNT"

# Grant secret accessor role to the compute service account for each secret
for SECRET_NAME in SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY SUPABASE_ANON_KEY SUPABASE_JWT_SECRET OPENAI_API_KEY ANTHROPIC_API_KEY; do
    if gcloud secrets describe "$SECRET_NAME" &> /dev/null; then
        echo "Granting access to $SECRET_NAME..."
        gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/secretmanager.secretAccessor" \
            --quiet &> /dev/null || true
    fi
done

echo -e "${GREEN}✓ Permissions granted${NC}"

echo ""
echo -e "${BLUE}=== Step 6: Build and Deploy Services ===${NC}"
echo "Building Docker image and deploying to Cloud Run..."

# Build the Docker image
echo "Building Docker image..."
gcloud builds submit --tag gcr.io/"$PROJECT_ID"/suna-backend

# Deploy API
echo "Deploying API service..."
gcloud run deploy suna-api \
    --image gcr.io/"$PROJECT_ID"/suna-backend \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --port=8000 \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1 \
    --vpc-connector=suna-vpc-connector \
    --no-cpu-throttling \
    --startup-cpu-boost \
    --set-env-vars="ENV_MODE=production,REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT,REDIS_PASSWORD=,REDIS_SSL=False" \
    --set-secrets="SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest,SUPABASE_JWT_SECRET=SUPABASE_JWT_SECRET:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest"

# Get API URL
API_URL=$(gcloud run services describe suna-api --region="$REGION" --format="value(status.url)")
echo -e "${GREEN}✓ API deployed at: ${API_URL}${NC}"

# Deploy Worker
echo "Deploying Worker service..."
gcloud run deploy suna-worker \
    --image gcr.io/"$PROJECT_ID"/suna-backend \
    --region="$REGION" \
    --platform=managed \
    --no-allow-unauthenticated \
    --memory=4Gi \
    --cpu=4 \
    --timeout=3600 \
    --max-instances=5 \
    --min-instances=1 \
    --vpc-connector=suna-vpc-connector \
    --command="uv" \
    --args="run,dramatiq,--skip-logging,--processes,4,--threads,4,run_agent_background" \
    --set-env-vars="ENV_MODE=production,REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT,REDIS_PASSWORD=,REDIS_SSL=False" \
    --set-secrets="SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest,SUPABASE_JWT_SECRET=SUPABASE_JWT_SECRET:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest"

echo -e "${GREEN}✓ Worker deployed${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Deployment Complete! 🎉               ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${BLUE}Backend API URL:${NC} ${API_URL}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update your frontend's NEXT_PUBLIC_BACKEND_URL to: ${API_URL}/api"
echo "2. Add your frontend URL to CORS in backend/api.py"
echo "3. Deploy your frontend to Vercel"
echo ""
echo -e "${YELLOW}Monitor your services:${NC}"
echo "  API logs:    gcloud run services logs tail suna-api --region=$REGION"
echo "  Worker logs: gcloud run services logs tail suna-worker --region=$REGION"
echo ""


