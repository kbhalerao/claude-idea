# Chief of Staff API - Deployment to macstudio

## Prerequisites

- Docker installed on macstudio
- Access to Couchbase at `macstudio.local:8091`
- `chief_of_staff` bucket created in Couchbase
- User exists in `users` bucket (e.g., `kaustubh@codesmriti.dev`)

## Step 1: Transfer to macstudio

```bash
# From your local machine
cd /Users/kaustubh/claude-idea
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.pytest_cache' \
  chief-of-staff/ macstudio.local:~/chief-of-staff/
```

Or clone from git:
```bash
ssh macstudio.local
cd ~
git clone <repo-url> chief-of-staff
cd chief-of-staff
```

## Step 2: Configure on macstudio

```bash
ssh macstudio.local
cd ~/chief-of-staff

# Create .env from example
cp .env.example .env

# Edit with your Couchbase password
nano .env
```

Set these values in `.env`:
```
COS_COUCHBASE_HOST=localhost  # or macstudio.local if running elsewhere
COS_COUCHBASE_PASSWORD=your_actual_password
COS_DEFAULT_USER=kaustubh@codesmriti.dev
```

## Step 3: Build and Run with Docker

```bash
cd ~/chief-of-staff

# Build the image
docker build -t chief-of-staff:latest .

# Run the container
docker run -d \
  --name cos-api \
  --restart unless-stopped \
  --network host \
  --env-file .env \
  chief-of-staff:latest

# Or use docker-compose
docker-compose up -d
```

## Step 4: Verify

```bash
# Check container is running
docker ps | grep cos-api

# Check logs
docker logs cos-api

# Test health endpoint
curl http://localhost:8000/api/cos/health

# Test with user header
curl -H "X-User-ID: kaustubh@codesmriti.dev" http://localhost:8000/api/cos/docs
```

## Step 5: Integrate with Existing API Gateway

If integrating with the existing CodeSmriti API server, you have two options:

### Option A: Reverse Proxy (Recommended)

Add to your nginx/traefik config to route `/api/cos/*` to the CoS container:

```nginx
location /api/cos/ {
    proxy_pass http://localhost:8000/api/cos/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-User-ID $http_x_user_id;
}
```

### Option B: Mount as Router in Existing FastAPI

In your existing CodeSmriti API:

```python
# In main.py of existing API
from cos.router import router as cos_router

app.include_router(cos_router)
```

This requires installing the `cos` package in your existing API environment.

## Useful Commands

```bash
# Stop container
docker stop cos-api

# Remove container
docker rm cos-api

# Rebuild after changes
docker build -t chief-of-staff:latest . && docker-compose up -d

# View logs
docker logs -f cos-api

# Shell into container
docker exec -it cos-api /bin/bash
```

## Troubleshooting

### Connection refused to Couchbase
- Check `COS_COUCHBASE_HOST` in `.env`
- If using `--network host`, use `localhost`
- If using bridge network, use `host.docker.internal` or the host IP

### User not found
- Verify user exists in `users` bucket with matching email
- Check the query: `SELECT * FROM users WHERE email = "your@email.com"`

### Scope creation fails
- Ensure Couchbase user has permissions to create scopes/collections
- Check Couchbase logs for errors
