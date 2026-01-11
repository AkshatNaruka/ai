# Developer Guide

A comprehensive guide for developers who want to understand, modify, or contribute to the SECI codebase.

## Table of Contents
- [Development Setup](#development-setup)
- [Code Organization](#code-organization)
- [Key Concepts](#key-concepts)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Debugging](#debugging)
- [Best Practices](#best-practices)
- [Common Tasks](#common-tasks)

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool (venv/conda)
- Code editor (VS Code, PyCharm, etc.)

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone https://github.com/AkshatNaruka/ai.git
cd ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install in development mode
pip install -e .  # Editable install
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest black isort flake8 mypy

# 5. Verify installation
python -c "import seci; print(seci.__file__)"
```

### Development Tools

**Recommended VS Code Extensions:**
- Python
- Pylance
- Python Test Explorer
- GitLens
- YAML

**Recommended Settings** (`.vscode/settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true
}
```

## Code Organization

### Directory Structure

```
seci/
├── __init__.py              # Package initialization
├── core/                    # Core AI components
│   ├── __init__.py
│   ├── model.py            # Compact Transformer
│   └── teacher.py          # Teacher Model
├── memory/                  # External memory system
│   ├── __init__.py
│   └── external_memory.py
├── distillation/           # Knowledge distillation
│   ├── __init__.py
│   └── distiller.py
├── replay/                 # Experience replay
│   ├── __init__.py
│   └── buffer.py
├── search/                 # Web search system
│   ├── __init__.py
│   ├── search_engine.py   # Main search engine
│   ├── providers.py       # Search providers
│   └── async_search.py    # Async search utilities
├── scraper/                # Web scraping
│   ├── __init__.py
│   ├── scraper.py         # Main scraper
│   └── content_extractor.py
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── helpers.py         # General utilities
│   ├── query_enhancer.py  # Query enhancement
│   ├── result_ranker.py   # Result ranking
│   └── intelligent_cache.py
├── config/                 # Configuration management
│   ├── __init__.py
│   └── config.py
├── context/                # Conversation context
│   ├── __init__.py
│   └── context_manager.py
├── query_processor.py      # Main query orchestrator
└── enhanced_processor.py   # Enhanced version with optimizations
```

### Module Responsibility Summary

| Module | Responsibility | Key Classes |
|--------|---------------|-------------|
| `core/` | AI model implementation | `CompactTransformer`, `TeacherModel` |
| `memory/` | External memory management | `ExternalMemory` |
| `distillation/` | Knowledge transfer | `KnowledgeDistiller` |
| `replay/` | Experience replay | `ReplayBuffer` |
| `search/` | Web search | `SearchEngine`, `DuckDuckGoProvider` |
| `scraper/` | Content extraction | `WebScraper`, `ContentExtractor` |
| `utils/` | Utilities & enhancements | `QueryEnhancer`, `ResultRanker` |
| `config/` | Configuration | `SECIConfig` |

## Key Concepts

### 1. Configuration System

SECI uses a hierarchical configuration system with YAML files and Python dataclasses.

**Example: Using Configuration**
```python
from seci.config.config import SECIConfig

# Load from file
config = SECIConfig.from_yaml("config/default.yaml")

# Access nested config
print(config.model.hidden_size)  # 256
print(config.training.learning_rate)  # 0.0001

# Modify
config.model.use_lora = True
config.training.batch_size = 16

# Save
config.to_yaml("config/my_config.yaml")
```

**Creating Custom Config:**
```python
from seci.config.config import ModelConfig, SECIConfig

# Custom model config
model_config = ModelConfig(
    vocab_size=50000,
    hidden_size=512,
    num_layers=8,
    use_lora=True,
    lora_r=16
)

# Build full config
config = SECIConfig(
    model=model_config,
    # ... other configs
)
```

### 2. Component Interfaces

All major components follow consistent interfaces:

**Model Interface:**
```python
class Model:
    def forward(self, input_ids, attention_mask=None, return_hidden_states=False):
        """
        Args:
            input_ids: [batch_size, seq_len]
            attention_mask: [batch_size, seq_len]
            return_hidden_states: bool
        
        Returns:
            dict with 'logits' and optionally 'hidden_states'
        """
        pass
```

**Memory Interface:**
```python
class Memory:
    def read(self, query):
        """Retrieve relevant memories"""
        pass
    
    def write(self, keys, values):
        """Store new memories"""
        pass
    
    def update_from_hidden_states(self, hidden_states):
        """Auto-update from model outputs"""
        pass
```

**Search Provider Interface:**
```python
class SearchProvider:
    def search(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Search for query and return results
        """
        pass
```

### 3. Training Pipeline

**Understanding the Training Loop:**

```python
# Simplified training loop structure
def train_step(batch):
    # 1. Student forward
    student_out = student(batch.input_ids, return_hidden_states=True)
    
    # 2. Memory retrieval
    memories = memory.read(student_out['hidden_states'][-1])
    
    # 3. Teacher forward (frozen)
    with torch.no_grad():
        teacher_out = teacher(batch.input_ids, return_hidden_states=True)
    
    # 4. Compute loss
    loss_dict = distiller(
        student_outputs=student_out,
        teacher_outputs=teacher_out,
        labels=batch.labels
    )
    
    # 5. Backward pass
    loss_dict['loss'].backward()
    optimizer.step()
    
    # 6. Update components
    memory.update_from_hidden_states(student_out['hidden_states'][-1])
    replay_buffer.add(batch, priority=loss_dict['loss'].item())
    
    return loss_dict
```

## Adding New Features

### Example 1: Adding a New Search Provider

**Step 1: Create Provider Class**

```python
# seci/search/providers.py

class BingSearchProvider:
    """Bing search provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BING_API_KEY")
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Search using Bing API
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {"q": query, "count": num_results}
        
        try:
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("webPages", {}).get("value", []):
                results.append(SearchResult(
                    title=item["name"],
                    url=item["url"],
                    snippet=item["snippet"],
                    source="bing"
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            return []
```

**Step 2: Register Provider**

```python
# In your code or jarvis.py
from seci.search import SearchEngine, BingSearchProvider

engine = SearchEngine()
engine.add_provider(BingSearchProvider(api_key="your-key"))
```

**Step 3: Add Tests**

```python
# tests/test_bing_provider.py
import pytest
from seci.search.providers import BingSearchProvider

def test_bing_search():
    provider = BingSearchProvider(api_key="test-key")
    results = provider.search("test query", num_results=5)
    
    assert len(results) <= 5
    assert all(r.source == "bing" for r in results)
```

### Example 2: Adding a New Memory Strategy

**Step 1: Extend ExternalMemory**

```python
# seci/memory/external_memory.py

class ExternalMemory:
    # ... existing code ...
    
    def update_with_importance(self, keys, values, importance_scores):
        """
        Update memory prioritizing important information
        
        Args:
            keys: [batch_size, embedding_dim]
            values: [batch_size, embedding_dim]
            importance_scores: [batch_size] - higher = more important
        """
        batch_size = keys.shape[0]
        
        # Find slots to update (lowest importance)
        current_importance = self.usage_count / (self.age + 1)
        slots_to_update = torch.argsort(current_importance)[:batch_size]
        
        # Update selected slots
        for i, slot in enumerate(slots_to_update):
            if importance_scores[i] > current_importance[slot]:
                self.memory_keys[slot] = keys[i]
                self.memory_values[slot] = values[i]
                self.usage_count[slot] = importance_scores[i]
                self.age[slot] = 0
```

### Example 3: Adding Enhanced Features

**Step 1: Create Feature Module**

```python
# seci/utils/semantic_cache.py

import torch
from typing import Dict, Optional
from sentence_transformers import SentenceTransformer

class SemanticCache:
    """Cache with semantic similarity matching"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.embeddings: Dict[str, torch.Tensor] = {}
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.max_size = max_size
        self.threshold = 0.85  # Similarity threshold
    
    def get(self, query: str) -> Optional[Any]:
        """Get cached result for semantically similar query"""
        query_emb = self.encoder.encode(query)
        
        # Check for exact match first
        if query in self.cache:
            return self.cache[query]
        
        # Check for semantic match
        best_similarity = 0
        best_match = None
        
        for cached_query, cached_emb in self.embeddings.items():
            similarity = torch.cosine_similarity(
                torch.tensor(query_emb),
                cached_emb,
                dim=0
            )
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cached_query
        
        if best_similarity > self.threshold:
            return self.cache[best_match]
        
        return None
    
    def set(self, query: str, result: Any):
        """Cache result with query embedding"""
        if len(self.cache) >= self.max_size:
            # Remove oldest (simple LRU)
            oldest = next(iter(self.cache))
            del self.cache[oldest]
            del self.embeddings[oldest]
        
        self.cache[query] = result
        self.embeddings[query] = torch.tensor(
            self.encoder.encode(query)
        )
```

**Step 2: Integrate**

```python
# seci/enhanced_processor.py

from seci.utils.semantic_cache import SemanticCache

class EnhancedQueryProcessor(QueryProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.semantic_cache = SemanticCache()
    
    def process(self, query: str, session_id: str = None):
        # Check semantic cache
        cached = self.semantic_cache.get(query)
        if cached:
            logger.info(f"Semantic cache hit for: {query}")
            return cached
        
        # Process normally
        result = super().process(query, session_id)
        
        # Cache result
        self.semantic_cache.set(query, result)
        
        return result
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_model.py

# Run with coverage
pytest --cov=seci --cov-report=html

# Run specific test
pytest tests/test_model.py::test_forward_pass
```

### Writing Tests

**Example Test Structure:**

```python
# tests/test_compact_transformer.py
import pytest
import torch
from seci.core.model import CompactTransformer

class TestCompactTransformer:
    @pytest.fixture
    def model(self):
        """Create model instance for tests"""
        return CompactTransformer(
            vocab_size=1000,
            hidden_size=128,
            num_layers=2,
            num_heads=4
        )
    
    def test_forward_pass(self, model):
        """Test basic forward pass"""
        batch_size = 2
        seq_len = 10
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        outputs = model(input_ids)
        
        assert 'logits' in outputs
        assert outputs['logits'].shape == (batch_size, seq_len, 1000)
    
    def test_lora_parameters(self, model):
        """Test LoRA parameter efficiency"""
        total_before = model.get_trainable_params()
        
        model.enable_lora()
        total_after = model.get_trainable_params()
        
        assert total_after < total_before * 0.02  # <2% trainable
    
    def test_hidden_states(self, model):
        """Test hidden state output"""
        input_ids = torch.randint(0, 1000, (2, 10))
        outputs = model(input_ids, return_hidden_states=True)
        
        assert 'hidden_states' in outputs
        assert len(outputs['hidden_states']) == 2  # num_layers
```

## Debugging

### Common Debugging Scenarios

**1. Model Not Learning**

```python
# Check gradients
for name, param in model.named_parameters():
    if param.grad is not None:
        grad_norm = param.grad.norm()
        print(f"{name}: {grad_norm:.4f}")
    else:
        print(f"{name}: No gradient!")

# Check if parameters are frozen
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"Trainable: {trainable}/{total} ({100*trainable/total:.1f}%)")
```

**2. Memory Issues**

```python
# Monitor memory usage
import torch

print(f"Allocated: {torch.cuda.memory_allocated()/1e9:.2f} GB")
print(f"Cached: {torch.cuda.memory_reserved()/1e9:.2f} GB")

# Clear cache
torch.cuda.empty_cache()

# Use gradient checkpointing
model.gradient_checkpointing_enable()
```

**3. Slow Training**

```python
# Profile code
import time

start = time.time()
# ... code to profile ...
end = time.time()
print(f"Time: {end - start:.2f}s")

# Use PyTorch profiler
with torch.profiler.profile() as prof:
    # ... training loop ...
    pass

print(prof.key_averages().table())
```

**4. Search Not Working**

```python
# Test provider directly
from seci.search.providers import DuckDuckGoProvider

provider = DuckDuckGoProvider()
results = provider.search("test", num_results=5)
print(f"Got {len(results)} results")
for r in results:
    print(f"  {r.title}: {r.url}")

# Check logs
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### Code Style

**Follow PEP 8:**
```bash
# Format code
black seci/
isort seci/

# Check style
flake8 seci/
```

**Type Hints:**
```python
from typing import List, Dict, Optional, Tuple

def process_batch(
    input_ids: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None
) -> Dict[str, torch.Tensor]:
    """
    Process input batch
    
    Args:
        input_ids: Input token IDs [batch_size, seq_len]
        attention_mask: Attention mask [batch_size, seq_len]
    
    Returns:
        Dictionary with logits and hidden states
    """
    pass
```

### Documentation

**Docstring Format:**
```python
def complex_function(param1: int, param2: str) -> List[str]:
    """
    One-line summary of what the function does
    
    More detailed explanation if needed. Can span multiple lines.
    Explain the purpose, not the implementation.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is negative
        TypeError: When param2 is not a string
    
    Example:
        >>> result = complex_function(5, "test")
        >>> print(result)
        ['output1', 'output2']
    """
    pass
```

### Error Handling

**Be Specific:**
```python
# Good
try:
    results = search_engine.search(query)
except requests.Timeout:
    logger.error("Search timeout")
    return []
except requests.HTTPError as e:
    logger.error(f"HTTP error: {e.response.status_code}")
    return []

# Bad
try:
    results = search_engine.search(query)
except Exception as e:
    print(f"Error: {e}")  # Too broad, no logging
    pass
```

### Logging

**Use Appropriate Levels:**
```python
import logging

logger = logging.getLogger(__name__)

# DEBUG: Detailed diagnostic information
logger.debug(f"Processing batch with {len(batch)} samples")

# INFO: General informational messages
logger.info("Training started")

# WARNING: Something unexpected but handled
logger.warning("Cache miss, executing slow path")

# ERROR: Serious problem, functionality impaired
logger.error(f"Failed to load checkpoint: {e}")

# CRITICAL: Very serious error, system may crash
logger.critical("Out of memory, aborting")
```

## Common Tasks

### Task 1: Adding a Configuration Parameter

```python
# 1. Add to config dataclass
@dataclass
class ModelConfig:
    # ... existing fields ...
    new_parameter: int = 42  # New parameter with default

# 2. Update YAML files
# config/default.yaml
model:
  # ... existing config ...
  new_parameter: 42

# 3. Use in code
config = SECIConfig.from_yaml("config/default.yaml")
print(config.model.new_parameter)  # 42
```

### Task 2: Modifying the Model Architecture

```python
# seci/core/model.py

class CompactTransformer(nn.Module):
    def __init__(self, ..., new_layer_type: str = "standard"):
        super().__init__()
        # ... existing init ...
        
        # Add new functionality
        if new_layer_type == "custom":
            self.custom_layer = CustomLayer(...)
    
    def forward(self, input_ids, ...):
        # ... existing forward ...
        
        # Add new processing
        if hasattr(self, 'custom_layer'):
            hidden_states = self.custom_layer(hidden_states)
        
        return outputs
```

### Task 3: Adding Metrics/Logging

```python
# train.py

class SECITrainer:
    def __init__(self, config):
        # ... existing init ...
        self.metrics = {
            'train_loss': [],
            'distill_loss': [],
            'custom_metric': []
        }
    
    def train_step(self, batch):
        # ... training code ...
        
        # Compute custom metric
        custom_value = self.compute_custom_metric(outputs)
        self.metrics['custom_metric'].append(custom_value)
        
        # Log
        if step % 100 == 0:
            logger.info(f"Step {step}: custom_metric={custom_value:.4f}")
        
        return loss_dict
```

### Task 4: Optimizing Performance

```python
# Use torch.compile (PyTorch 2.0+)
model = torch.compile(model)

# Use mixed precision
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

with autocast():
    outputs = model(input_ids)
    loss = compute_loss(outputs, labels)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

## Next Steps

- **Read Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Study Examples**: Check `examples/` directory
- **Join Community**: GitHub Discussions
- **Contribute**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Happy Coding! Build amazing things with SECI! 🚀**
