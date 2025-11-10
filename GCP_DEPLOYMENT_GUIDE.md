# Google Cloud Platform Deployment Guide

This guide walks you through deploying the Suna backend to Google Cloud Platform (GCP) and the frontend to Vercel.

## Architecture

```
Frontend (Vercel)  →  Cloud Run (API)  →  Cloud Memorystore (Redis)
                      Cloud Run (Worker) ↗
                             ↓
                        Supabase
```

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **Vercel Account** for frontend deployment
4. **Supabase Project** (cloud or self-hosted)

## Cost Estimate (Monthly)

- **Cloud Run (API)**: ~$10-50 (depending on traffic)
- **Cloud Run (Worker)**: ~$30-100 (runs continuously)
- **Cloud Memorystore Redis (Basic, 1GB)**: ~$30
- **Total**: ~$70-180/month for moderate usage

You can reduce costs by:
- Using smaller Redis instance
- Reducing min instances to 0 for API (cold starts)
- Using Cloud Run's free tier (2 million requests/month)

## Step-by-Step Deployment

### Part 1: Deploy Backend to Google Cloud

#### Option A: Automated Deployment (Recommended)

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Set your GCP project ID**:
   ```bash
   export GCP_PROJECT_ID="your-gcp-project-id"
   export GCP_REGION="us-central1"  # Optional, defaults to us-central1
   ```

3. **Run the deployment script**:
   ```bash
   ./deploy-gcp.sh
   ```

4. **Follow the prompts**:
   - The script will enable necessary APIs
   - Create VPC connector
   - Create Redis instance
   - Prompt you to create secrets
   - Deploy both API and Worker services

#### Option B: Manual Deployment

<details>
<summary>Click to expand manual deployment steps</summary>

1. **Enable Required APIs**:
   ```bash
   gcloud services enable run.googleapis.com \
     vpcaccess.googleapis.com \
     redis.googleapis.com \
     secretmanager.googleapis.com \
     cloudbuild.googleapis.com
   ```

2. **Create VPC Connector** (for Cloud Run to access Redis):
   ```bash
   gcloud compute networks vpc-access connectors create suna-vpc-connector \
     --region=us-central1 \
     --network=default \
     --range=10.8.0.0/28 \
     --min-instances=2 \
     --max-instances=10
   ```

3. **Create Cloud Memorystore Redis Instance**:
   ```bash
   gcloud redis instances create suna-redis \
     --region=us-central1 \
     --tier=BASIC \
     --size=1 \
     --network=default \
     --redis-version=redis_7_0
   ```

4. **Get Redis Connection Details**:
   ```bash
   REDIS_HOST=$(gcloud redis instances describe suna-redis --region=us-central1 --format="value(host)")
   REDIS_PORT=$(gcloud redis instances describe suna-redis --region=us-central1 --format="value(port)")
   echo "Redis Host: $REDIS_HOST"
   echo "Redis Port: $REDIS_PORT"
   ```

5. **Create Secrets in Secret Manager**:
   ```bash
   # Supabase credentials
   echo -n "your-supabase-url" | gcloud secrets create SUPABASE_URL --data-file=-
   echo -n "your-supabase-key" | gcloud secrets create SUPABASE_KEY --data-file=-
   
   # AI API keys
   echo -n "your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
   echo -n "your-anthropic-key" | gcloud secrets create ANTHROPIC_API_KEY --data-file=-
   
   # Add any other secrets from your .env file
   ```

6. **Build Docker Image**:
   ```bash
   cd backend
   gcloud builds submit --tag gcr.io/PROJECT_ID/suna-backend
   ```

7. **Deploy API Service**:
   ```bash
   gcloud run deploy suna-api \
     --image gcr.io/PROJECT_ID/suna-backend \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --port=8000 \
     --memory=2Gi \
     --cpu=2 \
     --timeout=300 \
     --max-instances=10 \
     --min-instances=1 \
     --vpc-connector=suna-vpc-connector \
     --set-env-vars="ENV_MODE=production,REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT" \
     --set-secrets="SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest"
   ```

8. **Deploy Worker Service**:
   ```bash
   gcloud run deploy suna-worker \
     --image gcr.io/PROJECT_ID/suna-backend \
     --region=us-central1 \
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
     --set-env-vars="ENV_MODE=production,REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT" \
     --set-secrets="SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest"
   ```

9. **Get the API URL**:
   ```bash
   gcloud run services describe suna-api --region=us-central1 --format="value(status.url)"
   ```

</details>

### Part 2: Update Backend CORS

After deployment, you need to add your frontend URL to the CORS configuration.

1. **Edit** `backend/api.py` around line 139-157
2. **Add your frontend URL** to the `allowed_origins` list:
   ```python
   allowed_origins = [
       "https://www.kortix.com",
       "https://kortix.com",
       "https://www.suna.so",
       "https://suna.so",
       "https://your-frontend.vercel.app",  # Add this
   ]
   ```
3. **Redeploy** the backend:
   ```bash
   cd backend
   gcloud builds submit --tag gcr.io/PROJECT_ID/suna-backend
   gcloud run services update suna-api --region=us-central1 --image gcr.io/PROJECT_ID/suna-backend
   ```

### Part 3: Deploy Frontend to Vercel

#### Option A: Via Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"New Project"**
3. Import your GitHub repository
4. Configure project settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Install Command**: `npm install`

5. Add environment variables:
   ```env
   NEXT_PUBLIC_BACKEND_URL=https://your-api-url.run.app/api
   NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   NEXT_PUBLIC_URL=https://your-frontend.vercel.app
   NEXT_PUBLIC_ENV_MODE=PRODUCTION
   ```

6. Click **"Deploy"**

#### Option B: Via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

3. **Login to Vercel**:
   ```bash
   vercel login
   ```

4. **Deploy**:
   ```bash
   vercel --prod
   ```

5. **Add environment variables** via the dashboard or CLI:
   ```bash
   vercel env add NEXT_PUBLIC_BACKEND_URL production
   # Enter: https://your-api-url.run.app/api
   
   vercel env add NEXT_PUBLIC_SUPABASE_URL production
   # Enter: your-supabase-url
   
   # ... repeat for other environment variables
   ```

6. **Redeploy** after adding env vars:
   ```bash
   vercel --prod
   ```

## Monitoring & Logs

### View API Logs
```bash
gcloud run services logs tail suna-api --region=us-central1 --project=PROJECT_ID
```

### View Worker Logs
```bash
gcloud run services logs tail suna-worker --region=us-central1 --project=PROJECT_ID
```

### View Redis Metrics
```bash
gcloud redis instances describe suna-redis --region=us-central1
```

### Cloud Console URLs
- **Cloud Run Services**: https://console.cloud.google.com/run
- **Cloud Memorystore**: https://console.cloud.google.com/memorystore
- **Secret Manager**: https://console.cloud.google.com/security/secret-manager
- **Logs Explorer**: https://console.cloud.google.com/logs

## Continuous Deployment

### Set Up Automated Deployments with Cloud Build

1. **Create a Cloud Build trigger**:
   ```bash
   gcloud builds triggers create github \
     --name="suna-backend-deploy" \
     --repo-name="YOUR_REPO_NAME" \
     --repo-owner="YOUR_GITHUB_USERNAME" \
     --branch-pattern="^main$" \
     --build-config="backend/cloudbuild.yaml"
   ```

2. **Connect your GitHub repository** via the [Cloud Build Console](https://console.cloud.google.com/cloud-build/triggers)

3. Now every push to `main` will automatically deploy your backend!

## Troubleshooting

### Issue: "VPC connector not ready"
**Solution**: Wait a few minutes for the VPC connector to become ready, then retry deployment.

### Issue: "Permission denied" errors
**Solution**: Grant Cloud Run access to secrets:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Issue: Cold starts on API
**Solution**: Keep min-instances at 1 or use [Cloud Scheduler](https://cloud.google.com/scheduler) to ping your API every 5 minutes.

### Issue: Worker not processing jobs
**Solution**: Check that:
1. Redis is accessible from Cloud Run (check VPC connector)
2. Worker logs show it's connecting to Redis
3. Both services use the same Redis instance

### Issue: CORS errors
**Solution**: Make sure your frontend URL is in the `allowed_origins` list in `backend/api.py`.

## Scaling & Optimization

### Cost Optimization
- Set `--min-instances=0` for API if you can tolerate cold starts
- Use Cloud Scheduler to keep services warm during business hours
- Monitor Redis usage and downgrade if needed

### Performance Optimization
- Increase `--cpu` and `--memory` for better performance
- Use multiple regions for global deployment
- Enable Cloud CDN for static assets

### High Availability
- Deploy to multiple regions
- Use Cloud Load Balancing
- Set up uptime monitoring with Cloud Monitoring

## Rolling Back

If something goes wrong, you can quickly roll back:

```bash
# List revisions
gcloud run revisions list --service=suna-api --region=us-central1

# Roll back to previous revision
gcloud run services update-traffic suna-api \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

## Cleanup (If You Want to Remove Everything)

```bash
# Delete Cloud Run services
gcloud run services delete suna-api --region=us-central1
gcloud run services delete suna-worker --region=us-central1

# Delete Redis instance
gcloud redis instances delete suna-redis --region=us-central1

# Delete VPC connector
gcloud compute networks vpc-access connectors delete suna-vpc-connector --region=us-central1

# Delete secrets
gcloud secrets delete SUPABASE_URL
gcloud secrets delete SUPABASE_KEY
gcloud secrets delete OPENAI_API_KEY
gcloud secrets delete ANTHROPIC_API_KEY
```

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Memorystore Documentation](https://cloud.google.com/memorystore/docs/redis)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Vercel Documentation](https://vercel.com/docs)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Cloud Run logs
3. Check Redis connectivity from Cloud Run
4. Verify all secrets are created and accessible

