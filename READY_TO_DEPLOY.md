# 🚀 Ready to Deploy!

Your codebase is now configured for production deployment on **Google Cloud Platform** (backend) and **Vercel** (frontend).

## What's Been Set Up

### ✅ Backend Configuration (Google Cloud)
- **`backend/deploy-gcp.sh`** - Automated deployment script
- **`backend/cloudbuild.yaml`** - Cloud Build configuration for CI/CD
- **`backend/.gcloudignore`** - Excludes unnecessary files from deployment

### ✅ Frontend Configuration (Vercel)
- **`frontend/vercel.json`** - Vercel deployment configuration

### ✅ Documentation
- **`GCP_DEPLOYMENT_GUIDE.md`** - Detailed step-by-step guide
- **`DEPLOYMENT_QUICKSTART.md`** - Quick reference (3-step process)
- **`ENVIRONMENT_VARIABLES.md`** - Complete env var reference

### ✅ Cleanup
- ❌ Removed incorrect root `vercel.json` (was configured for backend)
- ❌ Removed `.vercelignore` from root

## Your Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     PRODUCTION                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend (Vercel)                                      │
│  ├─ Next.js App                                         │
│  └─ Env: NEXT_PUBLIC_BACKEND_URL → Cloud Run           │
│                    │                                    │
│                    ▼                                    │
│  Backend (Google Cloud Run)                             │
│  ├─ API Service (FastAPI)                              │
│  ├─ Worker Service (Dramatiq)                          │
│  └─ Redis (Cloud Memorystore)                          │
│                    │                                    │
│                    ▼                                    │
│  Database (Supabase Cloud)                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Quick Start: 3 Steps to Deploy

### 1️⃣ Deploy Backend (15-20 minutes)

```bash
cd backend
export GCP_PROJECT_ID="your-gcp-project-id"
./deploy-gcp.sh
```

**What it does:**
- Creates VPC networking
- Deploys Redis (Cloud Memorystore)
- Builds Docker image
- Deploys API and Worker to Cloud Run
- Gives you the API URL

**Save the API URL!** You'll need it for step 3.

### 2️⃣ Update CORS (2 minutes)

Edit `backend/api.py` line ~155:

```python
allowed_origins = [
    "https://www.kortix.com",
    "https://kortix.com",
    "https://your-frontend.vercel.app",  # Add your Vercel URL
]
```

Redeploy:
```bash
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/suna-backend
gcloud run services update suna-api --region=us-central1 --image gcr.io/$GCP_PROJECT_ID/suna-backend
```

### 3️⃣ Deploy Frontend (5 minutes)

**Via Vercel Dashboard:**
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your repo
3. Set **Root Directory** to `frontend`
4. Add environment variables:
   - `NEXT_PUBLIC_BACKEND_URL` = `https://your-api-url.run.app/api`
   - `NEXT_PUBLIC_SUPABASE_URL` = your Supabase URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = your anon key
   - `NEXT_PUBLIC_URL` = your Vercel URL
   - `NEXT_PUBLIC_ENV_MODE` = `PRODUCTION`
5. Deploy!

**Or via CLI:**
```bash
cd frontend
vercel --prod
```

## Prerequisites

Before deploying, make sure you have:

- [ ] Google Cloud account with billing enabled
- [ ] gcloud CLI installed (`brew install --cask google-cloud-sdk`)
- [ ] gcloud authenticated (`gcloud auth login`)
- [ ] Vercel account
- [ ] Supabase project created
- [ ] API keys ready:
  - [ ] OpenAI API key
  - [ ] Anthropic API key
  - [ ] Any other service API keys

## Cost Estimate

**Monthly costs (moderate usage):**
- Cloud Run API: $10-50
- Cloud Run Worker: $30-100
- Redis (1GB Basic): ~$30
- **Total: ~$70-180/month**

Plus:
- Vercel: Free tier (or $20/month Pro)
- Supabase: Free tier (or paid plans)

## What Happens Next

### After Backend Deployment:
1. Your API will be available at: `https://suna-api-xxxxx.run.app`
2. Worker will be running in background
3. Redis will be accessible via VPC
4. All secrets will be securely stored in Secret Manager

### After Frontend Deployment:
1. Your frontend will be at: `https://your-app.vercel.app`
2. Auto-deploys on every `git push` to main
3. Preview deployments for PRs
4. Built-in analytics and monitoring

## Monitoring Your Deployment

### View Logs
```bash
# API logs
gcloud run services logs tail suna-api --region=us-central1

# Worker logs
gcloud run services logs tail suna-worker --region=us-central1
```

### Health Checks
```bash
# Backend health
curl https://your-api-url.run.app/api/health

# Should return: {"status":"ok","timestamp":"...","instance_id":"..."}
```

### Google Cloud Console
- **Cloud Run**: https://console.cloud.google.com/run
- **Memorystore (Redis)**: https://console.cloud.google.com/memorystore
- **Logs**: https://console.cloud.google.com/logs

### Vercel Dashboard
- **Deployments**: https://vercel.com/dashboard
- **Analytics**: Built-in
- **Logs**: Real-time function logs

## Troubleshooting Common Issues

| Issue | Quick Fix |
|-------|-----------|
| "gcloud: command not found" | Install gcloud CLI |
| "Project not found" | Set: `gcloud config set project PROJECT_ID` |
| "VPC connector not ready" | Wait 2-3 minutes, retry |
| CORS errors | Add frontend URL to `allowed_origins` in `backend/api.py` |
| Cold starts | Set `--min-instances=1` in Cloud Run |
| Worker not processing | Check Redis connection, view worker logs |

## Next Steps After Deployment

### Immediate
- [ ] Test the full application flow
- [ ] Verify all features work
- [ ] Check logs for errors

### Recommended
- [ ] Set up custom domain (both Vercel and Cloud Run)
- [ ] Configure Cloud Build triggers for CI/CD
- [ ] Set up monitoring alerts
- [ ] Configure backups
- [ ] Add status page monitoring

### Optional
- [ ] Set up staging environment
- [ ] Configure CDN for assets
- [ ] Add performance monitoring (Sentry, DataDog)
- [ ] Set up log aggregation
- [ ] Configure auto-scaling rules

## Support & Resources

### Documentation
- [GCP_DEPLOYMENT_GUIDE.md](./GCP_DEPLOYMENT_GUIDE.md) - Detailed guide
- [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md) - All env vars
- [DEPLOYMENT_QUICKSTART.md](./DEPLOYMENT_QUICKSTART.md) - Quick reference

### External Resources
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Supabase Docs](https://supabase.com/docs)

### Getting Help
1. Check the troubleshooting sections in the guides
2. Review Cloud Run logs
3. Check Vercel deployment logs
4. Review Supabase connection status

## Rolling Back

If something goes wrong:

```bash
# List previous Cloud Run revisions
gcloud run revisions list --service=suna-api --region=us-central1

# Roll back to previous version
gcloud run services update-traffic suna-api \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

For Vercel, just revert in the dashboard under "Deployments" → "Promote to Production".

---

## 🎉 You're Ready!

Everything is configured. Just run the deployment scripts and you'll be live in ~20 minutes!

**Questions?** Check the detailed guides or run:
```bash
# For backend help
cd backend && cat ../GCP_DEPLOYMENT_GUIDE.md

# For environment variables
cat ENVIRONMENT_VARIABLES.md
```

**Good luck with your deployment! 🚀**

