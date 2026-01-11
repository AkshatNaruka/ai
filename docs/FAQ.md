# Frequently Asked Questions (FAQ)

Common questions about SECI answered.

## General Questions

### What is SECI?

SECI (Self-Evolving Compact Intelligence) is a personal AI assistant that combines:
- A compact AI model that runs on your device
- Web search capabilities (like Perplexity AI)
- Continuous learning without forgetting
- Complete privacy (runs locally)

### Who is SECI for?

SECI is designed for:
- **Students**: Research and learning assistant
- **Developers**: Code help and documentation search
- **Researchers**: Information gathering and synthesis
- **Hobbyists**: Personal AI experimentation
- **Privacy-conscious users**: Local AI without cloud dependence

### How is SECI different from ChatGPT?

| Feature | SECI | ChatGPT |
|---------|------|---------|
| **Location** | Runs on your device | Cloud-based |
| **Privacy** | 100% private | Data sent to OpenAI |
| **Cost** | Free, open source | Free tier limited, paid plans |
| **Customization** | Fully customizable | Limited customization |
| **Size** | ~8M parameters | Billions of parameters |
| **Web Search** | Built-in | Via plugins/browsing |
| **Learning** | Can learn continuously | Fixed model |

### Is SECI free?

Yes! SECI is:
- **Free to use**: No licensing costs
- **Open source**: MIT License
- **No API fees**: Web search uses free providers
- **No hidden costs**: Runs on your hardware

### Can SECI replace ChatGPT/GPT-4?

**Short answer**: For some tasks, yes. For others, no.

**SECI is better for**:
- Privacy-sensitive tasks
- Running offline
- Learning from your data
- Custom modifications
- Resource-constrained environments

**GPT-4 is better for**:
- Complex reasoning
- Creative writing
- Following complex instructions
- Broad knowledge
- Language translation

## Installation & Setup

### What are the system requirements?

**Minimum**:
- Python 3.8+
- 1GB RAM
- 1GB disk space
- Internet (for web search)

**Recommended**:
- Python 3.10+
- 2GB RAM
- 2GB disk space
- GPU (optional, for training)

### Does SECI work on my device?

SECI works on:
- ✅ Windows 10/11
- ✅ macOS (Intel and Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Fedora, Arch)
- ✅ Raspberry Pi (ARM)
- ✅ Android (via Termux)
- ✅ Cloud servers

### Do I need a GPU?

**For using SECI**: No, CPU is fine
**For training SECI**: GPU helps but not required

### Can I run SECI offline?

**Partially**:
- ✅ AI model works offline
- ✅ Local knowledge works offline
- ❌ Web search requires internet

## Usage Questions

### How do I ask a question?

**Interactive mode:**
```bash
python jarvis.py --interactive
You: ask What is Python?
```

**Command mode:**
```bash
python jarvis.py ask "What is Python?"
```

**Via API:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?"}'
```

### What's the difference between 'ask' and 'search'?

- **ask**: Uses AI knowledge + web search for comprehensive answer
- **search**: Shows web search results directly

Both can access the internet, but `ask` synthesizes information while `search` shows sources.

### How does SECI remember conversations?

SECI maintains conversation context within a session:
- Uses session IDs to track conversations
- Stores last ~20 messages
- Context expires when you exit (unless saved)

### Can SECI learn from my conversations?

**Currently**: No, conversations aren't used for training by default
**Future**: Optional feedback-based learning (coming in v1.0)

### What languages does SECI support?

**Currently**: Primarily English
**Future**: Multi-language support planned

The model can understand and generate some other languages, but English works best.

### How accurate is SECI?

**Accuracy depends on**:
- Quality of web sources
- Complexity of question
- Availability of information

Always verify important information from original sources (citations provided).

## Technical Questions

### How does SECI work?

**Simplified**:
1. You ask a question
2. SECI searches the web
3. Scrapes and reads content
4. Synthesizes an answer
5. Provides citations

**Technical**:
- Compact Transformer model (8M params)
- External memory for knowledge storage
- Knowledge distillation for learning
- Experience replay for continual learning

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

### Can I train SECI on my own data?

Yes! See the training guide:

```python
from train import SECITrainer
from seci.config import SECIConfig

config = SECIConfig.from_yaml("config/default.yaml")
trainer = SECITrainer(config)
trainer.train(your_dataloader, num_epochs=3)
```

### Can I add new search providers?

Yes! Implement the provider interface:

```python
from seci.search import SearchProvider, SearchResult

class MyProvider(SearchProvider):
    def search(self, query: str, num_results: int) -> List[SearchResult]:
        # Your implementation
        return results

# Use it
engine.add_provider(MyProvider())
```

### Can I use SECI's components separately?

Yes! All components are modular:

```python
# Just use search
from seci.search import SearchEngine, DuckDuckGoProvider
engine = SearchEngine()
engine.add_provider(DuckDuckGoProvider())
results = engine.search("query")

# Just use the model
from seci.core.model import CompactTransformer
model = CompactTransformer(...)
outputs = model(input_ids)
```

### How do I optimize performance?

**For faster responses**:
1. Enable caching
2. Reduce search results
3. Skip content scraping
4. Use minimal mode

**For lower memory**:
1. Use low_resource.yaml config
2. Enable quantization
3. Reduce memory/buffer sizes

See [USER_GUIDE.md](USER_GUIDE.md) for details.

## Privacy & Security

### Is my data safe?

Yes! SECI:
- ✅ Runs locally on your device
- ✅ Doesn't send data to external servers (except web searches)
- ✅ No telemetry or tracking
- ✅ Open source (audit the code yourself)

### What data leaves my device?

Only web search queries go to:
- Search providers (DuckDuckGo, Google, Bing)
- Websites being scraped

Your conversations and training data stay local.

### Can I use SECI for sensitive work?

Yes, but:
- Review what you search for (queries go to search providers)
- Consider using only local knowledge (no web search)
- Deploy API behind firewall for team use
- Audit the code if handling critical data

### Is SECI compliant with GDPR/privacy laws?

SECI itself:
- ✅ Doesn't collect personal data
- ✅ No cookies or tracking
- ✅ No data retention (local only)

**Your responsibility**:
- How you deploy it
- What data you process
- How you configure it

## Deployment Questions

### Can I deploy SECI as a web service?

Yes! See [DEPLOYMENT.md](docs/DEPLOYMENT.md):

```bash
# Start API server
uvicorn api:app --host 0.0.0.0 --port 8000

# Or use Docker
docker build -t seci .
docker run -p 8000:8000 seci
```

### How do I deploy for a team?

Options:
1. **Shared server**: Everyone accesses same API
2. **Individual instances**: Each person runs own instance
3. **Hybrid**: API server + individual models

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for multi-user setup.

### What's the cost to deploy SECI?

**Hardware costs**:
- Cloud VPS: $5-20/month (DigitalOcean, AWS, etc.)
- Or: Use existing hardware (free)

**Operational costs**:
- Search API keys: Optional (free tier available)
- Bandwidth: Minimal
- Maintenance: Your time

### Can SECI scale to thousands of users?

Current version: No (single-process, in-memory)
Future version: Yes (distributed architecture planned)

For now:
- Use caching aggressively
- Deploy multiple instances behind load balancer
- Consider queuing for heavy loads

## Troubleshooting

### SECI is slow, how do I fix it?

**Common causes**:
1. Slow internet → Check connection
2. No caching → Enable caching
3. Too many results → Reduce max_results
4. Heavy scraping → Skip scraping or reduce URLs

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions.

### Installation failed, what do I do?

**Common fixes**:
1. Update pip: `pip install --upgrade pip`
2. Try minimal: `pip install -r requirements-minimal.txt`
3. Check Python version: `python --version` (need 3.8+)
4. Use virtual environment

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details.

### API returns errors, how do I debug?

**Steps**:
1. Check server logs
2. Test with curl: `curl http://localhost:8000/health`
3. Enable debug mode
4. Check firewall/ports

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions.

## Contributing & Development

### How can I contribute?

Many ways:
- **Code**: Bug fixes, features, optimizations
- **Documentation**: Improve docs, add examples
- **Testing**: Report bugs, test new features
- **Community**: Help others, answer questions

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### I found a bug, what should I do?

1. Check if already reported (GitHub Issues)
2. Verify it's reproducible
3. Create detailed bug report
4. Include: OS, Python version, error logs

Use the bug report template in [CONTRIBUTING.md](CONTRIBUTING.md).

### Can I request a feature?

Yes! We welcome feature requests:
1. Check roadmap first
2. Search existing requests
3. Open GitHub Discussion
4. Describe use case and benefits

See [ROADMAP.md](ROADMAP.md) for planned features.

### How do I set up development environment?

```bash
# Fork and clone
git clone https://github.com/YOUR-USERNAME/ai.git
cd ai

# Install in dev mode
pip install -e .
pip install pytest black isort flake8

# Make changes and test
pytest
black seci/
```

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for details.

## Future Plans

### What's on the roadmap?

**Short-term (3-6 months)**:
- Web interface
- Multi-modal support (images, audio)
- Voice interface
- Mobile apps

**Long-term (1-2 years)**:
- Plugin system
- Multi-agent collaboration
- Better reasoning
- Enterprise features

See [ROADMAP.md](ROADMAP.md) for complete plan.

### Will SECI always be free?

**Core software**: Always free and open source (MIT License)

**Potential future**:
- Premium hosted version (optional)
- Enterprise support (optional)
- Additional features (optional)

Open source version will always be available and capable.

### Can I sponsor development?

Yes! (Coming soon)
- GitHub Sponsors
- OpenCollective
- Direct contributions

Stay tuned for details.

## Getting Help

### Where do I get help?

1. **Documentation**: Check docs/ folder
2. **FAQ**: You're reading it! 😊
3. **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **GitHub Discussions**: Ask the community
5. **GitHub Issues**: Report bugs

### I have a question not answered here

**Please**:
1. Search documentation
2. Check GitHub Discussions
3. Ask in GitHub Discussions (preferred)
4. Open GitHub Issue (if bug/feature request)

### How do I stay updated?

- **GitHub**: Watch the repository
- **Releases**: Check GitHub Releases
- **Blog**: Coming soon
- **Discord**: Coming soon
- **Twitter**: Coming soon

---

## Have More Questions?

**Ask us!**
- GitHub Discussions: For questions and discussions
- GitHub Issues: For bugs and feature requests
- Email: Coming soon

**We're here to help! 🤝**
