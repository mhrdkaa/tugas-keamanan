# CryptoAuth API - Railway Deployment Guide

## Quick Start

### Prerequisites
- Railway account (https://railway.app)
- GitHub account with repo
- Git CLI

### Step 1: Push to GitHub

```bash
cd project-baru
git init
git add .
git commit -m "Initial commit: CryptoAuth API"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/project-baru.git
git push -u origin main
```

### Step 2: Deploy to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your `project-baru` repository
4. Railway auto-detects Python + Procfile
5. Click "Deploy"

### Step 3: Get Your URL

Once deployed, Railway gives you:
```
https://project-baru-production.up.railway.app
```

---

## API Endpoints

### Health Check
```bash
curl https://YOUR_URL/health
```

### Register User
```bash
curl -X POST https://YOUR_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"secure123"}'
```

### Login
```bash
curl -X POST https://YOUR_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"alice_secret_123"}'
```

Response:
```json
{
  "status": "success",
  "token": {...},
  "user_id": "alice",
  "expires_in": 3600
}
```

### Get Server Public Key
```bash
curl https://YOUR_URL/api/keys/public
```

### Verify Token
```bash
curl -X POST https://YOUR_URL/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token": {...}}'
```

### Send Encrypted Message
```bash
curl -X POST https://YOUR_URL/api/message/send \
  -H "Content-Type: application/json" \
  -d '{"token": {...}, "message":"Hello Server"}'
```

---

## Demo Users (Pre-registered)

| Username | Password |
|----------|----------|
| alice | alice_secret_123 |
| bob | bob_secret_456 |

---

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Test endpoint
curl http://localhost:5000/health
```

---

## Environment Variables

Railway automatically sets `PORT` environment variable.
App listens on: `0.0.0.0:$PORT`

---

## Files for Deployment

```
project-baru/
├── main.py              ← Flask app (entry point)
├── Procfile             ← Railway run command
├── runtime.txt          ← Python version
├── requirements.txt     ← Dependencies
├── crypto_auth/         ← Library code
└── README.md            ← Documentation
```

---

## Troubleshooting

### App crashes on startup
- Check logs: Railway Dashboard → Deployments → Logs
- Verify requirements.txt has all dependencies
- Test locally first: `python main.py`

### Port binding error
- Procfile should use `python main.py`
- App reads PORT from environment variable

### Import errors
- Ensure crypto_auth package is in same directory
- Check requirements.txt includes cryptography

---

## Next Steps (Production)

1. **Add Database**: Store users instead of in-memory dict
2. **Key Management**: Use Railway Postgres for secure key storage
3. **Rate Limiting**: Prevent brute force attacks
4. **CORS**: Configure allowed origins
5. **HTTPS**: Railway auto-enables SSL
6. **Monitoring**: Add logging/alerting

---

## Support

Issues? Check:
- Railway Docs: https://docs.railway.app
- Flask Docs: https://flask.palletsprojects.com
- This repo README.md
