# Vercel Production Deployment Checklist

Follow this step-by-step checklist to deploy your backend to production.

## Pre-Deployment Setup

### ✅ 1. Set Up External Services

- [ ] **Upstash Redis**
  - Create account at https://upstash.com
  - Create a new Redis database
  - Note down: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`

- [ ] **Supabase** (if not already done)
  - Ensure production database is set up
  - Note down connection credentials
  - Verify RLS policies are enabled
  - **⚠️ IMPORTANT:** Configure Google OAuth (see `GOOGLE_OAUTH_SETUP.md`)
    - Enable Google provider in Supabase Dashboard → Authentication → Providers
    - Add Google Client ID and Secret from Google Cloud Console

### ✅ 2. Configure Stripe

- [ ] Set up production Stripe account
- [ ] Create webhook endpoint: `https://your-backend.vercel.app/api/webhooks/stripe`
- [ ] Note down webhook secret
- [ ] Verify all product/price IDs match config

### ✅ 3. Get API Keys

- [ ] At least one LLM provider (Anthropic, OpenAI, etc.)
- [ ] Optional: Tavily, Firecrawl, etc.

## Vercel Setup

### ✅ 4. Create Vercel Project

```bash
# Option A: Using CLI
npm i -g vercel
cd /Users/kanishk/Desktop/YCDemo/suna
vercel login
vercel link

# Option B: Using Dashboard
# Go to https://vercel.com/new
# Import your Git repository
```

### ✅ 5. Configure Environment Variables

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

Copy variables from `ENV_VARS.md` and add them one by one:

**Critical Variables (Must Set):**
- [ ] `ENV_MODE=production`
- [ ] `PYTHONPATH=/var/task/backend`
- [ ] All Supabase variables (including GOOGLE_CLIENT_ID and GOOGLE_SECRET for OAuth)
- [ ] `SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID` (for Google Sign-In)
- [ ] `SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET` (for Google Sign-In)
- [ ] All Redis variables (Upstash)
- [ ] At least one LLM API key
- [ ] Stripe keys
- [ ] `FRONTEND_URL`

**Recommended:**
- [ ] `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`
- [ ] `SENTRY_DSN`

### ✅ 6. Deploy to Vercel

```bash
# Deploy to production
vercel --prod

# Or push to main branch if using Git integration
git push origin main
```

### ✅ 7. Test Deployment

```bash
# Test health endpoint
curl https://your-deployment.vercel.app/api/health

# Expected response:
# {
#   "status": "ok",
#   "timestamp": "2024-11-10T...",
#   "instance_id": "single"
# }
```

## Background Workers Setup

### ✅ 8. Choose Worker Deployment Platform

Pick one:
- [ ] **Railway** (Easiest, Docker support)
- [ ] **Render** (Good free tier)
- [ ] **DigitalOcean** (Most control)
- [ ] **Fly.io** (Global deployment)

### ✅ 9. Deploy Workers

#### Option A: Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and init
railway login
railway init

# Link to Dockerfile.worker
railway up -d backend/Dockerfile.worker

# Add environment variables in Railway dashboard
# Copy from ENV_VARS.md (use PYTHONPATH=/app instead)
```

#### Option B: Render

1. Go to https://dashboard.render.com/
2. New → Background Worker
3. Connect your repository
4. Use `render.yaml` configuration
5. Add environment variables from `ENV_VARS.md`
6. Deploy

#### Option C: DigitalOcean

1. Create App Platform app
2. Select Docker deployment
3. Point to `backend/Dockerfile.worker`
4. Add environment variables
5. Deploy

### ✅ 10. Verify Workers

Check worker logs to ensure:
- [ ] Successfully connected to Redis
- [ ] Successfully connected to Supabase
- [ ] Dramatiq workers are running
- [ ] No startup errors

## Post-Deployment Configuration

### ✅ 11. Update Frontend

Update frontend API URL:
```typescript
// In your frontend config
const API_URL = 'https://your-backend.vercel.app'
```

Redeploy frontend if needed.

### ✅ 12. Configure Webhooks

Set up webhook endpoints in external services:

- [ ] **Stripe**: `https://your-backend.vercel.app/api/webhooks/stripe`
- [ ] **Composio**: `https://your-backend.vercel.app/api/webhooks/composio`
- [ ] Add `WEBHOOK_BASE_URL` env var

### ✅ 13. Test End-to-End

- [ ] User registration/login works
- [ ] Can create agents
- [ ] Can send messages to agents
- [ ] Agent responses stream correctly
- [ ] Background tasks execute (check worker logs)
- [ ] File uploads work
- [ ] Billing/subscription flows work

## Monitoring & Maintenance

### ✅ 14. Set Up Monitoring

- [ ] **Vercel Analytics**: Enable in dashboard
- [ ] **Sentry**: Verify error tracking works
- [ ] **Langfuse**: Check LLM traces appear
- [ ] **Uptime Monitor**: Set up (e.g., UptimeRobot)

### ✅ 15. Configure Alerts

Set up alerts for:
- [ ] Function errors (Sentry)
- [ ] High latency
- [ ] Worker failures
- [ ] Redis connection issues
- [ ] Database connection issues

### ✅ 16. Security Audit

- [ ] All API keys are in environment variables (not code)
- [ ] CORS origins are restricted to your domains
- [ ] Rate limiting is configured
- [ ] Webhook signatures are validated
- [ ] Database RLS is enabled
- [ ] Admin endpoints are protected

## Performance Optimization

### ✅ 17. Optimize for Production

- [ ] Enable Vercel caching where appropriate
- [ ] Configure CDN for static assets
- [ ] Set up database connection pooling (already done in Supabase)
- [ ] Monitor function cold starts
- [ ] Review function memory allocation

### ✅ 18. Load Testing

Run load tests to ensure:
- [ ] API can handle expected traffic
- [ ] Workers can process background jobs
- [ ] No memory leaks
- [ ] Response times are acceptable

## Backup & Disaster Recovery

### ✅ 19. Set Up Backups

- [ ] Supabase automatic backups enabled
- [ ] Redis backup strategy (if using persistent Redis)
- [ ] Document recovery procedures

### ✅ 20. Create Rollback Plan

- [ ] Document how to rollback Vercel deployment
- [ ] Document how to rollback worker deployment
- [ ] Keep previous working configuration

---

## Common Issues & Solutions

### Issue: "Module not found" errors
**Solution**: Ensure `PYTHONPATH=/var/task/backend` is set in Vercel

### Issue: Redis connection timeout
**Solution**: Verify Upstash credentials, ensure `REDIS_SSL=true`

### Issue: Background tasks not executing
**Solution**: Check worker logs, ensure workers are running and connected

### Issue: CORS errors from frontend
**Solution**: Verify `FRONTEND_URL` is set correctly and CORS is configured

### Issue: Stripe webhooks failing
**Solution**: Check webhook secret, ensure endpoint is accessible

---

## Quick Deploy Commands

```bash
# Verify files are created
ls -la vercel.json railway.json render.yaml

# Deploy to Vercel
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs [deployment-url]

# Rollback if needed
vercel rollback [deployment-url]
```

---

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Upstash Docs**: https://docs.upstash.com

---

**Last Updated**: November 10, 2024

**Status Tracker**: 
- [ ] Pre-deployment complete
- [ ] Vercel deployed
- [ ] Workers deployed
- [ ] Testing complete
- [ ] Monitoring configured
- [ ] Production ready ✅

