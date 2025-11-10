# 🚀 Quick Start: Deploy to Vercel

This is a simplified guide to get your backend deployed to Vercel ASAP.

## Prerequisites

- [ ] Vercel account (sign up at https://vercel.com)
- [ ] Supabase project set up
- [ ] At least one LLM API key (Anthropic/OpenAI/etc.)

## 5-Minute Setup

### Step 1: Set Up Upstash Redis (2 minutes)

1. Go to https://upstash.com → Sign up/Login
2. Click "Create Database"
3. Choose a name and region
4. Copy these values:
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `REDIS_PASSWORD`

### Step 2: Deploy to Vercel (2 minutes)

```bash
# Install Vercel CLI
npm i -g vercel

# Login and deploy
cd /Users/kanishk/Desktop/YCDemo/suna
vercel login
vercel

# Follow the prompts, accept defaults
```

### Step 3: Add Environment Variables (1 minute)

Go to: https://vercel.com/dashboard → Your Project → Settings → Environment Variables

**Add these (minimum required):**

```
ENV_MODE=production
PYTHONPATH=/var/task/backend

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Redis (from Upstash)
REDIS_HOST=your-host.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=your-password
REDIS_SSL=true

# LLM (pick one or more)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Frontend
FRONTEND_URL=https://your-frontend.com
```

### Step 4: Redeploy with Variables

```bash
vercel --prod
```

### Step 5: Test It

```bash
curl https://your-deployment.vercel.app/api/health
```

You should see: `{"status":"ok",...}`

## ✅ You're Live!

Your API is now deployed at: `https://your-deployment.vercel.app`

## ⚠️ Important: Deploy Background Workers

Vercel can't run background workers. You need to deploy them separately:

### Quick Worker Setup (Railway - Easiest)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
cd /Users/kanishk/Desktop/YCDemo/suna/backend
railway init
railway up -d Dockerfile.worker

# Add environment variables in Railway dashboard
# Use same variables as Vercel, but change:
PYTHONPATH=/app
```

## Next Steps

- [ ] Update your frontend to use the new API URL
- [ ] Set up Stripe webhooks: `https://your-deployment.vercel.app/api/webhooks/stripe`
- [ ] Enable monitoring (Sentry, Langfuse)
- [ ] Review full documentation in `VERCEL_DEPLOYMENT.md`

## Troubleshooting

**"Module not found" errors**
- Check `PYTHONPATH=/var/task/backend` is set in Vercel

**Redis connection fails**
- Verify Upstash credentials
- Ensure `REDIS_SSL=true`

**Background tasks don't run**
- Deploy workers separately (see above)

**CORS errors**
- Add your frontend URL to `FRONTEND_URL` env var
- Check CORS settings in `backend/api.py`

## Get Full Details

For complete documentation, see:
- `VERCEL_DEPLOYMENT.md` - Full deployment guide
- `ENV_VARS.md` - All environment variables
- `deploy-checklist.md` - Detailed checklist

## Need Help?

Run the environment checker:
```bash
python scripts/check-env.py
```

---

**Total Setup Time**: ~5-10 minutes

**What You Get**:
- ✅ Production API on Vercel
- ✅ Global CDN
- ✅ Auto-scaling
- ✅ HTTPS by default
- ✅ Zero server management

**What You Still Need**:
- 🔄 Background workers (deploy to Railway/Render)
- 📊 Monitoring setup
- 🔔 Alerting configuration

