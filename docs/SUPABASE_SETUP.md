# Supabase Setup Guide

This guide walks you through setting up Supabase for Google OAuth authentication in the Code Audit Platform.

## What is Supabase?

Supabase is an open-source Firebase alternative that provides:
- Authentication (including Google OAuth)
- Database (PostgreSQL)
- Real-time subscriptions
- Storage

For this project, we use Supabase specifically for **Google OAuth authentication**.

---

## Step 1: Create a Supabase Project

1. Go to https://supabase.com
2. Sign up for a new account (or log in if you already have one)
3. Click **"New Project"**
4. Fill in the project details:
   - **Name**: `code-audit-platform` (or any name you prefer)
   - **Database Password**: Generate a secure password (save it!)
   - **Region**: Choose a region close to you
5. Click **"Create new project"**
6. Wait for the project to be provisioned (may take 1-2 minutes)

---

## Step 2: Enable Google OAuth Provider

1. In your Supabase project dashboard, go to **Authentication** → **Providers**
2. Find **Google** in the list and click on it
3. Toggle **"Enable Sign In with Google"** to ON
4. You'll need to set up Google Cloud Console OAuth credentials:

### Setting up Google Cloud Console OAuth

1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Go to **APIs & Services** → **Credentials**
4. Click **"Create Credentials"** → **OAuth client ID**
5. If prompted, configure the OAuth consent screen first:
   - Choose "External" user type
   - Fill in the required fields (App name, User support email, etc.)
   - Add "Test users" (your email) if needed
6. Create OAuth client ID:
   - Application type: **Web application**
   - Name: `Code Audit Platform`
   - Authorized redirect URIs:
     ```
     http://localhost:5172/auth/callback
     ```
   - Click **Create**
7. Copy the **Client ID** and **Client Secret**

### Complete Google Setup in Supabase

1. Go back to Supabase → Authentication → Providers → Google
2. Paste the **Client ID** from Google Cloud Console
3. Paste the **Client Secret** from Google Cloud Console
4. Add the redirect URL: `http://localhost:5172/auth/callback`
5. Click **Save**

---

## Step 3: Get Supabase Credentials

1. In Supabase, go to **Project Settings** → **API**
2. You'll see three important values:

### Required Environment Variables

Add these to your `backend/.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**Notes:**
- **SUPABASE_URL**: Your project URL
- **SUPABASE_ANON_KEY**: Public key (safe to expose)
- **SUPABASE_SERVICE_ROLE_KEY**: Secret key (NEVER commit to git!)

---

## Step 4: Update Backend Configuration

1. Copy the Supabase credentials to `backend/.env`:

```bash
cd backend
cp .env.example .env
# Edit .env and add your Supabase credentials
```

2. Your `backend/.env` should look like:

```bash
# ===========================================
# Application Configuration
# ===========================================
APP_NAME="Code Audit API"
DEBUG=true

# ===========================================
# Database
# ===========================================
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/codeaudit

# ===========================================
# Redis
# ===========================================
REDIS_URL=redis://localhost:6379/0

# ===========================================
# Security
# ===========================================
# Generate with: openssl rand -hex 32
SECRET_KEY=your-secret-key-here

# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-fernet-key-here

# ===========================================
# Supabase (Google OAuth)
# ===========================================
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# ===========================================
# CORS
# ===========================================
CORS_ORIGINS=["http://localhost:5172","http://localhost:5172"]
```

---

## Step 5: Update Frontend Configuration

1. Copy Supabase credentials to `frontend/.env`:

```bash
cd frontend
# Create or edit .env
```

2. Your `frontend/.env` should look like:

```bash
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## Step 6: Test the Setup

### Option A: Docker with Hot Reload (Recommended)

```bash
# 1. Create .env files from examples
make setup

# 2. Edit .env files with your Supabase credentials
#    - backend/.env
#    - frontend/.env

# 3. Start everything (migrations run automatically!)
make up-docker-dev
```

That's it! Services are now running with hot reload:
- Backend:  http://localhost:8000 (auto-reloads on code change)
- Frontend: http://localhost:5172 (Vite HMR)
- API Docs: http://localhost:8000/docs

### Option B: Production Docker (No Hot Reload)

```bash
make up
```

### Option C: Local Development (No Docker)

```bash
make setup-local
make dev
```

### Test Google OAuth

1. Open http://localhost:5172 in your browser
2. Click "Login with Google"
3. You should be redirected to Google's OAuth page
4. After authorizing, you should be redirected back to the app

---

## Troubleshooting

### "Invalid token" error

- Verify your `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are correct
- Check that Google OAuth is enabled in Supabase
- Verify the redirect URL matches exactly

### "Redirect URI mismatch" error

- Make sure the redirect URL in Google Cloud Console matches: `http://localhost:5172/auth/callback`
- Check for trailing slashes or protocol mismatches (http vs https)

### User not being created in database

- Check the backend logs: `make logs-backend`
- Verify the database connection is working
- Migrations run automatically - check startup logs
- Ensure Supabase credentials are correct in backend/.env

### Migrations failing

```bash
# Check backend logs
make logs-backend

# Reset database if needed
make db-reset

# Or manually run migrations
make db-migrate
```

---

## Production Deployment

For production, you'll need to:

1. **Update redirect URLs** in Google Cloud Console:
   ```
   https://yourdomain.com/auth/callback
   ```

2. **Update CORS origins** in backend config:
   ```bash
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

3. **Use HTTPS** for all production URLs

4. **Rotate your service role key** after initial setup

---

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
