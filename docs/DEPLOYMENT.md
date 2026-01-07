# Perplexity-like AI Search - Deployment Guide

This guide explains how to deploy the SECI Perplexity-like AI search system on your VPS.

## Prerequisites

- Ubuntu/Debian VPS with Python 3.8+
- At least 2GB RAM
- Domain name (optional but recommended)
- SSL certificate (for HTTPS)

## Installation Steps

### 1. Update System and Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install git build-essential -y
```

### 2. Clone Repository

```bash
# Clone the repository
cd /opt
sudo git clone https://github.com/AkshatNaruka/ai.git
cd ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install the package
pip install -e .
```

### 4. Configure the System

Create a configuration file `config/search_config.yaml`:

```yaml
# Search configuration
search:
  providers:
    - duckduckgo  # No API key needed
    - google      # Optional
  max_results: 10
  timeout: 10
  cache_ttl: 3600

# Scraper configuration
scraper:
  timeout: 10
  max_content_length: 50000
  user_agent: "SECI-Search-Bot/1.0"

# Context management
context:
  max_history: 20
  max_sessions: 1000

# API server
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  log_level: "info"
```

### 5. Run the API Server

#### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with uvicorn
python api.py
```

#### Production Mode with Systemd

Create a systemd service file `/etc/systemd/system/seci-api.service`:

```ini
[Unit]
Description=SECI Search API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai
Environment="PATH=/opt/ai/venv/bin"
ExecStart=/opt/ai/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable seci-api
sudo systemctl start seci-api
sudo systemctl status seci-api
```

### 6. Configure Nginx Reverse Proxy (Recommended)

Install Nginx:

```bash
sudo apt install nginx -y
```

Create Nginx configuration `/etc/nginx/sites-available/seci-api`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/seci-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Configure SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Certbot will automatically configure HTTPS
```

### 8. Configure Firewall

```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable
```

## Testing the Deployment

### 1. Test API Endpoints

```bash
# Health check
curl http://your-domain.com/health

# Root endpoint
curl http://your-domain.com/

# Test search
curl -X POST http://your-domain.com/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?", "max_results": 5}'
```

### 2. Run Example Script

```bash
cd /opt/ai
source venv/bin/activate
python examples/perplexity_search.py
```

## Monitoring and Logs

### View Logs

```bash
# Systemd service logs
sudo journalctl -u seci-api -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Monitor System Resources

```bash
# CPU and memory usage
htop

# Service status
sudo systemctl status seci-api
```

## Performance Optimization

### 1. Enable Caching

The system includes built-in caching. For production, consider:

- Redis for distributed caching
- CDN for static assets
- Database for persistent storage

### 2. Scale Horizontally

Run multiple workers:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 8
```

Or use multiple instances behind a load balancer.

### 3. Rate Limiting

Add rate limiting to prevent abuse:

```bash
pip install slowapi
```

## API Usage Examples

### Python

```python
import requests

# Search query
response = requests.post(
    "http://your-domain.com/search",
    json={
        "query": "Latest AI developments",
        "session_id": "user-123",
        "max_results": 5
    }
)

result = response.json()
print(result['response'])
print(result['citations'])
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://your-domain.com/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Latest AI developments',
    session_id: 'user-123',
    max_results: 5
  })
});

const result = await response.json();
console.log(result.response);
console.log(result.citations);
```

### cURL

```bash
curl -X POST http://your-domain.com/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest AI developments",
    "session_id": "user-123",
    "max_results": 5
  }'
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u seci-api -n 50

# Check Python dependencies
source venv/bin/activate
pip list

# Verify configuration
python -c "from seci import SearchEngine; print('OK')"
```

### Search Not Working

- Check internet connectivity
- Verify search providers are accessible
- Check firewall rules

### High Memory Usage

- Reduce number of workers
- Limit max_sessions in context manager
- Enable swap space

## Security Considerations

1. **API Authentication**: Add authentication middleware
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Input Validation**: Already included via Pydantic
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure CORS appropriately for your use case

## Maintenance

### Update the System

```bash
cd /opt/ai
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart seci-api
```

### Backup

```bash
# Backup configuration
sudo cp -r /opt/ai/config /backup/

# Backup logs (if needed)
sudo cp /var/log/nginx/* /backup/logs/
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/AkshatNaruka/ai/issues
- Documentation: See `docs/` directory

---

**Built with ❤️ for efficient and fast AI search**
