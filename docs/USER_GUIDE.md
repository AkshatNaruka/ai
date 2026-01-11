# SECI User Guide

A comprehensive guide for users to make the most of SECI AI Assistant.

## Table of Contents
- [Introduction](#introduction)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Tips and Tricks](#tips-and-tricks)
- [Customization](#customization)
- [Integration](#integration)
- [Best Practices](#best-practices)

## Introduction

SECI is your personal AI assistant that can:
- Answer questions using its AI knowledge
- Search the web for current information
- Maintain conversational context
- Learn and improve over time

### What Can SECI Do?

**Information Lookup:**
- "What is quantum computing?"
- "Explain machine learning in simple terms"
- "Who invented the transistor?"

**Web Search:**
- "Latest developments in AI"
- "Best Python libraries for data science"
- "Current weather in Tokyo"

**Conversational:**
- Follow-up questions with context
- Multi-turn conversations
- Clarifications and refinements

**Research Assistant:**
- Summarize complex topics
- Compare and contrast concepts
- Find reliable sources

## Basic Usage

### Interactive Mode

**Starting Interactive Mode:**
```bash
python jarvis.py --interactive
```

**Basic Commands:**
```
You: ask <question>     # Ask a question
You: search <query>     # Search the web
You: help              # Show help
You: status            # Check system status
You: exit              # Exit program
```

**Example Session:**
```bash
$ python jarvis.py --interactive

JARVIS: Hello! How can I help you today?

You: ask What is Python?

JARVIS: Python is a high-level, interpreted programming language...
[Detailed answer with sources]

You: search Python tutorials

JARVIS: Here are the top results:
1. Python Tutorial - W3Schools
2. Learn Python - Python.org
[More results...]

You: exit

JARVIS: Goodbye!
```

### Command Line Mode

**Quick Questions:**
```bash
# Ask a question
python jarvis.py ask "What is machine learning?"

# Search the web
python jarvis.py search "Python best practices"

# Check status
python jarvis.py status
```

### API Mode

**Start API Server:**
```bash
python jarvis.py serve
# Or: python api.py
```

**Make Requests:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?"}'
```

## Advanced Features

### Conversational Context

SECI remembers your conversation within a session:

```
You: ask What is Python?
JARVIS: [Explains Python]

You: ask What are its main uses?
JARVIS: [Explains Python uses, understanding "it" refers to Python]

You: ask How does it compare to Java?
JARVIS: [Compares Python and Java, with full context]
```

**How It Works:**
- Maintains conversation history
- Understands references (it, that, them)
- Provides contextual answers
- Up to 20 messages by default

### Search Customization

**Control Search Behavior:**

```python
# Via API
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "machine learning",
        "max_results": 10,        # Number of results
        "scrape_content": True,   # Scrape full content
        "session_id": "my-session" # Maintain context
    }
)
```

**Search Providers:**
- DuckDuckGo (default, no API key needed)
- Google (requires API key)
- Bing (requires API key)

### Enhanced Query Processing

SECI automatically enhances your queries:

**Original:** "ML basics"

**Enhanced:**
- "ML basics"
- "machine learning basics"
- "introduction to machine learning"
- "ML fundamentals"

This results in better, more comprehensive answers.

### Result Ranking

Results are automatically ranked by:
- **Relevance** (30%): How well it matches your query
- **Title Match** (25%): Keywords in title
- **Content Quality** (25%): Snippet informativeness
- **Source Credibility** (20%): Reliability of source

### Caching

Repeated queries are cached for speed:
```
First query: "What is AI?" → 2-3 seconds
Repeated query: "What is AI?" → <100ms (from cache)
```

Cache expires after 1 hour by default.

## Tips and Tricks

### Getting Better Results

**1. Be Specific**
- ❌ "Tell me about AI"
- ✅ "What are the main applications of AI in healthcare?"

**2. Ask Follow-ups**
```
You: ask What is neural network?
JARVIS: [Explains neural networks]

You: ask Can you give an example?
JARVIS: [Provides example with context]
```

**3. Use Search for Current Info**
```
# For facts and concepts
ask "What is machine learning?"

# For current events
search "Latest AI news 2024"
```

**4. Break Down Complex Questions**
```
# Instead of:
"Tell me everything about quantum computing"

# Try:
ask "What is quantum computing?"
ask "How does it differ from classical computing?"
ask "What are current applications?"
```

### Keyboard Shortcuts (Interactive Mode)

- `Ctrl+C`: Interrupt current operation
- `Ctrl+D` or `exit`: Exit program
- `Up/Down Arrow`: Command history (if supported by your terminal)

### Session Management

**Preserve Context:**
```python
# Use consistent session_id
response1 = search(query="What is Python?", session_id="user-123")
response2 = search(query="What are its uses?", session_id="user-123")
# Second query understands context from first
```

**Start Fresh:**
```python
# Use new session_id or omit it
response = search(query="New topic", session_id="new-session")
```

### Performance Optimization

**1. Use Minimal Mode (Resource-Constrained Devices)**
```bash
python install.py --minimal
```

**2. Adjust Settings**
```python
# Edit ~/.seci/config.json
{
    "max_results": 5,          # Fewer results = faster
    "scrape_content": false,   # Skip scraping = faster
    "cache_enabled": true      # Enable caching
}
```

**3. Pre-warm Cache**
```bash
# Cache common queries
python jarvis.py ask "What is Python?"
python jarvis.py ask "What is machine learning?"
# Later queries will be instant
```

## Customization

### Configuration File

**Location:** `~/.seci/config.json`

**Example Configuration:**
```json
{
    "search": {
        "providers": ["duckduckgo"],
        "max_results": 10,
        "timeout": 10,
        "cache_ttl": 3600
    },
    "scraper": {
        "timeout": 10,
        "max_content_length": 50000,
        "user_agent": "SECI/0.1"
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8000,
        "cors_origins": ["*"]
    },
    "logging": {
        "level": "INFO",
        "file": "~/.seci/logs/seci.log"
    }
}
```

### Environment Variables

```bash
# Search API keys (optional)
export GOOGLE_API_KEY="your-key"
export GOOGLE_CSE_ID="your-cse-id"
export BING_API_KEY="your-key"

# Configuration
export SECI_CONFIG="path/to/config.json"
export SECI_LOG_LEVEL="DEBUG"
```

### Model Configuration

**Location:** `config/default.yaml`

**Adjust Model Behavior:**
```yaml
model:
  hidden_size: 256      # Model capacity
  num_layers: 4         # Model depth
  use_lora: false       # Parameter-efficient training
  use_quantization: false  # Memory efficiency

training:
  learning_rate: 0.0001
  batch_size: 32
  max_steps: 10000
```

## Integration

### Python Integration

```python
from seci import QueryProcessor, SearchEngine, WebScraper, ContextManager
from seci.search import DuckDuckGoProvider

# Initialize components
search_engine = SearchEngine()
search_engine.add_provider(DuckDuckGoProvider())
scraper = WebScraper()
context = ContextManager()

# Create processor
processor = QueryProcessor(search_engine, scraper, context)

# Process queries
result = processor.process("What is AI?", session_id="user-1")
print(result.response)
print(f"Sources: {len(result.citations)}")
```

### API Integration

**JavaScript/Node.js:**
```javascript
const axios = require('axios');

async function ask(query) {
    const response = await axios.post('http://localhost:8000/search', {
        query: query,
        session_id: 'my-session'
    });
    return response.data;
}

// Use it
const result = await ask("What is machine learning?");
console.log(result.response);
```

**Python:**
```python
import requests

def ask(query, session_id=None):
    response = requests.post(
        'http://localhost:8000/search',
        json={
            'query': query,
            'session_id': session_id
        }
    )
    return response.json()

# Use it
result = ask("What is machine learning?")
print(result['response'])
```

**cURL:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "session_id": "test"}'
```

### Web Application Integration

**Example: Flask App**
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
SECI_API = "http://localhost:8000"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    
    # Forward to SECI
    response = requests.post(
        f"{SECI_API}/search",
        json={
            'query': data['message'],
            'session_id': data['user_id']
        }
    )
    
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=5000)
```

### Command Line Integration

**Bash Script:**
```bash
#!/bin/bash
# ask.sh - Quick wrapper for SECI

query="$*"
python jarvis.py ask "$query"
```

**Usage:**
```bash
chmod +x ask.sh
./ask.sh What is Python?
```

## Best Practices

### For Optimal Performance

1. **Enable Caching**
   - Dramatically speeds up repeated queries
   - Configure cache TTL based on your needs

2. **Use Appropriate Mode**
   - Interactive: For exploration and multi-turn conversations
   - Command: For scripts and automation
   - API: For application integration

3. **Manage Context**
   - Use session IDs consistently for related queries
   - Start new sessions for unrelated topics
   - Clear old sessions periodically

### For Better Answers

1. **Frame Questions Clearly**
   - Be specific about what you want to know
   - Provide context when necessary
   - Ask one thing at a time

2. **Use Follow-ups**
   - Build on previous answers
   - Ask for clarification
   - Request examples or details

3. **Choose Right Command**
   - `ask`: For explanations and understanding
   - `search`: For current information and sources

### For Security

1. **API Keys**
   - Store in environment variables
   - Never commit to version control
   - Use separate keys for different environments

2. **Network Security**
   - Use HTTPS in production
   - Configure CORS appropriately
   - Implement rate limiting

3. **Data Privacy**
   - SECI runs locally by default (private)
   - Be careful with API deployments
   - Review what data is logged

### For Troubleshooting

1. **Check Logs**
   ```bash
   # View logs
   tail -f ~/.seci/logs/seci.log
   
   # Enable debug logging
   export SECI_LOG_LEVEL=DEBUG
   ```

2. **Verify Installation**
   ```bash
   python jarvis.py status
   ```

3. **Test Components**
   ```python
   # Test search
   from seci.search import DuckDuckGoProvider
   provider = DuckDuckGoProvider()
   results = provider.search("test")
   print(len(results))
   ```

## Common Use Cases

### Research Assistant
```
You: search recent advances in quantum computing
You: ask Can you explain the most significant breakthrough?
You: search companies working on quantum computers
You: ask Which company is leading in this field?
```

### Learning Tool
```
You: ask What is a neural network?
You: ask How does backpropagation work?
You: ask Can you give a simple example?
You: search neural network tutorials for beginners
```

### Information Lookup
```
You: ask Who invented the World Wide Web?
You: ask When was it invented?
You: ask What was the first website?
```

### Fact Checking
```
You: search Did Einstein fail mathematics in school?
You: ask What's the true story about Einstein's education?
```

## Getting Help

**Documentation:**
- [Getting Started](GETTING_STARTED.md) - First steps
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
- [FAQ](FAQ.md) - Frequently asked questions
- [Developer Guide](DEVELOPER_GUIDE.md) - For developers

**Community:**
- GitHub Issues - Report bugs
- GitHub Discussions - Ask questions
- Discord - Chat with community (coming soon)

**Still Stuck?**
1. Check the documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Open a new issue

---

**Enjoy using SECI! Ask away! 🚀**
