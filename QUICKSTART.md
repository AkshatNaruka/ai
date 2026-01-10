# Quick Start Guide - SECI AI Assistant (Jarvis)

Get started with SECI in under 5 minutes! Install and run your own AI assistant on any device.

## 🚀 One-Line Install

```bash
# Clone and install
git clone https://github.com/AkshatNaruka/ai.git
cd ai
python install.py
```

That's it! The installer will automatically:
- Detect your platform (Linux, macOS, Windows, ARM, etc.)
- Check system requirements
- Create a virtual environment
- Install all dependencies
- Set up the CLI interface
- Configure your system

## 📱 Installation Options

### Standard Installation (Recommended)
```bash
python install.py
```

### Minimal Installation (For limited resources, mobile, IoT)
```bash
python install.py --minimal
```

### Advanced Options
```bash
# Skip configuration wizard
python install.py --no-config

# Install globally (no virtual environment)
python install.py --no-venv
```

## 🎯 Using Jarvis

After installation, activate your environment (if using venv):

```bash
# Linux/macOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

### Interactive Mode (Recommended for First-Time Users)

```bash
python jarvis.py --interactive
```

Then you can:
```
You: ask What is machine learning?
JARVIS: [provides detailed answer with sources]

You: search latest AI news
JARVIS: [shows search results]

You: help
[shows available commands]

You: exit
```

### Command Line Mode

```bash
# Ask a question
python jarvis.py ask "What is artificial intelligence?"

# Search the web
python jarvis.py search "latest developments in AI"

# Check system status
python jarvis.py status

# Start API server
python jarvis.py serve
```

## 🌐 API Mode

Start the API server:

```bash
python api.py
# or
python jarvis.py serve
```

Then access it:
```bash
# Using curl
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?"}'

# Using the CLI test tool
python cli_test.py search "What is AI?"
```

API documentation available at: http://localhost:8000/docs

## 📋 Platform-Specific Notes

### Linux
- Works out of the box
- Systemd service template created automatically
- To run as service: `sudo cp systemd/jarvis.service /etc/systemd/system/`

### macOS
- Works out of the box
- Use `brew install python@3.11` if Python not installed

### Windows
- Use PowerShell or Command Prompt
- Activate venv: `.\venv\Scripts\activate`

### Raspberry Pi / ARM Devices
- Use minimal installation: `python install.py --minimal`
- Optimizations applied automatically
- May take longer to install

### Mobile (Termux on Android)
```bash
pkg install python git
git clone https://github.com/AkshatNaruka/ai.git
cd ai
python install.py --minimal
```

## 🔧 Configuration

### First-Time Setup
The installer runs a configuration wizard. You can reconfigure anytime:

```bash
python jarvis.py config --show
python jarvis.py config --set api_port 8080
python jarvis.py config --set max_results 10
```

### Configuration File
Located at: `~/.seci/config.json`

```json
{
  "api_port": 8000,
  "api_host": "localhost",
  "enable_search": true,
  "max_results": 5,
  "session_id": null
}
```

## 🎓 Examples

### Ask Questions
```bash
# General knowledge
python jarvis.py ask "What is quantum computing?"

# Current events (with web search)
python jarvis.py ask "What are the latest AI breakthroughs?"

# Technical questions
python jarvis.py ask "How does a transformer model work?"
```

### Search the Web
```bash
python jarvis.py search "Python tutorials"
python jarvis.py search "machine learning papers"
```

### Interactive Conversation
```bash
python jarvis.py --interactive

You: ask Tell me about AI
JARVIS: [provides answer]

You: ask Can you elaborate on neural networks?
JARVIS: [provides detailed answer with context from previous question]
```

## 🐳 Docker Deployment (Optional)

```bash
# Build
docker build -t jarvis .

# Run
docker run -p 8000:8000 jarvis
```

## 🔄 Running as a Service

### Linux (systemd)
```bash
# Copy service file
sudo cp systemd/jarvis.service /etc/systemd/system/

# Enable and start
sudo systemctl enable jarvis
sudo systemctl start jarvis

# Check status
sudo systemctl status jarvis
```

### macOS (launchd)
```bash
# Copy plist file (to be created)
cp launchd/com.seci.jarvis.plist ~/Library/LaunchAgents/

# Load
launchctl load ~/Library/LaunchAgents/com.seci.jarvis.plist
```

## 🧪 Verify Installation

```bash
# Check Jarvis status
python jarvis.py status

# Test API server
python cli_test.py health

# Run example
python examples/perplexity_search.py
```

## 🆘 Troubleshooting

### "Module not found" error
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Or reinstall
python install.py
```

### "API server not running"
```bash
# Start manually
python api.py

# Or let Jarvis start it
python jarvis.py ask "test question"
```

### Low memory/resources
```bash
# Use minimal installation
python install.py --minimal
```

### Port already in use
```bash
# Change port
python jarvis.py config --set api_port 8080
python jarvis.py serve --port 8080
```

## 🎯 Next Steps

1. **Explore Examples**: Check out `examples/` directory
2. **Read Full Docs**: See `README.md` and `docs/` for detailed documentation
3. **Customize**: Modify configuration in `~/.seci/config.json`
4. **Deploy**: Set up as a service for always-on access
5. **Extend**: Add custom features to suit your needs

## 📚 Additional Resources

- **Full Documentation**: [README.md](README.md)
- **Architecture**: [docs/ARCHITECTURE_VISUAL.md](docs/ARCHITECTURE_VISUAL.md)
- **Search System**: [docs/SEARCH_SYSTEM.md](docs/SEARCH_SYSTEM.md)
- **Deployment**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

## 🤝 Getting Help

- Open an issue on GitHub
- Check the documentation
- Run `python jarvis.py --help`

---

**Welcome to your personal AI assistant! 🤖**
