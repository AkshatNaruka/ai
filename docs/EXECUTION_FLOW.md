# End-to-End Execution Flow

## Training Pipeline Overview

```
[Data Batch] 
    ↓
[1. Student Forward Pass] → Hidden States + Logits
    ↓
[2. Memory Read] → Retrieve relevant past knowledge
    ↓
[3. Teacher Forward Pass] → Teacher Logits + Hidden States
    ↓
[4. Knowledge Distillation] → Compute distillation loss
    ↓
[5. Memory Update] → Store current hidden states
    ↓
[6. Replay Buffer Add] → Store experience for replay
    ↓
[7. Backward Pass] → Update student parameters
    ↓
[8. Replay Step] (every N steps) → Train on past experiences
    ↓
[9. Logging & Checkpointing]
```

## Detailed Step-by-Step Flow

### 1. Initialization Phase
```python
# Load configuration
config = SECIConfig.from_yaml("config/default.yaml")

# Initialize components
student = CompactTransformer(...)          # Compact student model
teacher = TeacherModel(...)                # Larger frozen teacher
memory = ExternalMemory(...)               # External memory bank
distiller = KnowledgeDistiller(...)        # Distillation manager
replay_buffer = ReplayBuffer(...)          # Experience replay
optimizer = AdamW(student.parameters())    # Optimizer
scheduler = get_linear_schedule_with_warmup(...)
```

### 2. Training Step (Main Loop)

#### Step 2.1: Student Forward Pass
```python
# Input: (batch_size, seq_len)
input_ids, attention_mask, labels = batch

# Student processes input
student_outputs = student(
    input_ids=input_ids,
    attention_mask=attention_mask,
    return_hidden_states=True  # For distillation
)
# Output: logits (batch_size, seq_len, vocab_size)
#         hidden_states: list of (batch_size, seq_len, hidden_size)
```

#### Step 2.2: Memory Read
```python
# Query memory with student's hidden states
memory_output, attention_weights = memory.read(
    query=student_outputs['last_hidden_state']
)
# Output: retrieved memory values (batch_size, seq_len, hidden_size)
# These augment the student's representations with past knowledge
```

#### Step 2.3: Teacher Forward Pass
```python
# Teacher processes same input (no gradients)
with torch.no_grad():
    teacher_outputs = teacher(
        input_ids=input_ids,
        attention_mask=attention_mask,
        return_hidden_states=True
    )
# Output: teacher logits and hidden states for distillation
```

#### Step 2.4: Knowledge Distillation
```python
# Compute combined loss
loss_dict = distiller(
    student_outputs=student_outputs,
    teacher_outputs=teacher_outputs,
    labels=labels
)
# Output: {
#     'loss': combined weighted loss,
#     'distill_loss': KL divergence between distributions,
#     'task_loss': cross-entropy with ground truth,
#     'hidden_loss': MSE between hidden states
# }
```

**Distillation Loss Formula**:
```
total_loss = α * distillation_loss + (1-α) * task_loss + β * hidden_loss

distillation_loss = KL(softmax(student_logits/T) || softmax(teacher_logits/T)) * T²
task_loss = CrossEntropy(student_logits, labels)
hidden_loss = MSE(student_hidden_states, teacher_hidden_states)
```

#### Step 2.5: Memory Update
```python
# Store current hidden states in memory
memory.update_from_hidden_states(
    hidden_states=student_outputs['last_hidden_state'].detach()
)
# Memory uses LRU strategy to replace old entries
# Updates memory keys and values with momentum
```

#### Step 2.6: Replay Buffer Addition
```python
# Store experience for future replay
replay_buffer.add(
    input_ids=input_ids.detach(),
    attention_mask=attention_mask.detach(),
    labels=labels.detach(),
    priority=loss.item()  # Priority based on loss
)
# Uses reservoir sampling or FIFO depending on config
```

#### Step 2.7: Backward Pass
```python
# Compute gradients and update parameters
loss.backward()
torch.nn.utils.clip_grad_norm_(student.parameters(), max_norm=1.0)
optimizer.step()
scheduler.step()
optimizer.zero_grad()
```

#### Step 2.8: Experience Replay
```python
# Every N steps, replay past experiences
if step % replay_frequency == 0 and not replay_buffer.is_empty():
    # Sample batch from buffer
    replay_batch = replay_buffer.sample(batch_size=32)
    
    # Forward pass on replayed data
    replay_outputs = student(
        input_ids=replay_batch['input_ids'],
        attention_mask=replay_batch['attention_mask']
    )
    
    # Compute and backpropagate replay loss
    replay_loss = CrossEntropy(replay_outputs['logits'], replay_batch['labels'])
    replay_loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

### 3. Periodic Operations

#### Every `logging_steps` (e.g., 100 steps)
```python
# Log metrics
print(f"Step {step}: loss={loss:.4f}, distill_loss={distill_loss:.4f}")
print(f"Memory utilization: {memory.get_memory_stats()}")
print(f"Buffer utilization: {replay_buffer.get_stats()}")
```

#### Every `save_steps` (e.g., 1000 steps)
```python
# Save checkpoint
save_checkpoint(
    model=student,
    optimizer=optimizer,
    step=step,
    path=f"checkpoint_step_{step}.pt"
)
memory.save_memory(f"memory_step_{step}.pt")
replay_buffer.save(f"buffer_step_{step}.pt")
```

### 4. Self-Evolution Mechanism

The "self-evolving" aspect comes from:

1. **Continual Memory Updates**: Memory bank continuously stores new knowledge
2. **Experience Replay**: Past experiences prevent catastrophic forgetting
3. **Distillation**: Knowledge from teacher (or previous self) guides learning
4. **Adaptive Sampling**: Priority-based replay focuses on hard examples

### 5. Key Execution Parameters

| Parameter | Purpose | Typical Value |
|-----------|---------|---------------|
| `batch_size` | Training batch size | 16-32 |
| `temperature` | Distillation softness | 2.0 |
| `alpha` | Distillation vs task weight | 0.5 |
| `replay_frequency` | Steps between replay | 5 |
| `memory_update_rate` | Memory momentum | 0.01 |
| `buffer_size` | Max replay samples | 10000 |
| `retrieval_top_k` | Memory slots to retrieve | 5 |

### 6. Compute Efficiency Features

- **LoRA**: Train only low-rank adapters (~1% parameters)
- **Quantization**: 8-bit weights for 4x memory reduction
- **Compact Architecture**: Small transformer (256 hidden, 4 layers)
- **Top-K Memory**: Retrieve only relevant memories
- **Gradient Accumulation**: Simulate larger batches
