# VidSquad Frontend V1 - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd vidSkuad/frontend
npm install
```

### 2. Configure Firebase
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing one
3. Enable Authentication (Email/Password + Google)
4. Copy your Firebase config
5. Update `.env` file with your Firebase credentials

### 3. Configure Backend URL
Update `.env` file:
```
VITE_API_URL=http://localhost:8000
```

### 4. Run Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## V1 Flow

1. **Auth Screen** - Login/Signup with Email or Google
2. **Input Screen** - Enter script idea (200+ chars) or paste full script
3. **Progress Screen** - Real-time progress updates from backend
4. **Download Screen** - Download Premiere Pro or CapCut project files

## Features

- Firebase Authentication (Email + Google)
- Real-time progress tracking via WebSocket
- Premiere Pro XML export
- CapCut project export
- Auto-expiring downloads (20 minutes)
- Beautiful animated UI with motion effects

## Backend Integration

The frontend connects to the FastAPI backend at `/api/videos/generate` and polls `/api/videos/status/{job_id}` for progress updates.

Make sure the backend is running on port 8000 before testing the full flow.

## Build for Production

```bash
npm run build
```

The production build will be in the `dist/` folder.
