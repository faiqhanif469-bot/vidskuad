# VidSquad Frontend - V1

AI Video Production Studio Frontend

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# Copy example env
cp .env.example .env

# Edit .env with your Firebase credentials
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:5173

## Project Structure

```
frontend/
├── src/
│   ├── services/
│   │   ├── firebase.ts      # Firebase config
│   │   ├── auth.ts          # Authentication
│   │   └── api.ts           # Backend API calls
│   ├── components/
│   │   ├── AuthScreen.tsx   # Login/Signup
│   │   ├── InputScreen.tsx  # Script input (from UI design)
│   │   ├── ProgressScreen.tsx # Progress indicator
│   │   ├── DownloadScreen.tsx # Download page
│   │   └── ui/              # UI components
│   ├── App.tsx              # Main app
│   └── main.tsx             # Entry point
├── package.json
├── vite.config.ts
└── .env
```

## Features

- ✅ Firebase Authentication (Email + Google)
- ✅ Script input with beautiful UI
- ✅ Real-time progress tracking
- ✅ Download Premiere Pro + CapCut projects
- ✅ Responsive design
- ✅ Dark theme

## Build for Production

```bash
npm run build
```

Output in `dist/` folder

## Deploy

### Vercel
```bash
npm install -g vercel
vercel
```

### Netlify
```bash
npm install -g netlify-cli
netlify deploy
```

## Environment Variables

Required for production:
- `VITE_API_URL` - Backend API URL
- `VITE_FIREBASE_*` - Firebase credentials

## Tech Stack

- React 18 + TypeScript
- Vite
- Tailwind CSS
- Firebase Auth
- Motion (animations)
- Lucide Icons
