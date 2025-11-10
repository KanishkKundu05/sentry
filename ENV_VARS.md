# Production Environment Variables

This file lists all environment variables needed for production deployment.

## Core Configuration

```bash
ENV_MODE=production
PYTHONPATH=/var/task/backend  # For Vercel, use /app for Docker
```

## Supabase (Required)

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Supabase Auth - Google OAuth (Required for Sign in with Google)
SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET=your-google-client-secret
```

## Redis (Required - Use Upstash for Vercel)

```bash
REDIS_HOST=your-upstash-redis-host.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=your-upstash-redis-password
REDIS_SSL=true
```

## LLM API Keys (At least one required)

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=...
OPENROUTER_API_KEY=sk-or-v1-...
XAI_API_KEY=...
```

## OpenRouter Configuration

```bash
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OR_SITE_URL=https://kortix.ai
OR_APP_NAME=Kortix AI
```

## Stripe (Required for billing)

```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_DEFAULT_TRIAL_DAYS=14
```

## Frontend URL

```bash
FRONTEND_URL=https://your-frontend-domain.com
```

## Observability (Optional but recommended)

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

## Sentry Error Tracking (Optional)

```bash
SENTRY_DSN=https://...@...ingest.sentry.io/...
```

## Search & Tools (Optional)

```bash
TAVILY_API_KEY=tvly-...
EXA_API_KEY=...
SERPER_API_KEY=...
FIRECRAWL_API_KEY=...
FIRECRAWL_URL=https://api.firecrawl.dev
SEMANTIC_SCHOLAR_API_KEY=...
```

## Sandbox Configuration (Optional)

```bash
DAYTONA_API_KEY=...
DAYTONA_SERVER_URL=...
DAYTONA_TARGET=...
```

## Email Service (Optional)

```bash
MAILTRAP_API_KEY=...
```

## Composio Integration (Optional)

```bash
COMPOSIO_API_KEY=...
COMPOSIO_WEBHOOK_SECRET=...
```

## VAPI Configuration (Optional)

```bash
VAPI_PRIVATE_KEY=...
VAPI_PHONE_NUMBER_ID=...
VAPI_SERVER_URL=...
```

## Webhook Configuration (Optional)

```bash
WEBHOOK_BASE_URL=https://your-backend-domain.com
TRIGGER_WEBHOOK_SECRET=...
```

## Security

```bash
KORTIX_ADMIN_API_KEY=...  # Auto-generated if not provided
API_KEY_SECRET=your-secret-key-for-api-keys
MCP_CREDENTIAL_ENCRYPTION_KEY=...  # 32-byte base64 encoded key
```

## Agent Execution Limits

```bash
MAX_PARALLEL_AGENT_RUNS=3
```

## API Keys Throttling

```bash
API_KEY_LAST_USED_THROTTLE_SECONDS=900
```

## Freestyle Deployment (Optional)

```bash
FREESTYLE_API_KEY=...
```

## AWS Bedrock (Optional)

```bash
AWS_BEARER_TOKEN_BEDROCK=...
```

## OpenAI Compatible API (Optional)

```bash
OPENAI_COMPATIBLE_API_KEY=...
OPENAI_COMPATIBLE_API_BASE=...
```

## Cloud Services (Optional)

```bash
CLOUDFLARE_API_TOKEN=...
RAPID_API_KEY=...
```

---

## How to Use

### For Vercel:
1. Go to your Vercel project settings
2. Navigate to "Environment Variables"
3. Add each variable from above
4. Select "Production" environment

### For Railway/Render/DigitalOcean:
1. Copy the variables you need
2. Add them in your service's environment settings
3. Deploy your application

### Generate Encryption Keys:

For `MCP_CREDENTIAL_ENCRYPTION_KEY`:
```python
import base64
import os
key = base64.b64encode(os.urandom(32)).decode()
print(key)
```

For `API_KEY_SECRET`:
```python
import secrets
secret = secrets.token_urlsafe(32)
print(secret)
```

