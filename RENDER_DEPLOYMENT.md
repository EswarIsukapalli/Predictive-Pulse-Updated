# Deploying Predictive Pulse to Render

## Prerequisites
- GitHub account with your code pushed
- Render account (https://render.com)

## Steps

### 1. Connect Your Repository
- Go to https://dashboard.render.com
- Click "New +" → "Web Service"
- Connect your GitHub account
- Select the `Predictive-Pulse-Updated` repository

### 2. Configure the Service
Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | predictive-pulse |
| **Environment** | Python 3 |
| **Region** | Select closest to you |
| **Branch** | main |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn wsgi:app` |

### 3. Add Environment Variables
Click "Advanced" and add environment variables:

```
SECRET_KEY = (generate a random secure string)
PYTHON_VERSION = 3.11
```

### 4. Add PostgreSQL Database
- Click "Create Database"
- Choose "PostgreSQL"
- Plan: Free (or Starter if needed)
- Database name: predictive_pulse

### 5. Connect Database
- The DATABASE_URL will be automatically added to your web service
- Render will set this as an environment variable

### 6. Deploy
- Click "Deploy"
- Wait for the build to complete (5-10 minutes)

## Important Notes

✅ **Database**: Uses PostgreSQL in production (auto-created tables on startup)
✅ **Files**: Uses Render's file storage (temporary, reset on redeploy)
✅ **Port**: Automatically configured (no need to specify)

⚠️ **Limitations**:
- Free tier has 15-minute inactivity timeout
- Uploaded PDFs are temporary (not persisted)
- Database resets when service stops

## Testing Registration
1. Go to your Render URL: `https://your-app-name.onrender.com`
2. Click "Register"
3. Fill in username, email, password
4. Should redirect to login page
5. Login with your credentials
6. Should show prediction page

## Troubleshooting

### 500 Error on Registration
- Check Render logs: Dashboard → Logs
- Common issues:
  - DATABASE_URL not set (create PostgreSQL database)
  - Python version mismatch
  - Missing dependencies (check requirements.txt installed)

### Database Not Created
- SSH into Render instance
- Run: `python wsgi.py` (creates tables)

### Model Not Found
- Ensure `model.joblib` is in your GitHub repository
- Check file size limits

## Monitoring
- View logs: Dashboard → Your Service → Logs
- Check CPU/Memory: Dashboard → Metrics
