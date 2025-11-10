# 🔧 Quick Fix: Google Sign-In Not Working in Production

## The Problem

You're seeing this error when users try to sign in with Google:

```json
{
  "code": 400,
  "error_code": "validation_failed",
  "msg": "Unsupported provider: provider is not enabled"
}
```

## The Solution (5 Minutes)

### Step 1: Enable Google OAuth in Supabase

**If using Supabase Cloud (Recommended):**

1. Go to https://app.supabase.com/
2. Select your project
3. Click **Authentication → Providers** in the sidebar
4. Find **Google** in the list
5. Toggle it **ON** (Enable Sign in with Google)
6. Skip to Step 2 below

**If using Self-Hosted Supabase:**

The configuration file has been updated for you. You just need to set environment variables (Step 2).

### Step 2: Get Google OAuth Credentials

1. Go to https://console.cloud.google.com/
2. Select your project (or create one)
3. Navigate to **APIs & Services → Credentials**
4. Click **+ CREATE CREDENTIALS → OAuth client ID**
5. Select **Web application**
6. Add these Authorized redirect URIs:
   ```
   https://your-project-id.supabase.co/auth/v1/callback
   ```
7. Click **CREATE**
8. **Copy the Client ID and Client Secret**

### Step 3: Configure Supabase with Google Credentials

**In Supabase Dashboard:**

1. Still in **Authentication → Providers → Google**
2. Paste your **Client ID**
3. Paste your **Client Secret**
4. Click **Save**

### Step 4: Set Environment Variables (For Self-Hosted Only)

If you're using self-hosted Supabase, add these to your environment:

```bash
SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET=your-client-secret-here
```

**For Vercel:**
```bash
vercel env add SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID production
# Paste your client ID when prompted

vercel env add SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET production
# Paste your client secret when prompted

# Redeploy
vercel --prod
```

**For Railway/Render:**
- Add the variables in your service's environment settings
- Redeploy

### Step 5: Test

1. Go to your application
2. Click "Sign in with Google"
3. You should see the Google OAuth consent screen
4. After authorizing, you should be signed in ✅

## Still Not Working?

### Check Authorized Redirect URIs

Make sure your Google OAuth client includes the exact redirect URI:

- Supabase hosted: `https://YOUR-PROJECT.supabase.co/auth/v1/callback`
- Self-hosted: `https://YOUR-DOMAIN.com/auth/v1/callback`

**Common mistakes:**
- ❌ Missing `/auth/v1/callback`
- ❌ Using `http://` instead of `https://`
- ❌ Wrong Supabase project ID
- ❌ Typo in the domain

### Check Authorized JavaScript Origins

Add these to your Google OAuth client:

- Production: `https://your-app-domain.com`
- Development: `http://localhost:3000`

### Verify Environment Variables

**For Supabase Cloud users:**
- You don't need to set `SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID` in your app
- These credentials are stored in Supabase and used automatically

**For self-hosted Supabase:**
- Make sure the environment variables are set in your deployment
- Restart your services after adding them

## Need More Help?

See the complete setup guide: [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md)

## Quick Reference

| What You Need | Where to Get It |
|---------------|----------------|
| Google Client ID | Google Cloud Console → Credentials |
| Google Client Secret | Google Cloud Console → Credentials |
| Supabase Project ID | Supabase Dashboard → Project Settings |
| Redirect URI | `https://[project-id].supabase.co/auth/v1/callback` |

## Checklist

- [ ] Google OAuth client created in Google Cloud Console
- [ ] OAuth consent screen configured
- [ ] Authorized redirect URIs added (must match exactly)
- [ ] Google provider enabled in Supabase
- [ ] Client ID and Secret added to Supabase
- [ ] Environment variables set (if self-hosted)
- [ ] Application redeployed
- [ ] Tested sign-in flow

---

**Estimated Time to Fix:** 5-10 minutes

**Common Causes of This Error:**
1. Google OAuth not enabled in Supabase ← **Most common**
2. Missing Google OAuth credentials
3. Incorrect redirect URIs
4. Environment variables not set (self-hosted only)

