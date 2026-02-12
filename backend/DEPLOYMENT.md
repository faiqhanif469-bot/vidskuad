# Production Deployment Guide

## DigitalOcean Setup ($29/month)

### 1. Create Droplet

```bash
# Choose:
- Image: Ubuntu 22.04 LTS
- Plan: Basic ($24/month)
  - 4GB RAM / 2 vCPUs / 80GB SSD
- Region: Choose closest to your users
- Authentication: SSH Key (recommended)
```

### 2. Create DigitalOcean Spaces

```bash
# In DigitalOcean Dashboard:
1. Create → Spaces
2. Choose region (same as Droplet)
3. Name: ai-video-production
4. Cost: $5/month
5. Generate API Keys (save these!)
```

### 3. Setup Firebase

```bash
# In Firebase Console:
1. Create new project
2. Enable Authentication (Email/Password)
3. Enable Firestore Database
4. Generate service account key
5. Download JSON credentials file
```

---

## Server Setup

### 1. Connect to Droplet

```bash
ssh root@your_droplet_ip
```

### 2. Install Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

### 3. Clone Repository

```bash
# Install git
apt install git -y

# Clone your repo
git clone https://github.com/yourusername/ai-video-production.git
cd ai-video-production/backend
```

### 4. Configure Environment

```bash
# Create .env file
nano .env
```

Add the following:

```env
# Firebase
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json

# DigitalOcean Spaces
DO_SPACES_KEY=your_spaces_key
DO_SPACES_SECRET=your_spaces_secret
DO_SPACES_REGION=nyc3
DO_SPACES_BUCKET=ai-video-production

# API Keys
GROQ_API_KEY=your_groq_key
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_token

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# CORS (add your frontend domain)
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
```

### 5. Upload Firebase Credentials

```bash
# On your local machine:
scp firebase-credentials.json root@your_droplet_ip:/root/ai-video-production/backend/

# On server:
mv firebase-credentials.json /root/ai-video-production/backend/
```

---

## Deploy Application

### 1. Build and Start Services

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Verify Services

```bash
# Check API
curl http://localhost:8000/health

# Check Redis
docker-compose exec redis redis-cli ping

# Check Celery workers
docker-compose exec worker celery -A app.workers.celery_app inspect active
```

---

## Setup Domain & SSL

### 1. Point Domain to Droplet

```bash
# In your domain registrar:
A Record: @ → your_droplet_ip
A Record: api → your_droplet_ip
```

### 2. Install SSL Certificate

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal is configured automatically
```

### 3. Update Nginx Config

```bash
nano nginx.conf
```

Update server_name to your domain.

```bash
# Reload Nginx
docker-compose restart nginx
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f redis
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
docker-compose restart worker
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Monitor Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check Docker stats
docker stats
```

### Cleanup Old Files

```bash
# Remove old temp files
rm -rf temp/*

# Prune Docker
docker system prune -a
```

---

## Scaling

### Add More Workers

```bash
# Edit docker-compose.yml
# Change worker replicas from 4 to 8

docker-compose up -d --scale worker=8
```

### Upgrade Droplet

```bash
# In DigitalOcean Dashboard:
1. Power off Droplet
2. Resize to 8GB RAM ($48/month)
3. Power on
4. Restart services
```

---

## Troubleshooting

### API Not Responding

```bash
# Check if running
docker-compose ps

# Check logs
docker-compose logs api

# Restart
docker-compose restart api
```

### Workers Not Processing Jobs

```bash
# Check worker logs
docker-compose logs worker

# Check Redis connection
docker-compose exec worker python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"

# Restart workers
docker-compose restart worker
```

### Out of Disk Space

```bash
# Check space
df -h

# Clean temp files
rm -rf temp/*

# Clean Docker
docker system prune -a

# Clean old logs
journalctl --vacuum-time=7d
```

### High Memory Usage

```bash
# Check memory
free -h

# Check Docker stats
docker stats

# Reduce worker replicas
docker-compose up -d --scale worker=2
```

---

## Backup

### Backup Firestore

```bash
# Firestore auto-backs up
# Manual export in Firebase Console:
# Firestore → Import/Export
```

### Backup Configuration

```bash
# Backup .env and configs
tar -czf backup-$(date +%Y%m%d).tar.gz .env docker-compose.yml nginx.conf

# Download to local
scp root@your_droplet_ip:/root/ai-video-production/backend/backup-*.tar.gz ./
```

---

## Cost Breakdown

```
DigitalOcean Droplet (4GB):  $24/month
DigitalOcean Spaces:         $5/month
Domain:                      $12/year (~$1/month)
SSL Certificate:             FREE (Let's Encrypt)
────────────────────────────────────────
Total:                       $30/month

API Costs (pay-as-you-go):
- Groq: FREE tier
- Cloudflare FLUX: FREE tier (80 images/day)
- Firebase: FREE tier (50K users)
```

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Check status: `docker-compose ps`
3. Restart services: `docker-compose restart`
4. Check resources: `docker stats`

---

## Next Steps

1. ✅ Deploy backend
2. ✅ Test API endpoints
3. ✅ Deploy frontend
4. ✅ Connect frontend to backend
5. ✅ Test full pipeline
6. ✅ Launch to users!
