# Backend Deployment Options

This backend can be deployed in multiple ways. Choose the option that best fits your needs.

## Deployment Options Overview

| Platform | API Layer | Workers | Difficulty | Cost | Best For |
|----------|-----------|---------|------------|------|----------|
| **Vercel + Railway** | ✅ Vercel | ✅ Railway | ⭐⭐ Easy | $ | Recommended |
| **Render** | ✅ Render | ✅ Render | ⭐ Easiest | $ | All-in-one |
| **DigitalOcean** | ✅ App Platform | ✅ App Platform | ⭐⭐ Medium | $$ | Full control |
| **Docker (Self-hosted)** | ✅ Docker | ✅ Docker | ⭐⭐⭐ Hard | Free-$$$ | Complete control |
| **Kubernetes** | ✅ K8s | ✅ K8s | ⭐⭐⭐⭐ Expert | $$$ | Enterprise |

## Quick Start Guides

### 🚀 Vercel (Recommended for API)

Best for: Serverless API with auto-scaling

**Pros**: Fast, global CDN, auto-scaling, easy setup
**Cons**: Can't run workers, cold starts

👉 **[Follow QUICKSTART_VERCEL.md](../QUICKSTART_VERCEL.md)**

### 🚂 Railway (Recommended for Workers)

Best for: Background workers

**Pros**: Docker support, easy setup, affordable
**Cons**: Workers only, not ideal for API

```bash
railway login
railway init
railway up -d Dockerfile.worker
```

### 🎨 Render (All-in-One)

Best for: Complete backend in one place

**Pros**: Simple, workers + API together
**Cons**: Slower than Vercel, more expensive

```bash
# Deploy using render.yaml
# Go to https://dashboard.render.com/
# Connect repo and use render.yaml config
```

### 🐳 Docker (Self-Hosted)

Best for: Complete control, cost optimization

```bash
# API
docker build -f Dockerfile -t suna-api .
docker run -p 8000:8000 --env-file .env suna-api

# Workers
docker build -f Dockerfile.worker -t suna-worker .
docker run --env-file .env suna-worker

# Or use docker-compose
docker-compose up -d
```

## Architecture Comparison

### Option 1: Hybrid (Vercel + Railway) ⭐ Recommended

```
Frontend (Vercel)
    ↓
API (Vercel Serverless)
    ↓
├─→ Supabase (Database)
├─→ Upstash Redis (Cache)
└─→ Railway (Background Workers)
```

**When to use**: Production apps, need global distribution, auto-scaling

### Option 2: All Render

```
Frontend (Vercel)
    ↓
API (Render Web Service)
    ↓
├─→ Supabase (Database)
├─→ Redis (Render)
└─→ Workers (Render Background Worker)
```

**When to use**: Simpler setup, all in one platform

### Option 3: All Docker

```
Frontend (Nginx/Caddy)
    ↓
API (Docker + Gunicorn)
    ↓
├─→ PostgreSQL (Docker)
├─→ Redis (Docker)
└─→ Workers (Docker + Dramatiq)
```

**When to use**: Self-hosted, cost optimization, specific compliance needs

## Deployment Files

| File | Purpose | Used By |
|------|---------|---------|
| `vercel.json` | Vercel configuration | Vercel |
| `Dockerfile` | API container | Docker, Railway, Render |
| `Dockerfile.worker` | Worker container | Docker, Railway, Render |
| `docker-compose.yml` | Local dev & self-hosted | Docker Compose |
| `railway.json` | Railway configuration | Railway |
| `render.yaml` | Render configuration | Render |
| `requirements.txt` | Python dependencies | Vercel |
| `pyproject.toml` | Python project config | uv, pip |

## Environment Setup

Each deployment needs environment variables. See:
- **All variables**: `ENV_VARS.md`
- **Quick reference**: `QUICKSTART_VERCEL.md`
- **Checklist**: `deploy-checklist.md`

### Minimum Required Variables

```bash
ENV_MODE=production
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWT_SECRET=...
REDIS_HOST=...
REDIS_PASSWORD=...
ANTHROPIC_API_KEY=... # or OPENAI_API_KEY
STRIPE_SECRET_KEY=...
FRONTEND_URL=...
```

## Post-Deployment

After deploying:

1. **Test health endpoint**
   ```bash
   curl https://your-api-url/api/health
   ```

2. **Configure webhooks**
   - Stripe: `https://your-api-url/api/webhooks/stripe`
   - Composio: `https://your-api-url/api/webhooks/composio`

3. **Update frontend**
   ```typescript
   const API_URL = 'https://your-api-url'
   ```

4. **Set up monitoring**
   - Enable Sentry error tracking
   - Configure Langfuse for LLM observability
   - Set up uptime monitoring

5. **Security audit**
   - Verify all secrets are in env vars
   - Check CORS settings
   - Test authentication flows

## Scaling Considerations

### API Layer

- **Vercel**: Auto-scales, 300s timeout (Pro)
- **Render**: Manual scaling, persistent connections
- **Docker**: Horizontal scaling with load balancer

### Workers

- **Railway**: Scale by increasing processes/threads
- **Render**: Add more background workers
- **Docker**: Deploy multiple worker containers

### Database

- **Supabase**: Auto-scales, connection pooling included
- **Self-hosted**: Configure pgBouncer for pooling

### Redis

- **Upstash**: Auto-scales, serverless-friendly
- **Self-hosted**: Configure replication, clustering

## Cost Estimation

### Small Scale (< 1000 users)
- Vercel Free + Railway Hobby: ~$5-10/month
- OR Render: ~$20/month
- OR Self-hosted: ~$6/month (DigitalOcean)

### Medium Scale (1K-10K users)
- Vercel Pro + Railway: ~$40-60/month
- OR Render Standard: ~$50-70/month
- OR Self-hosted: ~$25-50/month

### Large Scale (10K+ users)
- Vercel Pro + Railway Scale: ~$100-300/month
- OR Render Pro: ~$150-400/month
- OR Self-hosted: ~$100-500/month

*Prices exclude LLM API costs, Supabase, and traffic costs*

## Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Module import errors | Set `PYTHONPATH` correctly |
| Redis connection fails | Check Upstash credentials, enable SSL |
| Workers not running | Deploy workers separately |
| Function timeout | Use Pro plan or move to workers |
| Package too large | Increase maxLambdaSize in vercel.json |
| CORS errors | Update CORS origins in api.py |

## Migration Paths

### From Local → Vercel

1. Set up Upstash Redis
2. Deploy to Vercel
3. Deploy workers to Railway
4. Update frontend API URL

### From Vercel → Self-Hosted

1. Set up Docker environment
2. Configure docker-compose.yml
3. Deploy containers
4. Set up load balancer (Caddy/Nginx)
5. Update DNS records

### From Render → Vercel

1. Keep workers on Render
2. Deploy API to Vercel
3. Update frontend to use Vercel URL

## Monitoring & Observability

Recommended tools:

- **Errors**: Sentry
- **LLM Traces**: Langfuse
- **Metrics**: Prometheus + Grafana (self-hosted)
- **Logs**: Vercel/Railway/Render dashboards
- **Uptime**: UptimeRobot, Pingdom

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Docker Docs**: https://docs.docker.com
- **FastAPI Docs**: https://fastapi.tiangolo.com

## Quick Commands Reference

```bash
# Vercel
vercel login
vercel --prod
vercel logs

# Railway
railway login
railway up
railway logs

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose down

# Check environment
python scripts/check-env.py
```

---

**Next Steps**: Choose your deployment option and follow the corresponding guide!

