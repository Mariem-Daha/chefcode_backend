# Deploying ChefCode Backend to Render

This guide will help you deploy the ChefCode backend to Render, a cloud platform for hosting web applications.

## Prerequisites

- GitHub account
- Render account (free tier available at https://render.com)
- Your code pushed to a GitHub repository

## Deployment Steps

### 1. Prepare Your Code for Render

The following files have been created for Render deployment:
- ✅ `render.yaml` - Render Blueprint configuration
- ✅ `build.sh` - Build script for installing dependencies
- ✅ `.env.example` - Example environment variables

### 2. Update Database Configuration

The backend needs to support both SQLite (local) and PostgreSQL (production).

**Option A: Add PostgreSQL Support (Recommended)**

Update `requirements.txt` to include PostgreSQL:
```
psycopg2-binary==2.9.9
```

Update `database.py` to support both databases:
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use SQLite as fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chefcode.db")

# SQLite specific settings
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

**Option B: Use SQLite Only (Simpler, but not recommended for production)**

Remove the database section from `render.yaml` and Render will use the local filesystem (data will be lost on restarts).

### 3. Push to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 4. Deploy on Render

#### Method A: Using Blueprint (Recommended - Automated)

1. Go to https://dashboard.render.com
2. Click **New** → **Blueprint**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and set up:
   - Web Service (chefcode-backend)
   - PostgreSQL Database (chefcode-db) - if using Option A above
5. Click **Apply** to create the services

#### Method B: Manual Setup

1. **Create PostgreSQL Database** (if using PostgreSQL):
   - Go to https://dashboard.render.com
   - Click **New** → **PostgreSQL**
   - Name: `chefcode-db`
   - Plan: **Free**
   - Click **Create Database**
   - Copy the **Internal Database URL**

2. **Create Web Service**:
   - Click **New** → **Web Service**
   - Connect your GitHub repository
   - Configure:
     - **Name**: `chefcode-backend`
     - **Region**: Oregon (or closest to you)
     - **Branch**: `main`
     - **Root Directory**: `Backend` (if Backend is in a subdirectory)
     - **Runtime**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: **Free**

3. **Add Environment Variables**:
   - Click **Environment** tab
   - Add the following variables:
     - `ENVIRONMENT` = `production`
     - `DATABASE_URL` = (paste the Internal Database URL from step 1)
     - `OPENAI_API_KEY` = (your OpenAI API key - optional)
     - `GEMINI_API_KEY` = (your Gemini API key - optional)
     - `ALLOWED_ORIGINS` = `*` (or your frontend domain)

4. Click **Create Web Service**

### 5. Verify Deployment

After deployment completes (5-10 minutes):

1. Get your backend URL: `https://chefcode-backend.onrender.com`
2. Test the endpoints:
   - Health check: `https://chefcode-backend.onrender.com/health`
   - API docs: `https://chefcode-backend.onrender.com/docs`
   - Root: `https://chefcode-backend.onrender.com/`

### 6. Update Frontend Configuration

Update your frontend to use the new backend URL:

**For Web App** (`frontend/assets/config.js`):
```javascript
window.CONFIG = {
    API_BASE_URL: 'https://chefcode-backend.onrender.com'
};
```

**For Mobile App** (`frontend/mobile/src/BackendConfig.js`):
```javascript
const API_BASE_URL = 'https://chefcode-backend.onrender.com';
```

### 7. Configure CORS (Important!)

Once your frontend is deployed, update the `ALLOWED_ORIGINS` environment variable in Render:

```
ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000
```

This ensures only your frontend can access the backend.

## Important Notes

### Free Tier Limitations

Render's free tier has some limitations:
- **Automatic sleep**: Services sleep after 15 minutes of inactivity
- **Cold starts**: First request after sleep takes 30-60 seconds
- **Database**: 90-day expiration for free PostgreSQL databases
- **Hours**: 750 hours/month of uptime

### Keeping Service Active

To keep your service from sleeping:
1. Use a service like UptimeRobot (free) to ping your API every 10 minutes
2. Upgrade to a paid plan ($7/month) for always-on service

### Database Backups

Free PostgreSQL databases are **deleted after 90 days**. Options:
1. Upgrade to a paid database plan ($7/month)
2. Set up automatic backups using Render's backup feature
3. Manually export data periodically

### File Uploads

The `uploads/` directory is **ephemeral** on Render free tier. For production:
1. Use a cloud storage service (AWS S3, Cloudinary, etc.)
2. Upgrade to a persistent disk plan

## Troubleshooting

### Build Fails

1. Check build logs in Render dashboard
2. Verify `requirements.txt` has all dependencies
3. Ensure `build.sh` has execute permissions:
   ```bash
   chmod +x build.sh
   git add build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

### Service Won't Start

1. Check deploy logs in Render dashboard
2. Verify `DATABASE_URL` is set correctly
3. Check that port is using `$PORT` environment variable

### Database Connection Issues

1. Verify `DATABASE_URL` environment variable is set
2. Ensure `psycopg2-binary` is in `requirements.txt`
3. Check database is in the same region as web service

### CORS Errors

1. Check `ALLOWED_ORIGINS` environment variable
2. Update to include your frontend domain
3. Restart the service after changing environment variables

## Monitoring & Logs

- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Check CPU/memory usage in Metrics tab
- **Events**: See deployment history in Events tab

## Upgrading from Free Tier

When ready for production:
1. Upgrade web service to Starter ($7/month) for:
   - No sleeping
   - More CPU/RAM
   - Better performance
2. Upgrade database to Starter ($7/month) for:
   - No 90-day expiration
   - Automatic backups
   - More storage

## Support & Resources

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLAlchemy Documentation: https://docs.sqlalchemy.org

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Test API endpoints
3. ✅ Update frontend configuration
4. ✅ Test frontend-backend integration
5. ⬜ Deploy frontend (Netlify, Vercel, or Render)
6. ⬜ Configure custom domain (optional)
7. ⬜ Set up monitoring and alerts
8. ⬜ Implement proper error logging

Your ChefCode backend is now ready for deployment! 🚀
