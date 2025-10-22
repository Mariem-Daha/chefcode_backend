# Deploy ChefCode Backend to Google Cloud Run

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK (gcloud CLI)** installed
   - Download: https://cloud.google.com/sdk/docs/install
3. **Docker** installed (optional, for local testing)

## Quick Deployment Steps

### 1. Install Google Cloud SDK

**Windows:**
```powershell
# Download and run the installer
# https://cloud.google.com/sdk/docs/install#windows
```

**Or use PowerShell:**
```powershell
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

### 2. Authenticate and Setup

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Deploy to Cloud Run

**Option A: One-Command Deploy (Recommended)**

```bash
cd Backend

gcloud run deploy chefcode-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --set-env-vars ENVIRONMENT=production,ALLOWED_ORIGINS=*
```

**Option B: Build and Deploy Separately**

```bash
# Build the container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/chefcode-backend

# Deploy to Cloud Run
gcloud run deploy chefcode-backend \
  --image gcr.io/YOUR_PROJECT_ID/chefcode-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi
```

### 4. Set Environment Variables

After deployment, add your environment variables:

```bash
gcloud run services update chefcode-backend \
  --region us-central1 \
  --set-env-vars PROJECT_ID=your-project-id,LOCATION=us,PROCESSOR_ID=your-processor-id,GEMINI_API_KEY=your-gemini-key,OPENAI_API_KEY=your-openai-key,ALLOWED_ORIGINS=*
```

**Or set them one by one:**

```bash
gcloud run services update chefcode-backend --region us-central1 \
  --update-env-vars PROJECT_ID=your-gcp-project-id

gcloud run services update chefcode-backend --region us-central1 \
  --update-env-vars LOCATION=us

gcloud run services update chefcode-backend --region us-central1 \
  --update-env-vars PROCESSOR_ID=your-processor-id

gcloud run services update chefcode-backend --region us-central1 \
  --update-env-vars GEMINI_API_KEY=your-gemini-api-key

gcloud run services update chefcode-backend --region us-central1 \
  --update-env-vars OPENAI_API_KEY=your-openai-api-key
```

### 5. Get Your Backend URL

```bash
gcloud run services describe chefcode-backend --region us-central1 --format 'value(status.url)'
```

Your backend will be available at: `https://chefcode-backend-xxxxx-uc.a.run.app`

## Google Cloud Credentials Setup

For OCR features, Cloud Run can use the default service account credentials automatically. No need to upload `invoice_key.json`!

**If you need a specific service account:**

1. Create a service account key
2. Upload it as a secret:

```bash
# Create secret
gcloud secrets create invoice-key --data-file=invoice_key.json

# Grant access to Cloud Run service
gcloud secrets add-iam-policy-binding invoice-key \
  --member=serviceAccount:YOUR-PROJECT-NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Update Cloud Run to use the secret
gcloud run services update chefcode-backend \
  --region us-central1 \
  --update-secrets GOOGLE_APPLICATION_CREDENTIALS=/secrets/invoice-key:latest
```

## Test Your Deployment

```bash
# Get the URL
URL=$(gcloud run services describe chefcode-backend --region us-central1 --format 'value(status.url)')

# Test health endpoint
curl $URL/health

# Test API docs
open $URL/docs  # or visit in browser
```

## Update Frontend Configuration

Update your frontend to use the new Google Cloud Run URL:

**frontend/assets/config.js:**
```javascript
window.CONFIG = {
    API_BASE_URL: 'https://chefcode-backend-xxxxx-uc.a.run.app'
};
```

**frontend/mobile/src/BackendConfig.js:**
```javascript
const API_BASE_URL = 'https://chefcode-backend-xxxxx-uc.a.run.app';
```

## Cost Estimates

**Google Cloud Run Pricing (Free Tier):**
- ✅ **2 million requests/month FREE**
- ✅ **360,000 GB-seconds/month FREE**
- ✅ **180,000 vCPU-seconds/month FREE**

For most small to medium apps, you'll stay within the free tier!

## Redeploy After Changes

```bash
cd Backend
git pull  # if using git

# Rebuild and deploy
gcloud run deploy chefcode-backend \
  --source . \
  --region us-central1
```

## View Logs

```bash
gcloud run services logs read chefcode-backend --region us-central1
```

## Troubleshooting

### Build Fails
```bash
# Check build logs
gcloud builds list

# View specific build
gcloud builds log BUILD_ID
```

### Service Won't Start
```bash
# Check service logs
gcloud run services logs read chefcode-backend --region us-central1 --limit 100
```

### Update Memory/CPU
```bash
gcloud run services update chefcode-backend \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2
```

## Production Checklist

- [ ] Deploy to Cloud Run
- [ ] Set all environment variables
- [ ] Test all API endpoints
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring and alerts
- [ ] Enable Cloud SQL for production database (optional)
- [ ] Update CORS allowed origins to your frontend domain

## Next Steps

1. **Custom Domain**: Map your own domain to Cloud Run
2. **Cloud SQL**: Use Cloud SQL PostgreSQL for production database
3. **Monitoring**: Set up Cloud Monitoring and logging
4. **CI/CD**: Automate deployments with Cloud Build triggers

---

**Your ChefCode backend is now running on Google Cloud! 🚀**

Free tier should cover most usage, and scaling is automatic!
