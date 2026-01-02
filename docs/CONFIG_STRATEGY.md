# Configuration Strategy

## Overview

SECI uses a hierarchical, dataclass-based configuration system that provides:
- **Type safety** through Python dataclasses
- **YAML serialization** for easy configuration management
- **Modular structure** separating concerns (model, memory, training, etc.)
- **Default values** for quick prototyping
- **Validation** through type hints

## Configuration Hierarchy

```
SECIConfig (root)
├── ModelConfig        # Model architecture and efficiency settings
├── MemoryConfig       # External memory parameters
├── DistillationConfig # Knowledge distillation hyperparameters
├── ReplayConfig       # Experience replay settings
└── TrainingConfig     # Optimization and training loop settings
```

## Configuration Files

### 1. Default Configuration (`config/default.yaml`)
**Purpose**: Balanced setup for moderate compute (single GPU)
- Medium model size (256 hidden, 4 layers)
- Standard training parameters
- Suitable for research and experimentation

### 2. Low-Resource Configuration (`config/low_resource.yaml`)
**Purpose**: CPU or small GPU training
- Smaller model (128 hidden, 2 layers)
- LoRA enabled for parameter efficiency
- Quantization enabled for memory efficiency
- Smaller batch sizes and replay buffer

## Configuration Components

### ModelConfig
Controls the transformer architecture and efficiency features.

**Key Parameters**:
- `hidden_size`: Model width (128-512 for compact models)
- `num_layers`: Model depth (2-8 for compact models)
- `use_lora`: Enable LoRA for ~99% parameter reduction
- `use_quantization`: Enable 8-bit quantization for 4x memory savings
- `lora_r`: LoRA rank (4-16, lower = more compact)

**Efficiency Tradeoffs**:
```
No optimizations:     100% params,  100% memory
LoRA (r=8):           ~1% params,   100% memory
Quantization (8-bit): 100% params,  ~25% memory
LoRA + Quantization:  ~1% params,   ~25% memory
```

### MemoryConfig
Controls external memory system behavior.

**Key Parameters**:
- `memory_size`: Number of memory slots (500-10000)
- `embedding_dim`: Must match model `hidden_size`
- `retrieval_top_k`: Memory slots retrieved per query (3-10)
- `memory_update_rate`: Momentum for memory writes (0.001-0.1)

**Scaling Considerations**:
- Memory size impacts retrieval speed (larger = slower)
- Top-K retrieval keeps complexity manageable
- Update rate controls plasticity vs stability

### DistillationConfig
Controls knowledge transfer from teacher to student.

**Key Parameters**:
- `temperature`: Softness of distributions (1.0-5.0)
  - Higher = softer, more knowledge transfer
  - Lower = sharper, closer to hard labels
- `alpha`: Weight between distillation and task loss (0.0-1.0)
  - 1.0 = pure distillation
  - 0.0 = ignore teacher
  - 0.5 = balanced
- `distill_loss_type`: Loss function (kl_div, mse, cosine)
  - kl_div: Standard for probability matching
  - mse: Simple squared error
  - cosine: Similarity-based

**Distillation Formula**:
```
total_loss = α * distill_loss + (1-α) * task_loss + β * hidden_loss
```

### ReplayConfig
Controls experience replay for continual learning.

**Key Parameters**:
- `buffer_size`: Maximum stored experiences (5000-50000)
- `replay_frequency`: Steps between replay (1-10)
- `sampling_strategy`: How to sample (reservoir, priority, random)
  - reservoir: Uniform over time
  - priority: Focus on high-loss samples
  - random: Simple random sampling
- `priority_alpha`: Priority sharpness (0.0-1.0)

**Replay Strategies**:
```
Reservoir:  Uniform distribution, good for general retention
Priority:   Focus on hard examples, faster learning
Random:     Simplest, least overhead
```

### TrainingConfig
Controls optimization and training schedule.

**Key Parameters**:
- `learning_rate`: Step size (1e-5 to 1e-3)
- `batch_size`: Samples per step (8-64)
- `gradient_accumulation_steps`: Simulate larger batches (1-8)
- `warmup_steps`: Linear warmup period (100-1000)
- `max_grad_norm`: Gradient clipping (0.5-5.0)

**Effective Batch Size**:
```
effective_batch = batch_size × gradient_accumulation_steps
```

## Loading Configurations

### From YAML
```python
from seci.config.config import SECIConfig

# Load from file
config = SECIConfig.from_yaml("config/default.yaml")

# Modify if needed
config.training.learning_rate = 5e-5
config.model.use_lora = True

# Save modified config
config.to_yaml("config/my_config.yaml")
```

### Programmatic Creation
```python
from seci.config.config import (
    SECIConfig, ModelConfig, TrainingConfig
)

# Create from code
config = SECIConfig(
    model=ModelConfig(
        hidden_size=256,
        num_layers=4,
        use_lora=True
    ),
    training=TrainingConfig(
        batch_size=32,
        learning_rate=1e-4
    )
)
```

### Environment-Based Overrides
```python
import os

config = SECIConfig.from_yaml("config/default.yaml")

# Override with environment variables
if os.getenv("SECI_DEVICE"):
    config.device = os.getenv("SECI_DEVICE")
if os.getenv("SECI_BATCH_SIZE"):
    config.training.batch_size = int(os.getenv("SECI_BATCH_SIZE"))
```

## Configuration Best Practices

### 1. Start with Default
Begin with `config/default.yaml` and modify only what's needed:
```python
config = SECIConfig.from_yaml("config/default.yaml")
config.training.learning_rate = 5e-5  # Fine-tune LR
```

### 2. Match Memory and Model Dimensions
```python
# Memory embedding_dim MUST equal model hidden_size
config.memory.embedding_dim = config.model.hidden_size
```

### 3. Scale Together
When reducing model size, reduce other components proportionally:
```python
# Small model setup
config.model.hidden_size = 128
config.model.num_layers = 2
config.memory.memory_size = 500        # Smaller memory
config.replay.buffer_size = 5000       # Smaller buffer
config.training.batch_size = 16        # Smaller batches
```

### 4. Adjust for Compute Budget

**GPU with 8GB+ VRAM**:
```yaml
model:
  hidden_size: 256
  num_layers: 4
  use_quantization: false
training:
  batch_size: 32
```

**GPU with 4-8GB VRAM**:
```yaml
model:
  hidden_size: 256
  num_layers: 4
  use_quantization: true
  quantization_bits: 8
training:
  batch_size: 16
```

**CPU or <4GB GPU**:
```yaml
model:
  hidden_size: 128
  num_layers: 2
  use_quantization: true
  use_lora: true
training:
  batch_size: 8
  gradient_accumulation_steps: 4
```

### 5. Tune Distillation
Start with balanced distillation and adjust based on results:
```python
# More teacher influence
config.distillation.alpha = 0.7
config.distillation.temperature = 3.0

# More task focus
config.distillation.alpha = 0.3
config.distillation.temperature = 1.5
```

## Configuration Validation

The system performs basic validation:
- Type checking via dataclasses
- Range checking for critical parameters
- Dimension matching warnings

```python
# This will warn if dimensions don't match
config = SECIConfig()
config.memory.embedding_dim = 512  # Different from model.hidden_size
# Warning: Memory embedding_dim should match model.hidden_size
```

## Example Configurations

### Research Experiment
```yaml
model:
  hidden_size: 512
  num_layers: 6
  use_lora: true
  lora_r: 16

training:
  learning_rate: 3e-4
  batch_size: 64
  max_steps: 50000

distillation:
  temperature: 2.5
  alpha: 0.6
```

### Production Inference
```yaml
model:
  hidden_size: 256
  num_layers: 4
  use_quantization: true
  quantization_bits: 8
  use_lora: false

memory:
  memory_size: 2000
  retrieval_top_k: 3
```

### Continual Learning Focus
```yaml
replay:
  buffer_size: 20000
  replay_frequency: 3
  sampling_strategy: priority
  priority_alpha: 0.7

distillation:
  alpha: 0.4  # More task focus
  temperature: 2.0
```
