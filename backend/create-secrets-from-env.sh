#!/bin/bash

# ============================================================================
# One-time script to create GCP secrets from your .env file
# ============================================================================

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Creating GCP Secrets from .env file${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found in current directory${NC}"
    echo "Make sure you're running this from the backend/ directory"
    exit 1
fi

# Load .env file
source .env

# Function to create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_value" ]; then
        echo -e "${YELLOW}⚠️  Skipping $secret_name (not set in .env)${NC}"
        return 0
    fi
    
    # Check if secret exists
    if gcloud secrets describe "$secret_name" &> /dev/null; then
        echo -e "${YELLOW}Updating existing secret: $secret_name${NC}"
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" --data-file=-
        echo -e "${GREEN}✓ Updated $secret_name${NC}"
    else
        echo -e "${GREEN}Creating new secret: $secret_name${NC}"
        echo -n "$secret_value" | gcloud secrets create "$secret_name" --data-file=-
        echo -e "${GREEN}✓ Created $secret_name${NC}"
    fi
}

# Create all required secrets from .env
echo "Creating secrets..."
echo ""

create_or_update_secret "SUPABASE_URL" "$SUPABASE_URL"
create_or_update_secret "SUPABASE_SERVICE_ROLE_KEY" "$SUPABASE_SERVICE_ROLE_KEY"
create_or_update_secret "SUPABASE_ANON_KEY" "$SUPABASE_ANON_KEY"
create_or_update_secret "SUPABASE_JWT_SECRET" "$SUPABASE_JWT_SECRET"
create_or_update_secret "OPENAI_API_KEY" "$OPENAI_API_KEY"
create_or_update_secret "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     All secrets created successfully! ✓        ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${BLUE}You can now run ./deploy-gcp.sh to continue deployment${NC}"
echo ""

