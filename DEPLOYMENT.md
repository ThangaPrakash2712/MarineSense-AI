# 🚀 MarineSense AI - Deployment Guide

## Deployment Options

This guide covers multiple deployment strategies for MarineSense AI.

---

## Option 1: Streamlit Cloud (Recommended for Quick Deploy)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit - MarineSense AI v2.0"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
- Go to https://share.streamlit.io
- Click "New app"
- Select your repository
- Set main file path: `app/app.py`
- Click "Deploy"

3. **Configure Secrets** (if needed)
- Go to App Settings → Secrets
- Add any API keys or credentials

### Pros
- Free hosting
- Automatic updates from GitHub
- Easy to manage
- Built-in SSL

### Cons
- Limited resources on free tier
- Public by default

---

## Option 2: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for cartopy
RUN apt-get update && apt-get install -y \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the app
ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t marinesense-ai:v2.0 .

# Run container
docker run -p 8501:8501 marinesense-ai:v2.0
```

### Docker Compose (Optional)

```yaml
version: '3.8'

services:
  marinesense:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - STREAMLIT_SERVER_PORT=8501
    restart: unless-stopped
```

Run with: `docker-compose up -d`

---

## Option 3: AWS Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (minimum)
   - Security Group: Allow port 8501

2. **Connect and Setup**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv -y

# Clone repository
git clone <your-repo-url>
cd MarineSense-AI

# Setup virtual environment
python3 -m venv marine_env
source marine_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with nohup
nohup streamlit run app/app.py --server.port 8501 --server.address 0.0.0.0 &
```

3. **Access Application**
   - URL: http://your-ec2-ip:8501

### AWS Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize EB**
```bash
eb init -p python-3.11 marinesense-ai
```

3. **Create Environment**
```bash
eb create marinesense-production
```

4. **Deploy**
```bash
eb deploy
```

---

## Option 4: Google Cloud Platform

### Cloud Run (Serverless)

1. **Create Dockerfile** (see Option 2)

2. **Build and Push**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/marinesense-ai

gcloud run deploy marinesense-ai \
  --image gcr.io/YOUR_PROJECT_ID/marinesense-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Compute Engine (VM)

Similar to AWS EC2 - launch VM and follow setup steps.

---

## Option 5: Azure Deployment

### Azure App Service

1. **Create App Service**
```bash
az webapp up --name marinesense-ai --runtime "PYTHON:3.11"
```

2. **Configure Startup**
- Startup command: `streamlit run app/app.py --server.port 8000`

3. **Deploy**
```bash
az webapp deployment source config-zip \
  --resource-group myResourceGroup \
  --name marinesense-ai \
  --src marinesense.zip
```

---

## Option 6: Heroku

### Setup

1. **Create Procfile**
```
web: streamlit run app/app.py --server.port=$PORT --server.address=0.0.0.0
```

2. **Create setup.sh**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

3. **Deploy**
```bash
heroku create marinesense-ai
git push heroku main
```

---

## Production Configuration

### Streamlit Config (.streamlit/config.toml)

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Environment Variables

```bash
# Optional: Set in production
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## Performance Optimization

### 1. Model Loading
- Models are cached with `@st.cache_resource`
- Load once, reuse across sessions

### 2. Data Loading
- SST data cached with `@st.cache_data`
- Consider using parquet format for large datasets

### 3. SHAP Computation
- Cached to avoid recomputation
- Consider pre-computing for common scenarios

### 4. Memory Management
```python
# Add to config
[server]
maxMessageSize = 200
```

---

## Monitoring & Logging

### Basic Logging

Add to app.py:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marinesense.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Health Check Endpoint

For Docker/Kubernetes:
```python
# Streamlit provides: /_stcore/health
```

---

## Security Best Practices

1. **Environment Variables**
   - Never commit API keys
   - Use `.env` files (add to .gitignore)
   - Use secrets management in production

2. **HTTPS**
   - Always use SSL in production
   - Use reverse proxy (nginx) if needed

3. **Authentication** (Optional)
   - Add Streamlit authentication
   - Use OAuth for enterprise

4. **Input Validation**
   - Already implemented in app
   - Validate all user inputs

---

## Backup & Recovery

### Backup Models
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf models_backup_$DATE.tar.gz models/
aws s3 cp models_backup_$DATE.tar.gz s3://your-bucket/backups/
```

### Backup Data
```bash
# Backup processed data
tar -czf data_backup_$DATE.tar.gz data/processed/
```

---

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx, AWS ALB)
- Deploy multiple instances
- Share models via S3/GCS

### Vertical Scaling
- Increase instance size
- More RAM for larger models
- GPU for SHAP computation (optional)

---

## Cost Estimation

### Streamlit Cloud
- Free tier: 1 app, limited resources
- Team tier: $250/month (5 apps)

### AWS EC2
- t3.medium: ~$30/month
- t3.large: ~$60/month
- + Data transfer costs

### Google Cloud Run
- Pay per request
- ~$10-50/month for moderate traffic

### Heroku
- Free tier: Limited hours
- Hobby: $7/month
- Standard: $25/month

---

## Maintenance

### Regular Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update models (when retrained)
cp new_models/*.pkl models/

# Restart service
systemctl restart marinesense  # or docker restart
```

### Monitoring Checklist
- [ ] Check application logs daily
- [ ] Monitor resource usage
- [ ] Verify model predictions
- [ ] Check for errors/warnings
- [ ] Update dependencies monthly

---

## Troubleshooting

### Issue: Out of Memory
**Solution:** Increase instance size or optimize caching

### Issue: Slow Loading
**Solution:** Pre-load models, optimize data loading

### Issue: Port Already in Use
**Solution:** Change port or kill existing process

### Issue: Model Not Found
**Solution:** Verify model paths, check file permissions

---

## Support & Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Docker Docs:** https://docs.docker.com
- **AWS Docs:** https://docs.aws.amazon.com
- **GCP Docs:** https://cloud.google.com/docs

---

**Choose the deployment option that best fits your needs and budget! 🚀**

For most users, **Streamlit Cloud** is the easiest starting point.
For production enterprise use, consider **AWS/GCP with Docker**.
