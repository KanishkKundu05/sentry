# Google OAuth Setup Guide

This guide explains how to set up Google Sign-In for your Suna application.

## Quick Fix for Production

If you're seeing the error **"Unsupported provider: provider is not enabled"**, you need to enable Google OAuth in your Supabase instance.

## Prerequisites

- A Google Cloud Console account
- Access to your Supabase project

## Step 1: Create Google OAuth Credentials

### 1.1 Go to Google Cloud Console

1. Visit https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Navigate to **APIs & Services → Credentials**

### 1.2 Configure OAuth Consent Screen

1. Click **OAuth consent screen** in the left sidebar
2. Choose **External** (or Internal if using Google Workspace)
3. Fill in the required fields:
   - **App name:** Your app name (e.g., "Suna AI")
   - **User support email:** Your email
   - **Developer contact email:** Your email
4. Click **Save and Continue**
5. Skip **Scopes** for now (click **Save and Continue**)
6. Add test users if needed (for development)
7. Click **Save and Continue**

### 1.3 Create OAuth Client ID

1. Go to **Credentials** in the left sidebar
2. Click **+ CREATE CREDENTIALS → OAuth client ID**
3. Select **Application type:** Web application
4. Fill in the details:
   - **Name:** "Suna Web Client" (or any name)
   - **Authorized JavaScript origins:**
     - Production: `https://your-domain.com`
     - Development: `http://localhost:3000`
   - **Authorized redirect URIs:**
     - For Supabase hosted: `https://your-project.supabase.co/auth/v1/callback`
     - For self-hosted Supabase: `https://your-supabase-instance.com/auth/v1/callback`
     - For local dev: `http://localhost:54321/auth/v1/callback`
5. Click **CREATE**
6. **Save your Client ID and Client Secret** (you'll need these next)

## Step 2: Configure Supabase

### Option A: Using Supabase Dashboard (Recommended for Hosted Supabase)

1. Go to https://app.supabase.com/
2. Select your project
3. Navigate to **Authentication → Providers**
4. Find **Google** and click to expand
5. Toggle **Enable Sign in with Google** to ON
6. Enter your credentials:
   - **Client ID:** (from Google Cloud Console)
   - **Client Secret:** (from Google Cloud Console)
7. Copy the **Callback URL** shown (you may need to add this to Google Cloud Console if not already added)
8. Click **Save**

### Option B: Using Self-Hosted Supabase (config.toml)

If you're running Supabase locally or self-hosted, the `config.toml` file has been updated with the Google OAuth section:

```toml
[auth.external.google]
enabled = true
client_id = "env(SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID)"
secret = "env(SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET)"
redirect_uri = ""
skip_nonce_check = false
```

## Step 3: Set Environment Variables

### For Production Deployment

Add these environment variables to your production environment:

```bash
SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET=your-client-secret
```

#### For Vercel:
1. Go to your Vercel project
2. Settings → Environment Variables
3. Add both variables above
4. Redeploy your application

#### For Google Cloud Run:
```bash
# Create secrets
echo -n "your-client-id" | gcloud secrets create SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID --data-file=-
echo -n "your-client-secret" | gcloud secrets create SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET --data-file=-

# Grant access to Cloud Run service
gcloud secrets add-iam-policy-binding SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID \
  --member="serviceAccount:your-service-account@your-project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET \
  --member="serviceAccount:your-service-account@your-project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### For Railway/Render:
Add the environment variables in your service settings.

### For Local Development

Add to your `.env` file:

```bash
SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
SUPABASE_AUTH_EXTERNAL_GOOGLE_SECRET=your-client-secret
```

## Step 4: Update Authorized Redirect URIs

Make sure your Google Cloud Console OAuth client has the correct redirect URIs for all environments:

### Production
```
https://your-supabase-project.supabase.co/auth/v1/callback
```

### Development
```
http://localhost:54321/auth/v1/callback
```

### Mobile (if applicable)
For the React Native mobile app, you may need additional configuration for deep linking.

## Step 5: Test the Integration

1. **Restart your Supabase instance** (if self-hosted):
   ```bash
   supabase stop
   supabase start
   ```

2. **Redeploy your application** (if hosted)

3. **Test Sign In:**
   - Go to your application's sign-in page
   - Click "Continue with Google"
   - You should be redirected to Google's OAuth consent screen
   - After authorizing, you should be redirected back and signed in

## Troubleshooting

### Error: "redirect_uri_mismatch"
- **Cause:** The redirect URI in your request doesn't match any authorized URIs in Google Cloud Console
- **Solution:** Add the exact redirect URI shown in the error to your OAuth client's authorized redirect URIs

### Error: "Unsupported provider: provider is not enabled"
- **Cause:** Google OAuth is not enabled in Supabase
- **Solution:** Follow Step 2 above to enable it

### Error: "Invalid client_id"
- **Cause:** The client ID is incorrect or not set
- **Solution:** Verify your environment variables match the credentials from Google Cloud Console

### Error: "Access blocked: This app's request is invalid"
- **Cause:** OAuth consent screen is not properly configured
- **Solution:** Complete the OAuth consent screen setup in Google Cloud Console

### Local Development Issues
- Make sure you're using `http://localhost:54321/auth/v1/callback` (not 127.0.0.1)
- Add `http://localhost:3000` to authorized JavaScript origins
- Check that Supabase local instance is running

## Security Best Practices

1. **Never commit credentials** to git
   - Use environment variables or secret management
   - Keep your `.env` files in `.gitignore`

2. **Rotate secrets regularly**
   - Generate new client secrets periodically
   - Update in both Google Cloud Console and Supabase

3. **Use different credentials per environment**
   - Development credentials should be separate from production
   - Use different Google Cloud projects if possible

4. **Restrict OAuth scopes**
   - Only request the scopes you need (email, profile)
   - Don't request additional Google API access unless required

5. **Monitor OAuth usage**
   - Check Google Cloud Console for unusual activity
   - Review Supabase auth logs regularly

## Additional Resources

- [Supabase Google OAuth Documentation](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

## Support

If you continue to experience issues after following this guide:
1. Check Supabase logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure your Google OAuth client is properly configured
4. Check that your redirect URIs match exactly (including http/https and ports)

