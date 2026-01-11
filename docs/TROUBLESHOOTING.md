# Troubleshooting Guide

Common issues and their solutions when using SECI.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Performance Issues](#performance-issues)
- [Search Problems](#search-problems)
- [API Issues](#api-issues)
- [Training Problems](#training-problems)
- [Getting More Help](#getting-more-help)

## Installation Issues

### Issue: "Python version not supported"

**Error:**
```
ERROR: Python 3.7 is not supported. Please use Python 3.8 or higher.
```

**Solution:**
```bash
# Check your Python version
python --version

# Install Python 3.8+ from python.org
# Or use pyenv:
pyenv install 3.10.5
pyenv local 3.10.5
```

### Issue: "pip install fails with dependency errors"

**Error:**
```
ERROR: Could not find a version that satisfies the requirement torch>=2.0.0
```

**Solutions:**

**1. Update pip:**
```bash
pip install --upgrade pip setuptools wheel
```

**2. Install PyTorch separately:**
```bash
# CPU version
pip install torch --index-url https://download.pytorch.org/whl/cpu

# GPU version (CUDA 11.8)
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**3. Use requirements-minimal.txt:**
```bash
pip install -r requirements-minimal.txt
```

### Issue: "ModuleNotFoundError: No module named 'seci'"

**Error:**
```
ModuleNotFoundError: No module named 'seci'
```

**Solution:**
```bash
# Make sure you installed in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/ai"

# Verify installation
python -c "import seci; print(seci.__file__)"
```

### Issue: "Permission denied" during installation

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

**1. Use virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

**2. Install for user only:**
```bash
pip install --user -e .
```

**3. Use sudo (not recommended):**
```bash
sudo pip install -e .
```

## Runtime Errors

### Issue: "CUDA out of memory"

**Error:**
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```

**Solutions:**

**1. Use CPU:**
```bash
export CUDA_VISIBLE_DEVICES=""
python jarvis.py --device cpu
```

**2. Reduce batch size:**
```yaml
# config/default.yaml
training:
  batch_size: 8  # Reduce from 32
```

**3. Use quantization:**
```yaml
# config/default.yaml
model:
  use_quantization: true
```

**4. Clear cache:**
```python
import torch
torch.cuda.empty_cache()
```

### Issue: "Connection refused" when starting API

**Error:**
```
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**Solutions:**

**1. Check if server is running:**
```bash
curl http://localhost:8000/health
```

**2. Check port availability:**
```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**3. Use different port:**
```bash
python api.py --port 8001
```

**4. Check firewall:**
```bash
# Linux
sudo ufw allow 8000

# Windows: Add firewall rule in Windows Defender
```

### Issue: "Import Error: cannot import name"

**Error:**
```
ImportError: cannot import name 'SearchEngine' from 'seci.search'
```

**Solution:**
```bash
# Reinstall in development mode
pip uninstall seci
pip install -e .

# Or check if __init__.py exists
ls seci/search/__init__.py
```

## Performance Issues

### Issue: Slow query responses

**Symptoms:** Queries take >5 seconds

**Solutions:**

**1. Enable caching:**
```python
from seci import EnhancedQueryProcessor

processor = EnhancedQueryProcessor(
    enable_caching=True,
    cache_ttl=3600
)
```

**2. Use minimal mode:**
```bash
python install.py --minimal
```

**3. Reduce search results:**
```python
results = search_engine.search(query, num_results=5)  # Instead of 10
```

**4. Skip content scraping:**
```python
result = processor.process(query, scrape_content=False)
```

**5. Check network connection:**
```bash
ping google.com
```

### Issue: High memory usage

**Symptoms:** System using >4GB RAM

**Solutions:**

**1. Use low-resource config:**
```bash
python train.py --config config/low_resource.yaml
```

**2. Reduce memory size:**
```yaml
# config/default.yaml
memory:
  memory_size: 500  # Reduce from 1000
```

**3. Reduce buffer size:**
```yaml
# config/default.yaml
replay:
  buffer_size: 5000  # Reduce from 10000
```

**4. Enable quantization:**
```yaml
model:
  use_quantization: true
```

**5. Monitor memory:**
```python
import psutil
print(f"Memory usage: {psutil.Process().memory_info().rss / 1024**2:.2f} MB")
```

### Issue: Slow training

**Symptoms:** Training takes hours

**Solutions:**

**1. Use GPU if available:**
```bash
python train.py --device cuda
```

**2. Increase batch size:**
```yaml
training:
  batch_size: 64  # If you have enough memory
```

**3. Reduce validation frequency:**
```python
trainer.train(
    train_loader,
    validate_every=1000  # Instead of every 100 steps
)
```

**4. Use gradient accumulation:**
```python
# Effective batch size = batch_size * accumulation_steps
config.training.gradient_accumulation_steps = 4
```

**5. Profile code:**
```python
import cProfile
cProfile.run('trainer.train(train_loader)', 'stats')

import pstats
p = pstats.Stats('stats')
p.sort_stats('cumulative').print_stats(10)
```

## Search Problems

### Issue: "No search results found"

**Error:**
```
WARNING: No results found for query: "test query"
```

**Solutions:**

**1. Check internet connection:**
```bash
ping google.com
curl https://duckduckgo.com
```

**2. Try different search provider:**
```python
from seci.search import GoogleSearchProvider

search_engine.add_provider(GoogleSearchProvider())
```

**3. Check for rate limiting:**
```
# Wait a few minutes and try again
# Or use different provider
```

**4. Verify query is not empty:**
```python
query = query.strip()
if not query:
    print("Empty query!")
```

### Issue: "Search timeout"

**Error:**
```
requests.exceptions.Timeout: HTTPSConnectionPool: Read timed out
```

**Solutions:**

**1. Increase timeout:**
```python
search_engine = SearchEngine(timeout=30)  # Default: 10
```

**2. Check network speed:**
```bash
speedtest-cli
```

**3. Use different DNS:**
```bash
# Linux: Edit /etc/resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
```

### Issue: "Web scraping fails"

**Error:**
```
ERROR: Failed to scrape content from https://example.com
```

**Solutions:**

**1. Check if URL is accessible:**
```bash
curl -I https://example.com
```

**2. Use different user agent:**
```python
scraper = WebScraper(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)
```

**3. Skip problematic URLs:**
```python
try:
    content = scraper.scrape(url)
except Exception as e:
    logger.warning(f"Failed to scrape {url}: {e}")
    continue
```

**4. Check for JavaScript-heavy sites:**
```
# Some sites require JavaScript
# Consider using selenium or playwright for these
```

## API Issues

### Issue: "CORS error in browser"

**Error:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solutions:**

**1. Configure CORS:**
```python
# api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**2. Or allow all (development only):**
```python
allow_origins=["*"]
```

**3. Use environment variable:**
```bash
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8080"
python api.py
```

### Issue: "API returns 500 Internal Server Error"

**Error:**
```json
{
  "detail": "Internal Server Error"
}
```

**Solutions:**

**1. Check server logs:**
```bash
# If running with uvicorn
python api.py  # View console output

# Or check log file
tail -f ~/.seci/logs/seci.log
```

**2. Enable debug mode:**
```python
# api.py
app = FastAPI(debug=True)
```

**3. Test endpoint manually:**
```python
# test_api.py
from api import app
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.post("/search", json={"query": "test"})
print(response.status_code)
print(response.json())
```

### Issue: "Rate limiting / Too Many Requests"

**Error:**
```
429 Too Many Requests
```

**Solutions:**

**1. Add rate limiting:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/search")
@limiter.limit("10/minute")
async def search(request: Request, ...):
    ...
```

**2. Implement caching:**
```python
# Cache responses to reduce API calls
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str):
    return processor.process(query)
```

## Training Problems

### Issue: "Loss not decreasing"

**Symptoms:** Loss stays constant or increases

**Solutions:**

**1. Check learning rate:**
```yaml
training:
  learning_rate: 0.0001  # Try different values: 1e-5, 5e-5, 1e-4
```

**2. Verify gradients:**
```python
for name, param in model.named_parameters():
    if param.grad is not None:
        print(f"{name}: {param.grad.norm().item():.4f}")
```

**3. Check if model is frozen:**
```python
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Trainable parameters: {trainable:,}")
```

**4. Verify data:**
```python
# Check a batch
batch = next(iter(train_loader))
print(f"Input shape: {batch['input_ids'].shape}")
print(f"Labels shape: {batch['labels'].shape}")
print(f"Sample input: {batch['input_ids'][0][:10]}")
```

**5. Reduce batch size:**
```yaml
training:
  batch_size: 8  # Start small
```

### Issue: "NaN in loss"

**Error:**
```
RuntimeError: loss is NaN
```

**Solutions:**

**1. Reduce learning rate:**
```yaml
training:
  learning_rate: 0.00001  # Much smaller
```

**2. Use gradient clipping:**
```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

**3. Check for invalid inputs:**
```python
assert not torch.isnan(input_ids).any()
assert not torch.isinf(input_ids).any()
```

**4. Use mixed precision carefully:**
```python
# If using amp, try without it
# scaler = GradScaler()  # Comment out
```

### Issue: "Checkpoint loading fails"

**Error:**
```
RuntimeError: Error loading checkpoint: ...
```

**Solutions:**

**1. Check file exists:**
```bash
ls -lh outputs/checkpoint_step_1000.pt
```

**2. Verify checkpoint structure:**
```python
import torch
checkpoint = torch.load("checkpoint.pt", map_location="cpu")
print(checkpoint.keys())
```

**3. Load with strict=False:**
```python
model.load_state_dict(checkpoint['model_state_dict'], strict=False)
```

**4. Check compatibility:**
```python
# Checkpoint from different Python/PyTorch version?
# Try: torch.load(..., weights_only=True)
```

## Getting More Help

### Diagnostic Information

When asking for help, include:

```bash
# System info
python --version
pip list | grep torch
pip list | grep seci

# SECI status
python jarvis.py status

# Error logs
tail -n 50 ~/.seci/logs/seci.log

# Configuration
cat ~/.seci/config.json
cat config/default.yaml
```

### Common Diagnostics

**Check Installation:**
```python
import seci
print(f"SECI version: {seci.__version__}")
print(f"Location: {seci.__file__}")

import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

**Test Components:**
```python
# Test search
from seci.search import DuckDuckGoProvider
provider = DuckDuckGoProvider()
results = provider.search("test")
print(f"Search works: {len(results) > 0}")

# Test model
from seci.core.model import CompactTransformer
model = CompactTransformer(vocab_size=1000, hidden_size=128, num_layers=2)
import torch
output = model(torch.randint(0, 1000, (1, 10)))
print(f"Model works: {output['logits'].shape}")
```

### Where to Get Help

1. **Documentation**: Check all docs in `docs/` folder
2. **FAQ**: See [FAQ.md](FAQ.md)
3. **GitHub Issues**: Search existing issues
4. **GitHub Discussions**: Ask the community
5. **Discord**: Join our chat (coming soon)

### Creating a Bug Report

Include:
1. **Description**: What went wrong?
2. **Steps to reproduce**: How to trigger the bug?
3. **Expected behavior**: What should happen?
4. **Actual behavior**: What actually happened?
5. **Environment**: OS, Python version, SECI version
6. **Logs**: Relevant error messages
7. **Code**: Minimal example that reproduces the issue

**Template:**
```markdown
**Bug Description**
Clear description of the problem

**Steps to Reproduce**
1. Install SECI
2. Run `python jarvis.py ask "test"`
3. See error

**Expected Behavior**
Should return an answer

**Actual Behavior**
Returns error: [paste error]

**Environment**
- OS: Ubuntu 22.04
- Python: 3.10.5
- SECI: 0.1.0
- PyTorch: 2.0.1

**Logs**
[paste relevant logs]

**Additional Context**
Any other information
```

---

**Still having issues? Don't hesitate to ask for help! We're here to support you. 🤝**
