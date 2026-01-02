# Core Python Interfaces

This document outlines the core interfaces for each major component in SECI.

## 1. Memory Interface

### ExternalMemory
```python
class ExternalMemory(nn.Module):
    """External memory bank with attention-based retrieval."""
    
    def __init__(
        self,
        memory_size: int,           # Number of memory slots
        embedding_dim: int,         # Dimension of embeddings
        num_memory_heads: int = 4,  # Attention heads for retrieval
        memory_update_rate: float = 0.01,  # Write momentum
        retrieval_top_k: int = 5    # Top-K slots to retrieve
    ):
        """Initialize memory bank."""
        pass
    
    def read(
        self,
        query: torch.Tensor,        # (batch, seq_len, dim)
        return_attention: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Read from memory using attention.
        Returns: retrieved values (batch, seq_len, dim)
        """
        pass
    
    def write(
        self,
        keys: torch.Tensor,         # (batch, dim)
        values: torch.Tensor,       # (batch, dim)
        write_strength: float = 1.0
    ):
        """Write key-value pairs to memory (LRU replacement)."""
        pass
    
    def update_from_hidden_states(
        self,
        hidden_states: torch.Tensor,  # (batch, seq_len, dim)
        labels: Optional[torch.Tensor] = None
    ):
        """Automatically update memory from model hidden states."""
        pass
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Return memory utilization statistics."""
        pass
```

**Key Features**:
- Cosine similarity for retrieval
- LRU replacement strategy
- Momentum-based updates
- Memory aging tracking

---

## 2. Model Interface

### CompactTransformer
```python
class CompactTransformer(nn.Module):
    """Compact transformer with LoRA and quantization support."""
    
    def __init__(
        self,
        vocab_size: int,
        hidden_size: int,
        num_layers: int,
        num_heads: int,
        intermediate_size: int,
        max_seq_length: int,
        dropout: float = 0.1,
        use_quantization: bool = False,
        quantization_bits: int = 8,
        use_lora: bool = False,
        lora_r: int = 8,
        lora_alpha: int = 16,
        lora_dropout: float = 0.1
    ):
        """Initialize compact transformer."""
        pass
    
    def forward(
        self,
        input_ids: torch.Tensor,      # (batch, seq_len)
        attention_mask: Optional[torch.Tensor] = None,
        return_hidden_states: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass.
        Returns: {
            'logits': (batch, seq_len, vocab_size),
            'last_hidden_state': (batch, seq_len, hidden_size),
            'hidden_states': list of hidden states (if requested)
        }
        """
        pass
    
    def enable_lora(self):
        """Enable LoRA for parameter-efficient fine-tuning."""
        pass
    
    def disable_lora(self):
        """Disable LoRA and unfreeze all parameters."""
        pass
    
    def get_trainable_params(self) -> int:
        """Count trainable parameters."""
        pass
```

**Key Features**:
- Pre-norm transformer architecture
- Optional LoRA adapters on attention
- Quantization hooks
- Multi-head attention with residual connections

---

## 3. Teacher Interface

### TeacherModel
```python
class TeacherModel(nn.Module):
    """Wrapper for teacher model in knowledge distillation."""
    
    def __init__(
        self,
        model: Optional[nn.Module] = None,
        use_compact_as_teacher: bool = False,
        teacher_config: Optional[Dict] = None
    ):
        """Initialize teacher (always frozen)."""
        pass
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        return_hidden_states: bool = True
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass (no gradients).
        Returns: {
            'logits': teacher logits,
            'hidden_states': list of hidden states
        }
        """
        pass
    
    @torch.no_grad()
    def get_soft_targets(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        temperature: float = 1.0
    ) -> torch.Tensor:
        """Get softened probability distributions."""
        pass
    
    @torch.no_grad()
    def get_hidden_states(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> List[torch.Tensor]:
        """Extract hidden states from all layers."""
        pass
```

**Key Features**:
- Always operates in eval mode
- No gradient computation
- Temperature-scaled soft targets
- Compatible with any PyTorch model

---

## 4. Distillation Interface

### KnowledgeDistiller
```python
class KnowledgeDistiller(nn.Module):
    """Knowledge distillation manager."""
    
    def __init__(
        self,
        temperature: float = 2.0,
        alpha: float = 0.5,           # Distillation vs task loss weight
        distill_loss_type: str = "kl_div",  # kl_div, mse, cosine
        layer_wise_distillation: bool = True,
        hidden_distillation: bool = True
    ):
        """Initialize distiller."""
        pass
    
    def forward(
        self,
        student_outputs: Dict[str, torch.Tensor],
        teacher_outputs: Dict[str, torch.Tensor],
        labels: Optional[torch.Tensor] = None,
        task_loss_fn: Optional[callable] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Compute combined loss.
        Returns: {
            'loss': total weighted loss,
            'distill_loss': distillation component,
            'task_loss': task-specific component,
            'hidden_loss': hidden state matching
        }
        """
        pass
    
    def compute_distillation_loss(
        self,
        student_logits: torch.Tensor,
        teacher_logits: torch.Tensor
    ) -> torch.Tensor:
        """Compute logit-level distillation loss."""
        pass
    
    def compute_hidden_distillation_loss(
        self,
        student_hidden_states: List[torch.Tensor],
        teacher_hidden_states: List[torch.Tensor]
    ) -> torch.Tensor:
        """Compute hidden state matching loss."""
        pass
    
    def set_temperature(self, temperature: float):
        """Update distillation temperature."""
        pass
    
    def set_alpha(self, alpha: float):
        """Update loss weight balance."""
        pass
```

**Key Features**:
- Multiple loss types (KL, MSE, cosine)
- Temperature scaling
- Layer-wise hidden state matching
- Configurable loss weighting

---

## 5. Replay Interface

### ReplayBuffer
```python
class ReplayBuffer:
    """Experience replay buffer for continual learning."""
    
    def __init__(
        self,
        buffer_size: int,
        replay_batch_size: int = 32,
        sampling_strategy: str = "reservoir",  # reservoir, priority, random
        priority_alpha: float = 0.6
    ):
        """Initialize replay buffer."""
        pass
    
    def add(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor,
        priority: Optional[float] = None,
        metadata: Optional[Dict] = None
    ):
        """Add experiences to buffer."""
        pass
    
    def sample(
        self,
        batch_size: Optional[int] = None,
        device: str = "cpu"
    ) -> Dict[str, torch.Tensor]:
        """
        Sample batch for replay.
        Returns: {
            'input_ids': sampled inputs,
            'attention_mask': sampled masks,
            'labels': sampled labels,
            'indices': sample indices
        }
        """
        pass
    
    def update_priorities(
        self,
        indices: List[int],
        priorities: List[float]
    ):
        """Update priorities for specific samples."""
        pass
    
    def get_stats(self) -> Dict[str, any]:
        """Return buffer statistics."""
        pass
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        pass
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        pass
```

**Key Features**:
- Multiple sampling strategies
- Reservoir sampling for uniform distribution
- Priority-based sampling for hard examples
- Efficient CPU storage

---

## Usage Example

```python
# Initialize components
config = SECIConfig()

student = CompactTransformer(
    vocab_size=config.model.vocab_size,
    hidden_size=config.model.hidden_size,
    num_layers=config.model.num_layers,
    num_heads=config.model.num_heads,
    intermediate_size=config.model.intermediate_size,
    max_seq_length=config.model.max_seq_length,
    use_lora=config.model.use_lora
)

teacher = TeacherModel(model=larger_model)

memory = ExternalMemory(
    memory_size=config.memory.memory_size,
    embedding_dim=config.model.hidden_size,
    num_memory_heads=config.memory.num_memory_heads
)

distiller = KnowledgeDistiller(
    temperature=config.distillation.temperature,
    alpha=config.distillation.alpha
)

replay_buffer = ReplayBuffer(
    buffer_size=config.replay.buffer_size,
    sampling_strategy=config.replay.sampling_strategy
)

# Training step
student_outputs = student(input_ids, attention_mask, return_hidden_states=True)
teacher_outputs = teacher(input_ids, attention_mask)
memory_output, _ = memory.read(student_outputs['last_hidden_state'])

loss_dict = distiller(student_outputs, teacher_outputs, labels)
loss_dict['loss'].backward()

memory.update_from_hidden_states(student_outputs['last_hidden_state'])
replay_buffer.add(input_ids, attention_mask, labels)
```
