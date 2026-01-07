# SECI: Self-Evolving Compact Intelligence + Perplexity-like Search

A modular PyTorch framework for efficient continual learning with compact transformers, **now enhanced with Perplexity-like web search capabilities**. SECI combines knowledge distillation, external memory, experience replay, and parameter-efficient training (LoRA, quantization) with intelligent web search, scraping, and conversational AI.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Key Features

### Core AI Features
- **Compact Transformer Core**: Small, efficient transformer (256 hidden, 4 layers, ~8M params)
- **External Memory**: Attention-based key-value memory for knowledge storage
- **Knowledge Distillation**: Transfer learning from larger teacher models
- **Experience Replay**: Buffer with multiple sampling strategies (reservoir, priority)
- **Parameter Efficiency**: LoRA adapters (~1% trainable params) and 8-bit quantization
- **Continual Learning**: Designed to prevent catastrophic forgetting
- **Modular Design**: Easy to extend, customize, and integrate

### 🔍 NEW: Perplexity-like Search Features
- **Web Search Integration**: Multi-provider support (DuckDuckGo, Google, Bing)
- **Intelligent Web Scraping**: Extract and process content from search results
- **Conversational Context**: Maintain conversation history across sessions
- **Citation Tracking**: Provide sources for all information
- **REST API**: FastAPI-based API server ready for deployment
- **Fast & Scalable**: Built-in caching and async processing
- **Production Ready**: Deploy on any VPS with comprehensive documentation

## 📋 Table of Contents

- [Architecture](#architecture)
- [Perplexity-like Search](#perplexity-like-search)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Search & Web Features](#search--web-features)
- [Configuration](#configuration)
- [Training](#training)
- [Advanced Usage](#advanced-usage)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Examples](#examples)
- [Contributing](#contributing)
- [Citation](#citation)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SECI System                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input → [Student Model] → Hidden States               │
│              ↓                    ↓                     │
│         [Logits]          [External Memory]            │
│              ↓                    ↓                     │
│         [Teacher Model]    Memory-Augmented            │
│              ↓              Representations             │
│    [Knowledge Distiller] ←─────────┘                   │
│              ↓                                          │
│         Combined Loss                                   │
│              ↓                                          │
│      Parameter Updates                                  │
│              ↓                                          │
│      [Replay Buffer] → Experience Replay               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### System Components

1. **CompactTransformer**: Efficient student model with LoRA/quantization
2. **TeacherModel**: Larger frozen model for knowledge distillation
3. **ExternalMemory**: Attention-based memory bank (1000 slots)
4. **KnowledgeDistiller**: Manages distillation loss computation
5. **ReplayBuffer**: Stores experiences for continual learning (10K samples)

See [Architecture Documentation](docs/EXECUTION_FLOW.md) for detailed execution flow.

## 🔍 Perplexity-like Search

SECI now includes comprehensive web search capabilities similar to Perplexity AI:

```
┌────────────────────────────────────────────────────────┐
│           SECI Search System (NEW!)                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  User Query → [Query Processor]                       │
│                       ↓                                │
│              [Search Engine]                           │
│                 ↓         ↓                            │
│        [DuckDuckGo]  [Google]                         │
│                 ↓                                      │
│              Search Results                            │
│                 ↓                                      │
│              [Web Scraper]                            │
│                 ↓                                      │
│            Scraped Content                            │
│                 ↓                                      │
│         [Response Generator]                          │
│                 ↓                                      │
│    Response with Citations                            │
│                 ↓                                      │
│         [Context Manager]                             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Quick Search Example

```python
from seci import SearchEngine, WebScraper, ContextManager, QueryProcessor
from seci.search import DuckDuckGoProvider

# Initialize components
search_engine = SearchEngine()
search_engine.add_provider(DuckDuckGoProvider())
scraper = WebScraper()
context = ContextManager()

# Create processor
processor = QueryProcessor(search_engine, scraper, context)

# Process query
result = processor.process("What is artificial intelligence?")
print(result.response)
print(result.citations)
```

### API Server

```bash
# Start API server
python api.py

# Make search request
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "max_results": 5}'
```

See [Search System Documentation](docs/SEARCH_SYSTEM.md) for complete details.

## 📦 Installation

### Prerequisites

- Python 3.8+
- PyTorch 2.0+
- CUDA (optional, for GPU acceleration)

### Install from Source

```bash
git clone https://github.com/AkshatNaruka/ai.git
cd ai
pip install -r requirements.txt
pip install -e .
```

### Dependencies

- `torch>=2.0.0` - Deep learning framework
- `transformers>=4.35.0` - Transformer utilities
- `peft>=0.7.0` - Parameter-efficient fine-tuning (LoRA)
- `numpy>=1.24.0` - Numerical operations
- `pyyaml>=6.0` - Configuration management
- `tqdm>=4.65.0` - Progress bars

## 🚀 Quick Start

### Basic Training

```python
from seci import SECIConfig, CompactTransformer, TeacherModel
from train import SECITrainer

# Load default configuration
config = SECIConfig.from_yaml("config/default.yaml")

# Create trainer
trainer = SECITrainer(config)

# Train (with your dataloader)
trainer.train(train_dataloader, num_epochs=3)
```

### Command Line

```bash
# Train with default config
python train.py --config config/default.yaml --output_dir ./outputs

# Train with low-resource config (CPU/small GPU)
python train.py --config config/low_resource.yaml --output_dir ./outputs

# Custom training
python train.py --config config/default.yaml --num_epochs 5
```

### Minimal Example

```python
import torch
from seci import CompactTransformer, ExternalMemory, ReplayBuffer

# Initialize model
model = CompactTransformer(
    vocab_size=32000,
    hidden_size=256,
    num_layers=4,
    num_heads=4,
    intermediate_size=1024,
    max_seq_length=512
)

# Forward pass
input_ids = torch.randint(0, 32000, (2, 128))  # (batch, seq_len)
outputs = model(input_ids, return_hidden_states=True)

print(f"Logits shape: {outputs['logits'].shape}")  # (2, 128, 32000)
print(f"Hidden states: {len(outputs['hidden_states'])} layers")
print(f"Parameters: {model.get_trainable_params():,}")
```

## 🧩 Core Components

### 1. Compact Transformer

```python
from seci.core.model import CompactTransformer

model = CompactTransformer(
    vocab_size=32000,
    hidden_size=256,
    num_layers=4,
    num_heads=4,
    intermediate_size=1024,
    max_seq_length=512,
    use_lora=True,        # Enable LoRA
    lora_r=8,             # LoRA rank
    use_quantization=True # Enable 8-bit quantization
)

# Enable LoRA for fine-tuning
model.enable_lora()  # Only trains LoRA params (~1% of total)
```

### 2. External Memory

```python
from seci.memory.external_memory import ExternalMemory

memory = ExternalMemory(
    memory_size=1000,      # Number of memory slots
    embedding_dim=256,     # Must match model hidden size
    retrieval_top_k=5      # Retrieve top-5 memories
)

# Read from memory
query = model.last_hidden_state  # (batch, seq_len, dim)
retrieved, attention = memory.read(query, return_attention=True)

# Write to memory
memory.update_from_hidden_states(model.last_hidden_state)

# Check stats
stats = memory.get_memory_stats()
print(f"Memory utilization: {stats['memory_utilization']:.2%}")
```

### 3. Knowledge Distillation

```python
from seci.distillation.distiller import KnowledgeDistiller

distiller = KnowledgeDistiller(
    temperature=2.0,      # Softness of distributions
    alpha=0.5,            # Balance: distillation vs task loss
    distill_loss_type="kl_div"  # KL divergence
)

# Compute loss
loss_dict = distiller(
    student_outputs=student_outputs,
    teacher_outputs=teacher_outputs,
    labels=labels
)

print(f"Total loss: {loss_dict['loss']:.4f}")
print(f"Distillation: {loss_dict['distill_loss']:.4f}")
print(f"Task loss: {loss_dict['task_loss']:.4f}")
```

### 4. Replay Buffer

```python
from seci.replay.buffer import ReplayBuffer

buffer = ReplayBuffer(
    buffer_size=10000,
    replay_batch_size=32,
    sampling_strategy="reservoir"  # or "priority", "random"
)

# Add experiences
buffer.add(input_ids, attention_mask, labels, priority=loss.item())

# Sample for replay
replay_batch = buffer.sample(device="cuda")

# Check stats
stats = buffer.get_stats()
print(f"Buffer: {stats['current_size']}/{stats['buffer_size']}")
```

## 🌐 Search & Web Features

### 1. Web Search

```python
from seci.search import SearchEngine, DuckDuckGoProvider, GoogleSearchProvider

# Initialize search engine
engine = SearchEngine(max_results=10)
engine.add_provider(DuckDuckGoProvider())  # No API key needed
engine.add_provider(GoogleSearchProvider())  # Optional

# Search the web
results = engine.search("artificial intelligence", num_results=5)
for result in results:
    print(f"[{result.source}] {result.title}: {result.url}")
```

### 2. Web Scraping

```python
from seci.scraper import WebScraper

# Initialize scraper
scraper = WebScraper(timeout=10, max_content_length=50000)

# Scrape a URL
content = scraper.scrape("https://example.com")
print(f"Title: {content.title}")
print(f"Content: {content.content[:500]}...")
print(f"Metadata: {content.metadata}")

# Scrape multiple URLs
urls = [result.url for result in results[:3]]
contents = scraper.scrape_multiple(urls)
```

### 3. Conversational Context

```python
from seci.context import ContextManager

# Initialize context manager
manager = ContextManager(max_history=20)

# Add messages to conversation
manager.add_user_message("session-123", "What is AI?")
manager.add_assistant_message("session-123", "AI is...")

# Get conversation history
history = manager.get_history("session-123")
for msg in history:
    print(f"{msg.role}: {msg.content}")

# Export conversation
json_data = manager.export_context("session-123")
```

### 4. Query Processing

```python
from seci.query_processor import QueryProcessor

# Initialize processor with all components
processor = QueryProcessor(
    search_engine=engine,
    web_scraper=scraper,
    context_manager=manager,
    max_sources=5,
    scrape_top_n=3
)

# Process a query (search + scrape + generate response)
result = processor.process(
    query="What are the latest AI developments?",
    session_id="user-123"
)

print(f"Response: {result.response}")
print(f"Citations: {len(result.citations)}")
for citation in result.citations:
    print(f"  [{citation['number']}] {citation['title']}")
```

### 5. REST API Server

```bash
# Start the API server
python api.py

# Or with uvicorn for production
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

API Endpoints:
- `POST /search` - Search and generate response
- `GET /conversation/{session_id}` - Get conversation history
- `DELETE /conversation/{session_id}` - Clear conversation
- `GET /sessions` - List all sessions
- `GET /health` - Health check

Example API usage:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "session_id": "user-123",
    "max_results": 5,
    "scrape_content": true
  }'
```
```

## ⚙️ Configuration

SECI uses a hierarchical YAML-based configuration system.

### Configuration Structure

```yaml
model:           # Model architecture
  hidden_size: 256
  num_layers: 4
  use_lora: false
  use_quantization: false

memory:          # External memory
  memory_size: 1000
  retrieval_top_k: 5

distillation:    # Knowledge distillation
  temperature: 2.0
  alpha: 0.5

replay:          # Experience replay
  buffer_size: 10000
  sampling_strategy: reservoir

training:        # Training hyperparameters
  batch_size: 32
  learning_rate: 0.0001
  max_steps: 10000
```

### Pre-configured Setups

| Config | Model Size | Parameters | Memory | Use Case |
|--------|-----------|------------|---------|----------|
| `default.yaml` | 256 hidden, 4 layers | ~8M | <2GB | Standard GPU |
| `low_resource.yaml` | 128 hidden, 2 layers | ~2M | <1GB | CPU/small GPU |

### Load and Modify

```python
from seci.config.config import SECIConfig

# Load from file
config = SECIConfig.from_yaml("config/default.yaml")

# Modify
config.model.use_lora = True
config.training.learning_rate = 5e-5

# Save
config.to_yaml("config/my_config.yaml")
```

See [Configuration Guide](docs/CONFIG_STRATEGY.md) for details.

## 🎓 Training

### Full Training Pipeline

```python
from train import SECITrainer
from seci.config.config import SECIConfig

# Setup
config = SECIConfig.from_yaml("config/default.yaml")
trainer = SECITrainer(config)

# Train
trainer.train(train_dataloader, num_epochs=3)

# Checkpoints saved at:
# - outputs/checkpoint_step_1000.pt
# - outputs/memory_step_1000.pt
# - outputs/buffer_step_1000.pt
```

### Training Loop Components

Each training step:
1. **Forward pass** through student model
2. **Memory retrieval** for augmented representations
3. **Teacher forward pass** (frozen)
4. **Distillation loss** computation
5. **Backward pass** and parameter updates
6. **Memory update** with current hidden states
7. **Replay buffer** addition
8. **Periodic replay** (every N steps)

### Monitoring

```python
# During training
print(f"Step {step}:")
print(f"  Loss: {loss:.4f}")
print(f"  Distillation: {distill_loss:.4f}")
print(f"  Learning rate: {lr:.2e}")
print(f"  Memory utilization: {memory_stats['memory_utilization']:.2%}")
print(f"  Buffer utilization: {buffer_stats['utilization']:.2%}")
```

## 🔬 Advanced Usage

### Enable LoRA for Fine-tuning

```python
# Train only LoRA adapters (~1% of parameters)
config.model.use_lora = True
config.model.lora_r = 8
config.model.lora_alpha = 16

model = CompactTransformer(**config.model.__dict__)
model.enable_lora()  # Freeze base, unfreeze LoRA

print(f"Trainable: {model.get_trainable_params():,}")  # ~80K params
```

### Custom Teacher Model

```python
from seci.core.teacher import TeacherModel

# Use your own pre-trained model
teacher = TeacherModel(model=your_pretrained_model)

# Or create larger version of student
teacher_config = {
    'vocab_size': 32000,
    'hidden_size': 512,  # 2x larger
    'num_layers': 8,     # 2x deeper
    ...
}
teacher = TeacherModel(use_compact_as_teacher=True, teacher_config=teacher_config)
```

### Priority-Based Replay

```python
# Focus replay on hard examples
buffer = ReplayBuffer(
    buffer_size=10000,
    sampling_strategy="priority",
    priority_alpha=0.6  # Higher = more focus on high-priority
)

# Add with priority
buffer.add(input_ids, attention_mask, labels, priority=loss.item())

# Update priorities after training
buffer.update_priorities(indices, new_priorities)
```

### Memory Management

```python
# Save/load memory
memory.save_memory("memory_checkpoint.pt")
memory.load_memory("memory_checkpoint.pt")

# Reset memory
memory.reset_memory()

# Get detailed stats
stats = memory.get_memory_stats()
print(f"Total accesses: {stats['total_accesses']}")
print(f"Average age: {stats['avg_memory_age']:.1f}")
```

## 🚀 Deployment

### VPS Deployment

Deploy SECI Search API on your VPS in minutes:

```bash
# 1. Clone repository
git clone https://github.com/AkshatNaruka/ai.git
cd ai

# 2. Install dependencies
pip install -r requirements.txt
pip install -e .

# 3. Run API server
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# 4. Configure Nginx (optional)
# 5. Setup SSL with Let's Encrypt (optional)
```

### Systemd Service

Create `/etc/systemd/system/seci-api.service`:

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

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable seci-api
sudo systemctl start seci-api
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t seci-search .
docker run -p 8000:8000 seci-search
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment guide.
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

### Core Documentation
- **[Repo Structure](docs/REPO_TREE.txt)**: Complete file tree
- **[Module Responsibilities](docs/MODULE_RESPONSIBILITIES.md)**: What each module does
- **[Execution Flow](docs/EXECUTION_FLOW.md)**: End-to-end training pipeline
- **[Core Interfaces](docs/CORE_INTERFACES.md)**: API reference for all components
- **[Configuration Strategy](docs/CONFIG_STRATEGY.md)**: Configuration guide
- **[MVP Metrics](docs/MVP_METRICS.md)**: Success criteria and benchmarks

### Search System Documentation (NEW)
- **[Search System Overview](docs/SEARCH_SYSTEM.md)**: Complete guide to search features
- **[Deployment Guide](docs/DEPLOYMENT.md)**: VPS deployment instructions
- **[API Reference](docs/SEARCH_SYSTEM.md#api-usage)**: REST API documentation

## 💡 Examples

Example scripts demonstrate key features:

```bash
# Core training examples
examples/
├── basic_training.py         # Simple training loop
├── continual_learning.py     # Multi-task learning
└── perplexity_search.py      # NEW: Web search example

# Run Perplexity-like search example
python examples/perplexity_search.py
```

### Quick Examples

**Web Search:**
```python
from seci.search import SearchEngine, DuckDuckGoProvider

engine = SearchEngine()
engine.add_provider(DuckDuckGoProvider())
results = engine.search("artificial intelligence")
```

**Full Query Processing:**
```python
from seci import QueryProcessor

result = processor.process("What is machine learning?")
print(result.response)
```

**API Client:**
```python
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={"query": "What is AI?"}
)
print(response.json()['response'])
```

## 🛠️ Development

### Run Tests

```bash
# Coming soon
pytest tests/
```

### Code Style

```bash
# Format code
black seci/
isort seci/

# Lint
flake8 seci/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- PyTorch team for the deep learning framework
- Hugging Face for transformer implementations and PEFT
- Research papers on continual learning, knowledge distillation, and efficient transformers

## 📧 Contact

Project Link: [https://github.com/AkshatNaruka/ai](https://github.com/AkshatNaruka/ai)

## 🔗 Related Work

- **Knowledge Distillation**: Hinton et al. (2015) - Distilling the Knowledge in a Neural Network
- **LoRA**: Hu et al. (2021) - LoRA: Low-Rank Adaptation of Large Language Models
- **Experience Replay**: Rolnick et al. (2019) - Experience Replay for Continual Learning
- **External Memory**: Graves et al. (2014) - Neural Turing Machines

---

**Built with ❤️ for efficient and continual learning**
