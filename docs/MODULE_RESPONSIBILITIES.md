# Module Responsibilities

## Core Modules

### seci/core/model.py - CompactTransformer
**Responsibility**: Small, efficient transformer model (student)
- Implements compact transformer architecture with pre-norm structure
- Multi-head attention with optional LoRA adapters
- Feed-forward networks with GELU activation
- Support for dynamic quantization hooks
- Returns logits and intermediate hidden states for distillation
- Configurable depth, width, and attention heads

**Key Methods**:
- `forward()`: Main forward pass with optional hidden state return
- `enable_lora()`: Enable LoRA for parameter-efficient fine-tuning
- `get_trainable_params()`: Count trainable parameters

### seci/core/teacher.py - TeacherModel
**Responsibility**: Larger frozen model for knowledge distillation
- Wraps any pre-trained model as a teacher
- Generates soft targets (probability distributions)
- Extracts intermediate hidden states for layer-wise distillation
- Always operates in eval mode (frozen)

**Key Methods**:
- `forward()`: Forward pass through teacher (no gradients)
- `get_soft_targets()`: Generate softened probability distributions
- `get_hidden_states()`: Extract all layer hidden states

## Memory Module

### seci/memory/external_memory.py - ExternalMemory
**Responsibility**: Key-value memory bank for storing learned representations
- Attention-based read operations with top-k retrieval
- Least-recently-used (LRU) write strategy
- Memory aging and usage tracking
- Cosine similarity for memory retrieval
- Supports online memory updates from hidden states

**Key Methods**:
- `read()`: Retrieve relevant memories via attention
- `write()`: Store new key-value pairs with momentum
- `update_from_hidden_states()`: Auto-update from model outputs
- `get_memory_stats()`: Memory utilization metrics

## Distillation Module

### seci/distillation/distiller.py - KnowledgeDistiller
**Responsibility**: Transfer knowledge from teacher to student
- Multiple distillation loss types (KL divergence, MSE, cosine)
- Layer-wise hidden state matching
- Temperature-scaled soft targets
- Configurable balance between distillation and task loss

**Key Methods**:
- `forward()`: Compute combined distillation + task loss
- `compute_distillation_loss()`: Logit-level distillation
- `compute_hidden_distillation_loss()`: Hidden state matching
- `set_temperature()`: Adjust distillation temperature

## Replay Module

### seci/replay/buffer.py - ReplayBuffer
**Responsibility**: Store and replay past experiences
- Multiple sampling strategies (reservoir, priority, random)
- Efficient storage of input sequences and labels
- Priority-based sampling for important examples
- Reservoir sampling for uniform distribution over time

**Key Methods**:
- `add()`: Store new experiences
- `sample()`: Retrieve batch for replay training
- `update_priorities()`: Adjust sample priorities
- `get_stats()`: Buffer utilization metrics

## Configuration Module

### seci/config/config.py - SECIConfig
**Responsibility**: Centralized configuration management
- Dataclass-based configuration with type safety
- YAML file loading and saving
- Hierarchical config structure (model, memory, distillation, replay, training)
- Default values for all hyperparameters

**Sub-Configs**:
- `ModelConfig`: Model architecture and LoRA/quantization settings
- `MemoryConfig`: External memory parameters
- `DistillationConfig`: Knowledge distillation hyperparameters
- `ReplayConfig`: Replay buffer configuration
- `TrainingConfig`: Optimizer, learning rate, and training schedule

## Utilities Module

### seci/utils/helpers.py
**Responsibility**: Common utility functions
- Random seed setting for reproducibility
- Parameter counting
- Checkpoint saving/loading
- Learning rate scheduling
- Metric formatting and logging
- AverageMeter for tracking metrics

## Training Script

### train.py - SECITrainer
**Responsibility**: Orchestrate end-to-end training
- Initialize all SECI components
- Main training loop with distillation + replay
- Periodic memory updates
- Checkpoint and logging management
- Integration of all modules

**Key Methods**:
- `train_step()`: Single training step with distillation
- `_replay_step()`: Experience replay training
- `train()`: Main training loop
- `save_checkpoint()`: Save model, memory, and buffer
