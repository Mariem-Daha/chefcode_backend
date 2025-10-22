# ChefCode Backend - Render Deployment Quick Start

## ✅ Files Created

The following files have been created for your Render deployment:

1. **render.yaml** - Render Blueprint configuration (auto-detects deployment settings)
2. **build.sh** - Build script for installing dependencies
3. **.env.example** - Example environment variables template
4. **RENDER_DEPLOYMENT.md** - Complete deployment guide with troubleshooting
5. **database.py** - Updated to support both SQLite (local) and PostgreSQL (production)
6. **requirements.txt** - Added PostgreSQL support (psycopg2-binary)

## 🚀 Quick Deployment Steps

### 1. Push to GitHub (if you haven't already)

```bash
cd Backend
git init
git add .
git commit -m "Add Render deployment configuration"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy on Render

**Option A: Blueprint (Automated - Recommended)**

1. Go to https://dashboard.render.com/blueprints
2. Click **New Blueprint Instance**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and auto-configure everything
5. Add your API keys in the environment variables section
6. Click **Apply**

**Option B: Manual Setup**

1. Go to https://dashboard.render.com
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Root Directory**: `Backend` (if in subdirectory)
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (see below)
6. Click **Create Web Service**

### 3. Required Environment Variables

Set these in the Render dashboard under **Environment**:

```
ENVIRONMENT=production
OPENAI_API_KEY=your_openai_key_here (optional)
GEMINI_API_KEY=your_gemini_key_here (optional)
ALLOWED_ORIGINS=* (change to your frontend domain in production)
```

If using PostgreSQL:
- Render will automatically create and connect a PostgreSQL database
- The `DATABASE_URL` will be set automatically

### 4. Test Your Deployment

Once deployed, your backend URL will be: `https://YOUR-SERVICE-NAME.onrender.com`

Test these endpoints:
- Health: `https://YOUR-SERVICE-NAME.onrender.com/health`
- API Docs: `https://YOUR-SERVICE-NAME.onrender.com/docs`
- Root: `https://YOUR-SERVICE-NAME.onrender.com/`

### 5. Update Frontend

Update your frontend configuration to use the new backend URL:

**Web App** (`frontend/assets/config.js`):
```javascript
window.CONFIG = {
    API_BASE_URL: 'https://YOUR-SERVICE-NAME.onrender.com'
};
```

**Mobile App** (`frontend/mobile/src/BackendConfig.js`):
```javascript
const API_BASE_URL = 'https://YOUR-SERVICE-NAME.onrender.com';
```

## 📋 Database Options

### Option 1: PostgreSQL (Recommended for Production)

✅ Already configured in `render.yaml`
- Render will create a free PostgreSQL database
- Database URL is automatically set
- ⚠️ Free database expires after 90 days

### Option 2: SQLite (Simpler, Local Storage)

If you want to use SQLite only:
1. Remove the `databases:` section from `render.yaml`
2. Don't set `DATABASE_URL` environment variable
3. ⚠️ Data will be lost on service restarts

## ⚠️ Important Notes

### Free Tier Limitations
- Services sleep after 15 minutes of inactivity
- First request after sleep takes ~30-60 seconds
- Free PostgreSQL databases expire after 90 days
- Uploads folder is ephemeral (files are deleted on restart)

### Production Recommendations
1. **Keep service awake**: Use UptimeRobot to ping every 10 minutes
2. **Secure CORS**: Set `ALLOWED_ORIGINS` to your specific domain
3. **Upgrade for production**: $7/month for always-on service
4. **Cloud storage**: Use S3/Cloudinary for persistent file uploads
5. **Monitor logs**: Check Render dashboard regularly

## 🔧 Troubleshooting

### Build Fails
```bash
# Make sure build.sh is executable
chmod +x build.sh
git add build.sh
git commit -m "Make build.sh executable"
git push
```

### Service Won't Start
- Check that `uvicorn` command uses `$PORT` variable
- Verify all dependencies are in `requirements.txt`
- Check deploy logs in Render dashboard

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Ensure PostgreSQL database is in same region
- Check `psycopg2-binary` is installed

## 📚 Full Documentation

See **RENDER_DEPLOYMENT.md** for complete deployment guide with:
- Detailed step-by-step instructions
- Advanced configuration options
- Comprehensive troubleshooting guide
- Production deployment checklist

## 🎉 You're Ready!

Your backend is now configured for Render deployment. Just:
1. Push to GitHub
2. Deploy on Render
3. Update your frontend
4. Start using your cloud-hosted API!

Questions? Check the full documentation in `RENDER_DEPLOYMENT.md`
