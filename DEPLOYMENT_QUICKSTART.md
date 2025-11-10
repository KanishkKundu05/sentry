# Deployment Quick Start Guide

This is a quick reference for deploying Suna to production. For detailed instructions, see [GCP_DEPLOYMENT_GUIDE.md](./GCP_DEPLOYMENT_GUIDE.md).

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│  Supabase   │
│  (Vercel)   │      │ (Cloud Run)  │      │  (Cloud)    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Redis     │
                     │(Memorystore) │
                     └──────────────┘
                            ▲
                            │
                     ┌──────────────┐
                     │   Worker     │
                     │ (Cloud Run)  │
                     └──────────────┘
```

## Prerequisites Checklist

- [ ] Google Cloud account with billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] Vercel account
- [ ] Supabase project set up
- [ ] All API keys ready (OpenAI, Anthropic, etc.)

## Deploy in 3 Steps

### 1️⃣ Deploy Backend to Google Cloud

```bash
# Set your project ID
export GCP_PROJECT_ID="your-gcp-project-id"

# Navigate to backend and run deployment script
cd backend
./deploy-gcp.sh
```

The script will:
- ✅ Enable required Google Cloud APIs
- ✅ Create VPC connector for networking
- ✅ Create Redis instance (Cloud Memorystore)
- ✅ Prompt you to add secrets (API keys)
- ✅ Build and deploy API and Worker services

**Time:** ~15-20 minutes (mostly waiting for resources)

**Save the API URL** that's printed at the end! You'll need it for the frontend.

### 2️⃣ Update CORS Settings

After deployment, update `backend/api.py` to allow your frontend URL:

```python
# Around line 139
allowed_origins = [
    "https://www.kortix.com",
    "https://kortix.com", 
    "https://your-frontend.vercel.app",  # Add this
]
```

Then redeploy:
```bash
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/suna-backend
gcloud run services update suna-api --region=us-central1 --image gcr.io/$GCP_PROJECT_ID/suna-backend
```

### 3️⃣ Deploy Frontend to Vercel

**Via Vercel Dashboard:**

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure:
   - **Root Directory:** `frontend`
   - **Framework:** Next.js (auto-detected)
4. Add environment variables:
   ```
   NEXT_PUBLIC_BACKEND_URL=https://your-api-url.run.app/api
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   NEXT_PUBLIC_URL=https://your-app.vercel.app
   NEXT_PUBLIC_ENV_MODE=PRODUCTION
   ```
5. Click "Deploy"

**Or via CLI:**

```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
# Then add env vars in the dashboard
```

## Verification

Test your deployment:

```bash
# Check backend health
curl https://your-api-url.run.app/api/health

# Check frontend
curl https://your-app.vercel.app
```

## Monitoring

View logs:
```bash
# API logs
gcloud run services logs tail suna-api --region=us-central1

# Worker logs  
gcloud run services logs tail suna-worker --region=us-central1
```

## Cost Estimate

**Monthly costs for moderate usage:**
- Cloud Run (API): ~$10-50
- Cloud Run (Worker): ~$30-100
- Cloud Memorystore (Redis 1GB): ~$30
- **Total: ~$70-180/month**

## Quick Commands Reference

```bash
# Deploy backend
cd backend && gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/suna-backend

# Update API service
gcloud run services update suna-api --region=us-central1 --image gcr.io/$GCP_PROJECT_ID/suna-backend

# Update Worker service
gcloud run services update suna-worker --region=us-central1 --image gcr.io/$GCP_PROJECT_ID/suna-backend

# Deploy frontend
cd frontend && vercel --prod

# View API URL
gcloud run services describe suna-api --region=us-central1 --format="value(status.url)"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "VPC connector not ready" | Wait 2-3 minutes, retry |
| Permission errors | Run: `gcloud auth login` |
| CORS errors | Add frontend URL to backend CORS config |
| Cold starts | Set `--min-instances=1` |
| Worker not processing | Check Redis connection in logs |

## Next Steps

- [ ] Set up custom domain on Vercel
- [ ] Configure Cloud Build triggers for CI/CD
- [ ] Set up monitoring alerts
- [ ] Configure backup strategy
- [ ] Test the entire flow

## Support

- **Detailed Guide:** [GCP_DEPLOYMENT_GUIDE.md](./GCP_DEPLOYMENT_GUIDE.md)
- **Google Cloud Console:** https://console.cloud.google.com
- **Vercel Dashboard:** https://vercel.com/dashboard

---

**Need help?** Check the detailed deployment guide or Google Cloud documentation.

