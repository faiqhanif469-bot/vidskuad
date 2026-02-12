# API Documentation for Frontend Integration

Base URL: `https://api.yourdomain.com` (or `http://localhost:8000` for local)

---

## Authentication

All endpoints (except `/health`) require Firebase authentication token in header:

```javascript
headers: {
  'Authorization': 'Bearer <firebase_token>',
  'Content-Type': 'application/json'
}
```

---

## Endpoints

### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "api": "running",
    "redis": "connected",
    "celery": "running"
  }
}
```

---

### 2. Verify Token

```http
POST /api/auth/verify
```

**Body:**
```json
{
  "token": "firebase_id_token"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "abc123",
  "email": "user@example.com"
}
```

---

### 3. Get Current User

```http
GET /api/auth/me
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user_id": "abc123",
  "email": "user@example.com",
  "subscription_tier": "free",
  "videos_created_this_month": 2,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### 4. Generate Video (Main Endpoint)

```http
POST /api/videos/generate
```

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "script": "Your video script here...",
  "duration": 60,
  "title": "My Video Title"
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "celery_task_id",
  "status": "queued",
  "message": "Video generation started. Check status with /api/videos/status/{job_id}"
}
```

---

### 5. Check Job Status

```http
GET /api/videos/status/{job_id}
```

**Headers:** `Authorization: Bearer <token>`

**Response (Processing):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "current_step": "Downloading videos...",
  "eta_seconds": 120,
  "error": null,
  "result": null
}
```

**Response (Completed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "current_step": "Completed",
  "eta_seconds": 0,
  "error": null,
  "result": {
    "premiere_url": "https://spaces.digitalocean.com/.../premiere.zip",
    "capcut_url": "https://spaces.digitalocean.com/.../capcut.zip",
    "clips_count": 5,
    "images_count": 3,
    "expires_at": "2024-01-01T01:00:00Z"
  }
}
```

**Status Values:**
- `queued` - Job is in queue
- `processing` - Job is being processed
- `completed` - Job finished successfully
- `failed` - Job failed (check `error` field)

---

### 6. Get Download Links

```http
GET /api/videos/download/{job_id}
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "premiere_url": "https://spaces.digitalocean.com/.../premiere.zip",
  "capcut_url": "https://spaces.digitalocean.com/.../capcut.zip",
  "expires_at": "2024-01-01T01:00:00Z",
  "clips_count": 5,
  "images_count": 3
}
```

---

### 7. List User Projects

```http
GET /api/projects/
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "My Video",
      "status": "completed",
      "progress": 100,
      "created_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:05:00Z"
    }
  ],
  "total": 1
}
```

---

### 8. Get Queue Status

```http
GET /api/videos/queue/status
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "pending_jobs": 5,
  "processing_jobs": 4,
  "completed_jobs": 120,
  "failed_jobs": 2,
  "estimated_wait_time_seconds": 300
}
```

---

### 9. Generate Single Image

```http
POST /api/images/generate
```

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "prompt": "A rocket launching into space, photorealistic",
  "provider": "cloudflare"
}
```

**Response:**
```json
{
  "success": true,
  "image_id": "abc123",
  "image_url": "https://spaces.digitalocean.com/.../image.jpg",
  "prompt": "A rocket launching into space, photorealistic"
}
```

---

### 10. WebSocket (Real-time Progress)

```javascript
const ws = new WebSocket('ws://api.yourdomain.com/ws/progress/{job_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
  console.log('Status:', data.status);
  console.log('Step:', data.current_step);
};
```

**WebSocket Messages:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "current_step": "Downloading videos...",
  "eta_seconds": 120,
  "error": null,
  "result": null
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid token"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 429 Rate Limit
```json
{
  "detail": "Rate limit exceeded. Upgrade to create more videos. (5/5)"
}
```

### 500 Server Error
```json
{
  "error": "Internal server error",
  "message": "Error details..."
}
```

---

## Frontend Integration Example (React)

```javascript
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Login
const login = async (email, password) => {
  const userCredential = await signInWithEmailAndPassword(auth, email, password);
  const token = await userCredential.user.getIdToken();
  return token;
};

// Generate Video
const generateVideo = async (script, duration) => {
  const token = await auth.currentUser.getIdToken();
  
  const response = await fetch('https://api.yourdomain.com/api/videos/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ script, duration })
  });
  
  const data = await response.json();
  return data.job_id;
};

// Check Status (Polling)
const checkStatus = async (jobId) => {
  const token = await auth.currentUser.getIdToken();
  
  const response = await fetch(`https://api.yourdomain.com/api/videos/status/${jobId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};

// WebSocket (Real-time)
const connectWebSocket = (jobId) => {
  const ws = new WebSocket(`ws://api.yourdomain.com/ws/progress/${jobId}`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
  };
  
  return ws;
};
```

---

## Rate Limits

### Free Tier
- 5 videos per month
- 100 API requests per minute

### Pro Tier ($19/month)
- 50 videos per month
- 500 API requests per minute

### Enterprise Tier ($49/month)
- Unlimited videos
- Unlimited API requests

---

## File Retention

- Generated files are kept for **20 minutes** after completion
- Download links expire after 20 minutes
- Users must download files before expiration

---

## Support

For API issues:
- Check `/health` endpoint
- Check response status codes
- Check error messages in response body
- Contact support with job_id for debugging
