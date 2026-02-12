# Quick Start Guide

## ✅ **YES! It's Ready for Frontend Integration**

---

## What You Have Now:

```
✅ FastAPI backend (production-ready)
✅ Celery workers (handles 100s of users)
✅ Redis queue (job management)
✅ Firebase auth (user management)
✅ DigitalOcean Spaces (file storage)
✅ Docker setup (easy deployment)
✅ Complete API (documented)
✅ WebSocket (real-time updates)
✅ Rate limiting (free/pro/enterprise tiers)
✅ Auto-cleanup (20-minute file retention)
```

---

## Local Development (Test Before Deploy)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
# Copy example env
cp .env.example .env

# Edit .env with your keys
nano .env
```

### 3. Start Redis

```bash
# Option A: Docker
docker run -d -p 6379:6379 redis:alpine

# Option B: Local install
# Windows: Download from https://redis.io/download
# Mac: brew install redis && redis-server
# Linux: sudo apt install redis-server && redis-server
```

### 4. Start FastAPI

```bash
# Terminal 1
uvicorn app.main:app --reload --port 8000
```

### 5. Start Celery Workers

```bash
# Terminal 2
celery -A app.workers.celery_app worker --loglevel=info --concurrency=2
```

### 6. Test API

```bash
# Check health
curl http://localhost:8000/health

# View docs
open http://localhost:8000/docs
```

---

## Frontend Integration

### 1. Install Firebase in Frontend

```bash
npm install firebase
```

### 2. Initialize Firebase

```javascript
// src/firebase.js
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "your_api_key",
  authDomain: "your_project.firebaseapp.com",
  projectId: "your_project_id",
  // ... other config
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

### 3. Create API Service

```javascript
// src/services/api.js
import { auth } from '../firebase';

const API_URL = 'http://localhost:8000'; // Change to production URL

export const generateVideo = async (script, duration) => {
  const token = await auth.currentUser.getIdToken();
  
  const response = await fetch(`${API_URL}/api/videos/generate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ script, duration })
  });
  
  return await response.json();
};

export const checkStatus = async (jobId) => {
  const token = await auth.currentUser.getIdToken();
  
  const response = await fetch(`${API_URL}/api/videos/status/${jobId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

### 4. Use in Component

```javascript
// src/components/VideoGenerator.jsx
import { useState } from 'react';
import { generateVideo, checkStatus } from '../services/api';

export default function VideoGenerator() {
  const [script, setScript] = useState('');
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  
  const handleGenerate = async () => {
    const result = await generateVideo(script, 60);
    setJobId(result.job_id);
    
    // Poll for status
    const interval = setInterval(async () => {
      const statusData = await checkStatus(result.job_id);
      setStatus(statusData);
      
      if (statusData.status === 'completed') {
        clearInterval(interval);
      }
    }, 2000);
  };
  
  return (
    <div>
      <textarea 
        value={script} 
        onChange={(e) => setScript(e.target.value)}
        placeholder="Enter your video script..."
      />
      <button onClick={handleGenerate}>Generate Video</button>
      
      {status && (
        <div>
          <p>Status: {status.status}</p>
          <p>Progress: {status.progress}%</p>
          <p>Step: {status.current_step}</p>
          
          {status.status === 'completed' && (
            <div>
              <a href={status.result.premiere_url}>Download Premiere Pro</a>
              <a href={status.result.capcut_url}>Download CapCut</a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## Production Deployment

### 1. Setup DigitalOcean

```bash
# Create Droplet (4GB RAM, $24/month)
# Create Spaces ($5/month)
# Get API keys
```

### 2. Setup Firebase

```bash
# Create Firebase project
# Enable Auth & Firestore
# Download service account JSON
```

### 3. Deploy

```bash
# SSH to server
ssh root@your_droplet_ip

# Clone repo
git clone your_repo_url
cd backend

# Setup environment
cp .env.example .env
nano .env  # Add your keys

# Upload Firebase credentials
# (upload firebase-credentials.json to server)

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### 4. Point Domain

```bash
# In domain registrar:
A Record: api.yourdomain.com → your_droplet_ip

# Install SSL
certbot --nginx -d api.yourdomain.com
```

### 5. Update Frontend

```javascript
// Change API_URL to production
const API_URL = 'https://api.yourdomain.com';
```

---

## Testing Checklist

### Backend Tests

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. API docs
open http://localhost:8000/docs

# 3. Generate video (with Firebase token)
curl -X POST http://localhost:8000/api/videos/generate \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"script":"Test script","duration":60}'

# 4. Check status
curl http://localhost:8000/api/videos/status/JOB_ID \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

### Frontend Tests

1. ✅ User can sign up/login
2. ✅ User can submit script
3. ✅ Progress updates in real-time
4. ✅ Download links work
5. ✅ Files expire after 20 minutes
6. ✅ Rate limiting works (5 videos for free tier)

---

## Monitoring

### Check Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

### Check Queue

```bash
# Redis CLI
docker-compose exec redis redis-cli

# Check queue length
LLEN celery

# Check active jobs
KEYS celery-task-meta-*
```

### Check Resources

```bash
# CPU/Memory
docker stats

# Disk space
df -h

# Clean up
docker system prune -a
```

---

## Troubleshooting

### API not responding
```bash
docker-compose restart api
docker-compose logs api
```

### Workers not processing
```bash
docker-compose restart worker
docker-compose logs worker
```

### Out of memory
```bash
# Reduce worker replicas
docker-compose up -d --scale worker=2
```

---

## Next Steps

1. ✅ Test locally
2. ✅ Build frontend
3. ✅ Deploy to DigitalOcean
4. ✅ Test production
5. ✅ Launch to users!

---

## Support

- API Docs: `/docs`
- Health Check: `/health`
- Deployment Guide: `DEPLOYMENT.md`
- API Reference: `API_DOCUMENTATION.md`

**You're ready to integrate with frontend!** 🚀
