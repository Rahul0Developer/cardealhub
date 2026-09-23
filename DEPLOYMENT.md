# 🚀 Complete Deployment Guide - Car Deal Hub

Comprehensive guide to deploy your Car Deal Hub application on **Render**, **Railway**, and **Fly.io**.

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Platform Comparison](#platform-comparison)
3. [Deploy on Render (Recommended)](#deploy-on-render-recommended)
4. [Deploy on Railway](#deploy-on-railway)
5. [Deploy on Fly.io](#deploy-on-flyio)
6. [Environment Variables](#environment-variables)
7. [Post-Deployment Tasks](#post-deployment-tasks)
8. [Troubleshooting](#troubleshooting)
9. [Monitoring & Maintenance](#monitoring--maintenance)

---

## ✅ Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] All code committed to Git
- [ ] `requirements.txt` is up-to-date
- [ ] Database models are defined in `models.py`
- [ ] `main.py` entry point works locally
- [ ] Static files are in `static/` directory
- [ ] Templates are in `templates/` directory
- [ ] `.gitignore` excludes sensitive files
- [ ] GitHub repository is created and pushed

### Verify Locally

```bash
# Test your app locally first
python main.py

# Or with gunicorn
gunicorn --config gunicorn.conf.py main:app
```

---

## 📊 Platform Comparison

| Feature | Render | Railway | Fly.io |
|---------|--------|---------|--------|
| **Free Tier** | ✅ Yes (with limitations) | ✅ $5 credit/month | ✅ 3 free VMs |
| **Setup Time** | 5 minutes | 10 minutes | 15 minutes |
| **Database** | PostgreSQL (90 days free) | PostgreSQL (included) | PostgreSQL (add-on) |
| **Auto-Deploy** | ✅ Yes (GitHub) | ✅ Yes (GitHub) | ❌ CLI only |
| **Sleep Mode** | ⚠️ Yes (free tier) | ❌ No | ❌ No |
| **Global Regions** | 6 regions | 5 regions | 30+ regions |
| **Best For** | Beginners, quick deploy | Full-stack apps | Global apps |

---

## 🎯 Deploy on Render (Recommended)

### Option A: One-Click Deploy with Blueprint

#### Step 1: Prepare Repository
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

#### Step 2: Connect to Render
1. Visit [render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Click **"New +"** → **"Blueprint"**
4. Select your repository
5. Choose the `render.yaml` file
6. Click **"Apply"**

Render will automatically:
- Create a PostgreSQL database
- Deploy the web service
- Configure environment variables

#### Step 3: Configure Database
After deployment completes:
1. Go to Dashboard → Your Database
2. Click **"Settings"** tab
3. Copy **"External Database URL"**
4. Go to Web Service → **"Environment"**
5. Add `DATABASE_URL` if not auto-configured

### Option B: Manual Deploy

#### Step 1: Create PostgreSQL Database
1. Log into [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name:** `car-deal-hub-db`
   - **Region:** Oregon (or closest to you)
   - **Plan:** Free
   - **Database Name:** `cardealhub`
4. Click **"Create Database"**
5. **Important:** Copy the **External Connection String**

#### Step 2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account
3. Select your repository
4. Configure:

| Setting | Value |
|---------|-------|
| Name | `car-deal-hub` |
| Region | Same as database |
| Branch | `main` |
| Root Directory | (leave blank) |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --config gunicorn.conf.py main:app` |
| Instance Type | **Free** |

#### Step 3: Add Environment Variables
Go to **"Environment"** tab and add:

```
DATABASE_URL=postgresql://user:password@host:port/database
SESSION_SECRET=your-random-secret-key-here
PYTHON_VERSION=3.11.0
```

#### Step 4: Deploy
- Click **"Create Web Service"**
- Wait for build (2-5 minutes)
- App is live at `https://car-deal-hub.onrender.com`

---

## 🚂 Deploy on Railway

### Step 1: Sign Up
1. Visit [railway.app](https://railway.app)
2. Login with GitHub
3. You get $5 free credit/month

### Step 2: Create Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository

### Step 3: Configure Service
Railway auto-detects Python apps, but verify:

1. Go to your service
2. Click **"Settings"** tab
3. Set:
   - **Start Command:** `gunicorn --config gunicorn.conf.py main:app`
   - **Build Command:** `pip install -r requirements.txt`

### Step 4: Add Database
1. Click **"New"** → **"Database"** → **"PostgreSQL"**
2. Wait for provisioning
3. Copy the `DATABASE_URL` from variables

### Step 5: Add Environment Variables
In **"Variables"** tab, add:

```
DATABASE_URL=<paste from database>
SESSION_SECRET=random-secret-key
PYTHON_VERSION=3.11
```

### Step 6: Deploy
- Railway auto-deploys on push
- Click **"Deploy"** manually if needed
- Get your URL from **"Settings"** → **"Domains"**

---

## 🪂 Deploy on Fly.io

### Step 1: Install Fly CLI
```bash
# macOS
brew install flyctl

# Windows
winget install fly-io.flyctl

# Linux
curl -L https://fly.io/install.sh | sh
```

### Step 2: Authenticate
```bash
fly auth signup
fly auth login
```

### Step 3: Launch App
```bash
cd /workspace
fly launch --name car-deal-hub
```

Follow prompts:
- **Organization:** Your personal org
- **App Name:** `car-deal-hub`
- **Region:** Choose closest
- **Deploy now:** No (we'll configure first)

### Step 4: Configure for Python
Edit `fly.toml`:

```toml
[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  http_checks = []
  internal_port = 8080
  protocol = "tcp"
  
  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
  
  [[services.ports]]
    handlers = ["http"]
    port = 80
  
  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

### Step 5: Create Database
```bash
fly postgres create --name car-deal-hub-db
fly postgres attach --app car-deal-hub car-deal-hub-db
```

### Step 6: Set Secrets
```bash
fly secrets set SESSION_SECRET=your-random-secret-key
```

### Step 7: Deploy
```bash
fly deploy
```

### Step 8: Open App
```bash
fly open
```

---

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `SESSION_SECRET` | Flask session encryption key | `my-super-secret-key-123` |
| `PYTHON_VERSION` | Python version | `3.11.0` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_UPLOAD_SIZE` | Max file upload size | `16MB` |

### Getting DATABASE_URL Format

```
postgresql://username:password@hostname:port/database_name
```

Example (Render):
```
postgresql://cardealhub_user:abc123xyz@db-car-deal-hub-abc.render.net:5432/cardealhub
```

---

## ✅ Post-Deployment Tasks

### 1. Verify Deployment
```bash
# Test homepage
curl https://car-deal-hub.onrender.com

# Test API endpoints
curl https://car-deal-hub.onrender.com/api/cars
```

### 2. Create Admin User
```bash
# SSH into server (if available) or use reset script
python reset_admin.py
```

Or via admin panel if accessible.

### 3. Run Database Migrations
```bash
# If using migration scripts
python db_migrate.py
```

### 4. Test All Features
- [ ] User registration
- [ ] User login
- [ ] Car prediction
- [ ] Admin dashboard
- [ ] File uploads
- [ ] Database queries

### 5. Set Up Monitoring
- **UptimeRobot:** Free monitoring every 5 minutes
- **Render Dashboard:** Built-in logs and metrics
- **Sentry:** Error tracking (optional)

---

## 🔧 Troubleshooting

### Build Fails

**Error: Module not found**
```bash
# Solution: Update requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Fix dependencies"
git push
```

**Error: Python version mismatch**
```yaml
# In render.yaml or environment variables
PYTHON_VERSION: 3.11.0
```

### Database Connection Errors

**Error: Connection refused**
- Check DATABASE_URL format
- Ensure database is in same region
- Verify firewall allows connections
- Restart both database and web service

**Error: Authentication failed**
- Reset database password
- Update DATABASE_URL
- Check for special characters in password (URL encode)

### App Crashes on Startup

**Check logs:**
```bash
# Render
render logs -s car-deal-hub

# Railway
railway logs

# Fly.io
fly logs
```

**Common issues:**
- Missing environment variables
- Database not ready
- Port binding issues
- Import errors

### App Goes to Sleep (Render Free Tier)

**Solution 1: UptimeRobot**
1. Create free account at [uptimerobot.com](https://uptimerobot.com)
2. Add new monitor
3. URL: `https://car-deal-hub.onrender.com`
4. Interval: 5 minutes
5. Monitor type: HTTP(s)

**Solution 2: Upgrade Plan**
- Render Pro: $7/month (no sleep)
- Railway: Pay per use
- Fly.io: Paid tiers available

### Slow Performance

**Optimize:**
- Enable database connection pooling
- Use Redis for caching (optional)
- Optimize static file serving
- Consider CDN for static assets

---

## 📊 Monitoring & Maintenance

### Daily Checks
- [ ] App is responding
- [ ] No error spikes in logs
- [ ] Database connections healthy

### Weekly Tasks
- [ ] Review error logs
- [ ] Check disk usage
- [ ] Verify backups working

### Monthly Tasks
- [ ] Update dependencies
- [ ] Review performance metrics
- [ ] Backup database
- [ ] Security audit

### Backup Strategies

**Render (Free - 90 days):**
```bash
# Manual backup
pg_dump $DATABASE_URL > backup.sql
```

**Automated Backup Script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://your-bucket/backups/
```

---

## 🎯 Platform-Specific Tips

### Render
- Use Blueprints for infrastructure-as-code
- Free databases expire after 90 days
- Auto-SSL certificates included
- Easy rollbacks from dashboard

### Railway
- $5 free credit resets monthly
- Automatic deploys on git push
- Built-in environment variable management
- Easy database provisioning

### Fly.io
- Best global coverage (30+ regions)
- CLI-first workflow
- Persistent volumes available
- Great for Docker-based apps

---

## 📞 Support Resources

- **Render Docs:** https://render.com/docs
- **Railway Docs:** https://docs.railway.app
- **Fly.io Docs:** https://fly.io/docs
- **Flask Docs:** https://flask.palletsprojects.com
- **Gunicorn Docs:** https://docs.gunicorn.org

---

## 🎉 Success!

Your Car Deal Hub is now deployed! Share your link:
- `https://car-deal-hub.onrender.com` (Render)
- `https://car-deal-hub.railway.app` (Railway)
- `https://car-deal-hub.fly.dev` (Fly.io)

**Happy deploying! 🚀**
