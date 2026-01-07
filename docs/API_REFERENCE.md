# SECI Search API - Quick Reference

## Starting the API

### Development Mode
```bash
python api.py
```

### Production Mode
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### 1. Health Check
```bash
GET /health

# Response
{
  "status": "healthy",
  "timestamp": "2024-01-07T..."
}
```

### 2. System Status
```bash
GET /

# Response
{
  "status": "online",
  "version": "0.1.0",
  "components": {
    "search_engine": true,
    "web_scraper": true,
    "context_manager": true,
    "query_processor": true
  },
  "timestamp": "2024-01-07T..."
}
```

### 3. Search Query
```bash
POST /search
Content-Type: application/json

{
  "query": "What is artificial intelligence?",
  "session_id": "optional-session-id",
  "max_results": 5,
  "scrape_content": true
}

# Response
{
  "query": "What is artificial intelligence?",
  "session_id": "generated-or-provided-id",
  "response": "Based on the search results...",
  "citations": [
    {
      "number": 1,
      "title": "Artificial Intelligence - Wikipedia",
      "url": "https://en.wikipedia.org/...",
      "source": "duckduckgo"
    }
  ],
  "search_results": [...],
  "timestamp": "2024-01-07T...",
  "metadata": {
    "num_results": 5,
    "num_scraped": 3
  }
}
```

### 4. Get Conversation History
```bash
GET /conversation/{session_id}

# Response
{
  "session_id": "session-123",
  "messages": [
    {
      "role": "user",
      "content": "What is AI?",
      "timestamp": "2024-01-07T...",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "AI is...",
      "timestamp": "2024-01-07T...",
      "metadata": {
        "citations": [...]
      }
    }
  ],
  "created_at": "2024-01-07T...",
  "updated_at": "2024-01-07T..."
}
```

### 5. Clear Conversation
```bash
DELETE /conversation/{session_id}

# Response
{
  "message": "Conversation session-123 cleared"
}
```

### 6. List Active Sessions
```bash
GET /sessions

# Response
{
  "sessions": ["session-1", "session-2", ...],
  "count": 10,
  "timestamp": "2024-01-07T..."
}
```

## Example Usage

### cURL
```bash
# Search query
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "max_results": 5
  }'

# Get conversation
curl http://localhost:8000/conversation/my-session-id

# Health check
curl http://localhost:8000/health
```

### Python
```python
import requests

# Search
response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "What is machine learning?",
        "session_id": "my-session",
        "max_results": 5
    }
)
result = response.json()
print(result['response'])
print(result['citations'])

# Get history
history = requests.get(
    "http://localhost:8000/conversation/my-session"
)
print(history.json()['messages'])
```

### JavaScript/Fetch
```javascript
// Search
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is machine learning?',
    session_id: 'my-session',
    max_results: 5
  })
});

const result = await response.json();
console.log(result.response);
console.log(result.citations);

// Get history
const history = await fetch(
  'http://localhost:8000/conversation/my-session'
);
const messages = await history.json();
console.log(messages.messages);
```

### httpie
```bash
# Search
http POST localhost:8000/search \
  query="What is machine learning?" \
  max_results:=5

# Get conversation
http GET localhost:8000/conversation/my-session
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes
- `200`: Success
- `404`: Resource not found (e.g., session doesn't exist)
- `422`: Validation error (invalid request body)
- `500`: Internal server error
- `503`: Service unavailable (components not initialized)

## Rate Limiting

Currently no rate limiting is implemented. For production:
1. Use Nginx rate limiting
2. Implement API keys
3. Use Redis-based rate limiting

## Security Considerations

For production deployment:
1. Enable HTTPS
2. Add authentication (API keys, OAuth)
3. Configure CORS properly
4. Add rate limiting
5. Use environment variables for sensitive config

## Monitoring

### Logs
```bash
# View logs in real-time
tail -f /var/log/seci-api.log

# Or with systemd
journalctl -u seci-api -f
```

### Metrics
Monitor these metrics:
- Request rate
- Response time
- Error rate
- Cache hit rate
- Active sessions

## Troubleshooting

### API not starting
```bash
# Check if port is in use
lsof -i :8000

# Check dependencies
pip list

# Verify imports
python -c "from seci import QueryProcessor; print('OK')"
```

### Slow responses
- Increase timeout values
- Reduce scrape_top_n
- Enable caching
- Add more workers

### Search not working
- Check internet connectivity
- Verify search providers are accessible
- Check firewall rules
- Review logs for errors

## Performance Tips

1. **Enable Caching**: Results are cached by default
2. **Adjust Workers**: Match CPU cores
3. **Use Redis**: For distributed caching
4. **CDN**: For static assets
5. **Load Balancer**: For horizontal scaling

---

**For more information, see [DEPLOYMENT.md](../docs/DEPLOYMENT.md)**
