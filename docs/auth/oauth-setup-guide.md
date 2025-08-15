# OAuth Integration Setup Guide

This guide explains how to set up Google and GitHub OAuth authentication with Supabase for your application.

## Overview

The OAuth integration provides:

- **Google OAuth**: Allows users to sign in with their Google accounts
- **GitHub OAuth**: Allows users to sign in with their GitHub accounts
- **Seamless Integration**: Works alongside existing email/password authentication
- **User Sync**: Automatically creates local user records while using Supabase Auth
- **Security**: Uses Supabase's built-in OAuth flow with additional JWT token management

## Prerequisites

1. Supabase project configured
2. Google Cloud Console access (for Google OAuth)
3. GitHub Developer Settings access (for GitHub OAuth)
4. Domain configured for OAuth callbacks

## 1. Supabase Configuration

### Enable OAuth Providers

1. Go to your Supabase Dashboard
2. Navigate to **Authentication → Providers**
3. Enable **Google** and **GitHub** providers

### Configure Redirect URLs

In your Supabase Auth settings, add these redirect URLs:

**For Development:**

```
http://localhost:3000/auth/callback
```

**For Production:**

```
https://yourdomain.com/auth/callback
```

## 2. Google OAuth Setup

### Create Google OAuth Application

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google+ API**
4. Go to **Credentials → Create Credentials → OAuth 2.0 Client IDs**
5. Configure the OAuth consent screen
6. Create **Web Application** credentials

### Configure OAuth Settings

**Authorized JavaScript Origins:**

```
http://localhost:3000 (development)
https://yourdomain.com (production)
```

**Authorized Redirect URIs:**

```
https://[YOUR_SUPABASE_PROJECT_REF].supabase.co/auth/v1/callback
```

### Add to Supabase

1. In Supabase Dashboard → Authentication → Providers → Google
2. Enable Google provider
3. Add your Google **Client ID** and **Client Secret**
4. Save configuration

## 3. GitHub OAuth Setup

### Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in application details:
   - **Application name**: Your app name
   - **Homepage URL**: `https://yourdomain.com` (or `http://localhost:3000` for dev)
   - **Authorization callback URL**: `https://[YOUR_SUPABASE_PROJECT_REF].supabase.co/auth/v1/callback`

### Add to Supabase

1. In Supabase Dashboard → Authentication → Providers → GitHub
2. Enable GitHub provider
3. Add your GitHub **Client ID** and **Client Secret**
4. Save configuration

## 4. Backend Configuration

The backend endpoints are already implemented. Ensure your Supabase environment variables are configured:

### Environment Variables

Create or update your `.env` file in the `bff/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# Other required env vars...
```

## 5. Frontend Configuration

The frontend OAuth components are already implemented. No additional configuration needed.

## 6. Testing the Integration

### Manual Testing Steps

1. **Start the development servers:**

   ```bash
   # Backend
   cd bff
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Frontend
   cd frontend
   npm run dev
   ```

2. **Test Google OAuth:**

   - Navigate to `http://localhost:3000/login`
   - Click "Continue with Google"
   - Complete Google OAuth flow
   - Verify redirect to dashboard
   - Check user creation in Supabase Auth dashboard

3. **Test GitHub OAuth:**

   - Navigate to `http://localhost:3000/login`
   - Click "Continue with GitHub"
   - Complete GitHub OAuth flow
   - Verify redirect to dashboard
   - Check user creation in Supabase Auth dashboard

4. **Test Registration:**
   - Navigate to `http://localhost:3000/register`
   - Try both Google and GitHub registration
   - Verify new user creation

### Verification Checklist

- [ ] OAuth buttons appear on login/register pages
- [ ] Google OAuth redirects to Google consent screen
- [ ] GitHub OAuth redirects to GitHub authorization page
- [ ] Successful authentication redirects to `/dashboard`
- [ ] Failed authentication shows error page with retry options
- [ ] User data is created in both Supabase Auth and local database
- [ ] Existing users can sign in with OAuth
- [ ] New users can register with OAuth

## 7. Common Issues and Troubleshooting

### Issue: "Invalid redirect URI"

**Solution:** Ensure your redirect URIs in Google/GitHub match exactly with Supabase callback URL:

```
https://[YOUR_SUPABASE_PROJECT_REF].supabase.co/auth/v1/callback
```

### Issue: "OAuth provider not found"

**Solution:** Verify that the provider is enabled in Supabase Dashboard and has valid credentials.

### Issue: "CORS errors during OAuth"

**Solution:** Ensure your domain is added to authorized origins in Google Cloud Console.

### Issue: "Callback page shows loading indefinitely"

**Solution:** Check browser network tab for API errors. Verify backend endpoints are responding correctly.

### Issue: "User not created in local database"

**Solution:** Check backend logs for user creation errors. Verify database connection and user model.

## 8. Security Considerations

### Production Checklist

- [ ] Use HTTPS for all OAuth redirect URIs
- [ ] Restrict OAuth app domains to your production domain
- [ ] Enable PKCE (Proof Key for Code Exchange) in Supabase if available
- [ ] Review OAuth scopes requested (minimal necessary permissions)
- [ ] Monitor OAuth usage in Supabase Dashboard
- [ ] Set up proper CORS policies
- [ ] Implement rate limiting for auth endpoints

### Data Privacy

- OAuth providers will share basic profile information (email, name, avatar)
- User consent is required for OAuth authentication
- Users can revoke OAuth access through their provider settings
- Local user data follows your privacy policy

## 9. Advanced Configuration

### Custom OAuth Scopes

You can request additional scopes by configuring them in Supabase:

**Google Scopes:**

- `email` (default)
- `profile` (default)
- `openid` (default)

**GitHub Scopes:**

- `user:email` (default)
- `read:user` (default)

### Custom User Data Mapping

The backend automatically maps OAuth user data:

```python
# Google OAuth user data
user_metadata = {
    "full_name": google_user.get("name"),
    "avatar_url": google_user.get("picture"),
    "oauth_provider": "google"
}

# GitHub OAuth user data
user_metadata = {
    "full_name": github_user.get("name"),
    "username": github_user.get("login"),
    "avatar_url": github_user.get("avatar_url"),
    "oauth_provider": "github"
}
```

## 10. Production Deployment

### Environment Variables for Production

Ensure these environment variables are set in production:

```env
# Frontend (Next.js)
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key


# Backend (FastAPI)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### OAuth Provider Settings for Production

Update your OAuth app settings with production URLs:

**Google Cloud Console:**

- Authorized origins: `https://yourdomain.com`
- Authorized redirect URIs: `https://your-project-ref.supabase.co/auth/v1/callback`

**GitHub OAuth App:**

- Homepage URL: `https://yourdomain.com`
- Authorization callback URL: `https://your-project-ref.supabase.co/auth/v1/callback`

## Support

If you encounter issues:

1. Check Supabase Dashboard logs
2. Review browser network tab for failed requests
3. Verify all environment variables are set correctly
4. Ensure OAuth provider credentials are valid
5. Check that redirect URIs match exactly

For development support, check the console logs and network requests in browser developer tools.
