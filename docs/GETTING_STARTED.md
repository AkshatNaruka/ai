# Getting Started with SECI

Welcome to SECI (Self-Evolving Compact Intelligence)! This guide will help you get started with your personal AI assistant in just a few minutes.

## Table of Contents
- [What is SECI?](#what-is-seci)
- [Quick Installation](#quick-installation)
- [First Steps](#first-steps)
- [Basic Usage](#basic-usage)
- [Understanding the System](#understanding-the-system)
- [Next Steps](#next-steps)

## What is SECI?

SECI is a **personal AI assistant** that combines:
- 🤖 **Compact AI Model**: A small, efficient transformer that learns continuously
- 🔍 **Web Search**: Search the internet like Perplexity AI
- 💬 **Conversational AI**: Natural language interaction
- 📱 **Portable**: Works on any device - from servers to Raspberry Pi

**In Simple Terms**: Think of SECI as your own personal "Jarvis" (like in Iron Man) that you can:
- Ask questions about anything
- Search the web and get summarized answers
- Run on your own hardware (no cloud required)
- Train to learn new things continuously

## Quick Installation

### Prerequisites
- Python 3.8 or higher
- 1GB RAM minimum (2GB recommended)
- 1GB disk space
- Internet connection (for web search features)

### One-Command Install

```bash
# 1. Clone the repository
git clone https://github.com/AkshatNaruka/ai.git
cd ai

# 2. Run the installer (it does everything for you!)
python install.py
```

The installer automatically:
- ✅ Detects your operating system
- ✅ Checks if you have the required software
- ✅ Creates a virtual environment (isolated Python setup)
- ✅ Installs all dependencies
- ✅ Configures the system for your hardware
- ✅ Tests the installation

### Installation Options

**For Resource-Constrained Devices** (Raspberry Pi, old laptops, mobile):
```bash
python install.py --minimal
```

**For Advanced Users** (skip auto-configuration):
```bash
python install.py --no-config --no-venv
```

## First Steps

### 1. Activate the Environment

After installation, activate the virtual environment:

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

You'll see `(venv)` in your terminal prompt.

### 2. Test the Installation

```bash
# Check if everything is working
python jarvis.py status
```

You should see:
```
✓ SECI is installed and ready
✓ Python version: 3.x.x
✓ PyTorch available
✓ All dependencies installed
```

## Basic Usage

SECI has two main interfaces: **Jarvis CLI** (for interactive use) and **API Server** (for programmatic access).

### Using Jarvis CLI

#### Interactive Mode (Recommended for Beginners)

```bash
python jarvis.py --interactive
```

This starts a conversation where you can:
```
You: ask What is artificial intelligence?
JARVIS: [Provides a detailed answer with sources]

You: search latest Python tutorials
JARVIS: [Shows web search results]

You: help
JARVIS: [Shows available commands]

You: exit
```

#### Command Mode (Quick Questions)

```bash
# Ask a question
python jarvis.py ask "What is machine learning?"

# Search the web
python jarvis.py search "best Python libraries"

# Check system status
python jarvis.py status
```

### Using the API Server

For programmatic access or building applications:

```bash
# Start the API server
python jarvis.py serve
# Or directly: python api.py
```

The server runs at `http://localhost:8000`

**Example API Request:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?"}'
```

**Response:**
```json
{
  "response": "Artificial Intelligence (AI) is...",
  "citations": [
    {"number": 1, "title": "...", "url": "..."}
  ],
  "session_id": "abc123"
}
```

## Understanding the System

### What Makes SECI Special?

1. **Self-Learning**: Unlike most AI assistants, SECI can learn and improve over time
2. **Privacy-Focused**: Runs on your own hardware - your data stays with you
3. **Resource-Efficient**: Small model that can run on modest hardware
4. **Modular Design**: Each component does one thing well

### Key Components

#### 1. Compact Transformer (The Brain)
- A small AI model (~8M parameters)
- Can process and generate text
- Learns continuously without forgetting old knowledge

#### 2. External Memory (The Knowledge Bank)
- Stores important information it learns
- Can recall relevant facts when needed
- Like a personal knowledge database

#### 3. Search Engine (The Internet Gateway)
- Searches multiple providers (DuckDuckGo, Google)
- Extracts and summarizes web content
- Provides cited sources

#### 4. Query Processor (The Coordinator)
- Combines AI model, memory, and search
- Understands your questions
- Generates comprehensive answers

### How It Works (Simplified)

```
Your Question
    ↓
[Understanding] → What are you asking?
    ↓
[Search] → Find relevant information online
    ↓
[Processing] → Combine with AI knowledge
    ↓
[Generation] → Create a helpful response
    ↓
Answer with Citations
```

## Common Use Cases

### 1. Quick Information Lookup
```bash
python jarvis.py ask "What is quantum computing?"
```

### 2. Research Assistant
```bash
# In interactive mode
You: search recent developments in AI
You: search machine learning best practices
You: search Python vs JavaScript comparison
```

### 3. Learning Companion
```bash
python jarvis.py ask "Explain neural networks like I'm 10"
```

### 4. API Integration
Build your own applications using the API:
```python
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={"query": "Latest tech news"}
)
print(response.json()['response'])
```

## Next Steps

### For Regular Users
1. **Explore Interactive Mode**: Try different types of questions
2. **Read the [User Guide](USER_GUIDE.md)**: Learn advanced features
3. **Check [Troubleshooting](TROUBLESHOOTING.md)**: If you encounter issues

### For Developers
1. **Read [Developer Guide](DEVELOPER_GUIDE.md)**: Understand the codebase
2. **Explore [Architecture](ARCHITECTURE.md)**: Learn how it works internally
3. **See [Examples](../examples/)**: Code samples for common tasks
4. **Read [API Reference](API_REFERENCE.md)**: Detailed API documentation

### For Contributors
1. **Read [Contributing Guidelines](CONTRIBUTING.md)**: How to contribute
2. **Check [Roadmap](ROADMAP.md)**: Future plans
3. **See [Code of Conduct](CODE_OF_CONDUCT.md)**: Community guidelines

## Getting Help

- **Documentation**: Check the `docs/` folder
- **Examples**: Look at `examples/` directory
- **Issues**: Report bugs on GitHub Issues
- **Questions**: Ask on GitHub Discussions

## Quick Reference

### Essential Commands
```bash
# Installation
python install.py

# Interactive mode
python jarvis.py --interactive

# Ask a question
python jarvis.py ask "your question"

# Search the web
python jarvis.py search "search query"

# Start API server
python jarvis.py serve

# Check status
python jarvis.py status

# Get help
python jarvis.py --help
```

### Configuration Files
- `config/default.yaml` - Standard configuration
- `config/low_resource.yaml` - For limited hardware
- `~/.seci/config.json` - User preferences

### Important Directories
- `seci/` - Main source code
- `docs/` - Documentation
- `examples/` - Example scripts
- `config/` - Configuration files

## Tips for Success

1. **Start Simple**: Begin with basic questions in interactive mode
2. **Explore Gradually**: Try different commands one at a time
3. **Read Error Messages**: They often tell you exactly what's wrong
4. **Check Examples**: The `examples/` folder has working code
5. **Ask for Help**: Community is here to help you succeed

## What's Next?

You're now ready to use SECI! Here are some suggested paths:

**Beginner Path:**
1. Try interactive mode for 10 minutes
2. Read the [User Guide](USER_GUIDE.md)
3. Explore different question types

**Developer Path:**
1. Read [Architecture Guide](ARCHITECTURE.md)
2. Study example scripts
3. Build a small project using the API

**Contributor Path:**
1. Understand the [Workflow](WORKFLOW.md)
2. Read [Contributing Guidelines](CONTRIBUTING.md)
3. Start with documentation or small features

---

**Welcome to SECI! Start exploring and building amazing things! 🚀**
