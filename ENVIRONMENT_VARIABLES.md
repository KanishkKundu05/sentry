# Environment Variables Reference

This document lists all environment variables needed for production deployment.

## Backend (Google Cloud Run)

These should be added as **Secrets** in Google Cloud Secret Manager:

### Required Secrets

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-key

# AI API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Add any additional secrets your backend needs
```

### Environment Variables (Non-Secret)

These are set directly in Cloud Run:

```bash
ENV_MODE=production
REDIS_HOST=10.0.0.3              # Automatically set by deployment script
REDIS_PORT=6379                  # Default Redis port
REDIS_PASSWORD=                  # Empty for Memorystore basic tier
REDIS_SSL=False                  # Memorystore doesn't use SSL by default
```

### How to Create Secrets

```bash
# One-time setup
echo -n "your-supabase-url" | gcloud secrets create SUPABASE_URL --data-file=-
echo -n "your-supabase-key" | gcloud secrets create SUPABASE_KEY --data-file=-
echo -n "your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "your-anthropic-key" | gcloud secrets create ANTHROPIC_API_KEY --data-file=-
```

### How to Update Secrets

```bash
echo -n "new-value" | gcloud secrets versions add SUPABASE_URL --data-file=-
```

## Frontend (Vercel)

These should be added in **Vercel Project Settings → Environment Variables**:

### Required Environment Variables

```bash
# Backend API - URL from Cloud Run deployment
NEXT_PUBLIC_BACKEND_URL=https://suna-api-xxxxx-uc.a.run.app/api

# Supabase (same as backend)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Frontend URL (your Vercel deployment URL)
NEXT_PUBLIC_URL=https://your-app.vercel.app

# Environment mode
NEXT_PUBLIC_ENV_MODE=PRODUCTION
```

### How to Add in Vercel Dashboard

1. Go to your project in Vercel
2. Navigate to **Settings → Environment Variables**
3. Add each variable:
   - **Name:** `NEXT_PUBLIC_BACKEND_URL`
   - **Value:** `https://your-api-url.run.app/api`
   - **Environment:** Production
4. Repeat for all variables above

### How to Add via Vercel CLI

```bash
vercel env add NEXT_PUBLIC_BACKEND_URL production
# Then paste the value when prompted

vercel env add NEXT_PUBLIC_SUPABASE_URL production
# ... repeat for each variable
```

## Optional Environment Variables

### Backend (if needed)

```bash
# Email service (if using)
SENDGRID_API_KEY=SG.xxx
EMAIL_FROM=noreply@yourdomain.com

# Stripe (if using billing)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Other AI providers (if using)
GOOGLE_API_KEY=xxx
TOGETHER_API_KEY=xxx

# Sentry (error tracking)
SENTRY_DSN=https://xxx@sentry.io/xxx

# Monitoring
LOG_LEVEL=INFO
```

### Frontend (if needed)

```bash
# Analytics
NEXT_PUBLIC_POSTHOG_KEY=phc_xxx
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com

# Sentry
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx

# Feature flags
NEXT_PUBLIC_FEATURE_XYZ=true
```

## Verification Checklist

After setting all environment variables, verify:

### Backend
```bash
# SSH into Cloud Run (for debugging)
gcloud run services describe suna-api --region=us-central1

# Check if secrets are mounted correctly
gcloud run services describe suna-api --region=us-central1 --format="value(spec.template.spec.containers[0].env)"
```

### Frontend
```bash
# In your browser console (after deployment):
console.log(process.env.NEXT_PUBLIC_BACKEND_URL)

# Should show your Cloud Run URL
```

## Security Best Practices

### ✅ DO
- Use Secret Manager for sensitive data
- Rotate API keys regularly
- Use different keys for staging/production
- Set appropriate IAM permissions
- Use HTTPS everywhere

### ❌ DON'T
- Commit `.env` files to git
- Share secrets in plain text
- Use the same keys across environments
- Expose service role keys in frontend
- Store secrets in environment variables (use Secret Manager)

## Environment-Specific Configurations

### Development (Local)
```bash
# backend/.env
ENV_MODE=LOCAL
REDIS_HOST=localhost
REDIS_PORT=6379

# frontend/.env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000/api
NEXT_PUBLIC_URL=http://localhost:3000
NEXT_PUBLIC_ENV_MODE=LOCAL
```

### Staging (Optional)
```bash
# Backend
ENV_MODE=STAGING

# Frontend  
NEXT_PUBLIC_ENV_MODE=STAGING
NEXT_PUBLIC_BACKEND_URL=https://suna-api-staging-xxx.run.app/api
```

### Production
```bash
# Backend
ENV_MODE=production

# Frontend
NEXT_PUBLIC_ENV_MODE=PRODUCTION
NEXT_PUBLIC_BACKEND_URL=https://suna-api-xxx.run.app/api
```

## Troubleshooting

### Issue: "Secret not found"
```bash
# List all secrets
gcloud secrets list

# Check secret access
gcloud secrets get-iam-policy SECRET_NAME
```

### Issue: "Frontend can't connect to backend"
- Verify `NEXT_PUBLIC_BACKEND_URL` ends with `/api`
- Check CORS settings in `backend/api.py`
- Ensure backend is deployed and healthy

### Issue: "Database connection failed"
- Verify Supabase credentials
- Check if Supabase project is active
- Ensure service role key is used in backend

## Quick Reference Commands

```bash
# List all Google Cloud secrets
gcloud secrets list

# View Vercel environment variables
vercel env ls

# Pull environment variables from Vercel (for local testing)
vercel env pull .env.local

# Test backend health
curl https://your-api-url.run.app/api/health

# Test frontend (should return HTML)
curl https://your-app.vercel.app
```

