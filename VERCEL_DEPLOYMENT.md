# Vercel Backend Deployment Guide

This guide will help you deploy the Suna backend to Vercel for production.

## ⚠️ Architecture Considerations

### What Works on Vercel
- ✅ FastAPI HTTP endpoints
- ✅ Streaming responses (with timeout limits)
- ✅ Serverless functions
- ✅ Static file serving

### What Doesn't Work on Vercel
- ❌ **Background workers (Dramatiq)** - Must be deployed separately
- ❌ Long-running tasks > 300 seconds (Pro plan limit)
- ❌ Persistent in-memory state between requests

### Recommended Hybrid Architecture

```
┌─────────────────┐
│   Vercel        │  → FastAPI API endpoints
│   (API Layer)   │     - User authentication
│                 │     - CRUD operations
└─────────────────┘     - Webhook handlers
        │
        ├─────────────────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼──────────┐
│  Supabase      │      │  Redis (Upstash)  │
│  (Database)    │      │  (Caching)        │
└────────────────┘      └───────────────────┘
        │
┌───────▼────────────────┐
│  Railway/Render/DO     │  → Dramatiq background workers
│  (Worker Layer)        │     - Agent execution
│                        │     - Long-running tasks
└────────────────────────┘
```

## Step 1: Prepare Your Repository

The following files have been created for you:
- ✅ `vercel.json` - Vercel configuration
- ✅ `backend/requirements.txt` - Python dependencies
- ✅ `.vercelignore` - Files to exclude from deployment

## Step 2: Set Up Vercel Project

### 2.1 Install Vercel CLI (Optional)
```bash
npm i -g vercel
```

### 2.2 Connect to Vercel
```bash
# From project root
vercel login
vercel link
```

Or use the Vercel Dashboard: https://vercel.com/new

## Step 3: Configure Environment Variables

### Required Environment Variables

Add these in **Vercel Dashboard → Settings → Environment Variables**:

#### Core Configuration
```bash
ENV_MODE=production
PYTHONPATH=/var/task/backend
```

#### Supabase (Required)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

#### Redis (Required - Use Upstash)
```bash
REDIS_HOST=your-upstash-redis-host.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=your-upstash-password
REDIS_SSL=true
```

💡 **Upstash Redis Setup**: 
1. Go to https://upstash.com/
2. Create a Redis database
3. Copy the connection details

#### LLM API Keys (At least one required)
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=...
```

#### Stripe (Required for billing)
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

#### Optional Services
```bash
# Observability
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
SENTRY_DSN=https://...

# Tools
TAVILY_API_KEY=tvly-...
EXA_API_KEY=...
FIRECRAWL_API_KEY=...

# Sandbox
DAYTONA_API_KEY=...
DAYTONA_SERVER_URL=...

# Email
MAILTRAP_API_KEY=...

# Composio
COMPOSIO_API_KEY=...
COMPOSIO_WEBHOOK_SECRET=...

# Frontend
FRONTEND_URL=https://your-frontend.vercel.app
```

## Step 4: Deploy Background Workers Separately

The Dramatiq workers **cannot** run on Vercel. Deploy them separately:

### Option A: Railway
```bash
# railway.json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile.worker"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Option B: Render
Create a **Background Worker** service:
- **Build Command**: `cd backend && uv sync`
- **Start Command**: `cd backend && uv run dramatiq --processes 4 --threads 4 run_agent_background`

### Option C: DigitalOcean App Platform
Use the existing `backend/Dockerfile` with worker configuration

## Step 5: Deploy to Vercel

### Via CLI
```bash
# Production deployment
vercel --prod

# Preview deployment
vercel
```

### Via Git Integration
1. Connect your GitHub repository to Vercel
2. Push to your main branch
3. Vercel automatically deploys

## Step 6: Verify Deployment

### Health Check
```bash
curl https://your-backend.vercel.app/api/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-11-10T...",
  "instance_id": "single"
}
```

### Docker Health Check (requires Redis and DB)
```bash
curl https://your-backend.vercel.app/api/health-docker
```

## Step 7: Update Frontend Configuration

Update your frontend's API endpoint to point to your Vercel backend:

```typescript
// frontend/src/lib/config.ts or similar
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-backend.vercel.app';
```

## Troubleshooting

### Issue: Module Import Errors
**Solution**: Ensure `PYTHONPATH=/var/task/backend` is set in environment variables

### Issue: Redis Connection Failures
**Solution**: 
- Verify Redis is accessible from Vercel
- Use Upstash Redis (designed for serverless)
- Check REDIS_SSL is set to `true`

### Issue: Function Timeout
**Solution**: 
- Vercel Pro plan has 300s timeout
- Move long-running tasks to background workers
- Use streaming responses for real-time updates

### Issue: Package Size Too Large
**Solution**: 
- Increase `maxLambdaSize` in `vercel.json`
- Remove unnecessary dependencies
- Use `.vercelignore` to exclude files

### Issue: Background Tasks Not Running
**Solution**: 
- Deploy Dramatiq workers separately (see Step 4)
- Update worker to connect to production database/redis

## Performance Optimization

### 1. Use Edge Functions (Optional)
For low-latency global deployment:
```json
{
  "functions": {
    "backend/api.py": {
      "runtime": "@vercel/python",
      "regions": ["iad1", "sfo1", "cdg1"]
    }
  }
}
```

### 2. Enable Connection Pooling
Already configured in Supabase client.

### 3. Monitor Performance
- Use Vercel Analytics
- Set up Sentry for error tracking
- Use Langfuse for LLM observability

## Security Checklist

- [ ] All sensitive keys are in Vercel environment variables (not in code)
- [ ] CORS origins are properly configured in `api.py`
- [ ] Supabase RLS policies are enabled
- [ ] API rate limiting is configured
- [ ] Stripe webhook signatures are verified
- [ ] JWT tokens are validated

## Cost Considerations

### Vercel
- **Hobby**: Free (60s timeout, 12 deployments/day)
- **Pro**: $20/month per member (300s timeout, unlimited deployments)

### Background Workers
- **Railway**: ~$5-20/month (pay for usage)
- **Render**: $7/month (512MB RAM) or $25/month (2GB RAM)
- **DigitalOcean**: $6/month (basic droplet)

## Support

If you encounter issues:
1. Check Vercel function logs: `vercel logs [deployment-url]`
2. Review backend logs in Vercel Dashboard
3. Verify all environment variables are set
4. Test endpoints locally first

## Next Steps

1. Set up monitoring and alerting
2. Configure auto-scaling for workers
3. Set up staging environment
4. Implement CI/CD pipeline
5. Add integration tests

---

**Note**: This deployment setup separates the API layer (Vercel) from the worker layer (separate service), which is the recommended architecture for FastAPI applications with background tasks on Vercel.

