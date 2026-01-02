# SECI Architecture Visual Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                     SECI System Architecture                           │
│                Self-Evolving Compact Intelligence                      │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          INPUT PROCESSING                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Token IDs (batch, seq_len) → Embeddings → Position Encoding           │
└────────────────┬────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      STUDENT MODEL (Compact)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐            │
│  │ Transformer Block 1                                     │            │
│  │  • Multi-Head Attention (with optional LoRA)           │            │
│  │  • Feed-Forward Network                                │            │
│  │  • Layer Normalization                                 │            │
│  └─────────────────┬───────────────────────────────────────┘            │
│                    │                                                    │
│  ┌─────────────────▼───────────────────────────────────────┐            │
│  │ Transformer Block 2-4 (similar structure)              │            │
│  └─────────────────┬───────────────────────────────────────┘            │
│                    │                                                    │
│                    ▼                                                    │
│            Hidden States List                                          │
│            (All Layer Outputs)                                         │
└────────────────────┬───────────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────────┐
│ EXTERNAL MEMORY │    │  TEACHER MODEL       │
│                 │    │  (Larger, Frozen)    │
├─────────────────┤    ├──────────────────────┤
│ • 1000 slots    │    │ • 2x hidden size     │
│ • Key-Value     │    │ • 2x layers          │
│ • Attention     │    │ • No gradients       │
│ • Top-K         │    │ • Soft targets       │
│   retrieval     │    │ • Hidden states      │
└────────┬────────┘    └──────────┬───────────┘
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────────┐
│      KNOWLEDGE DISTILLATION                 │
├─────────────────────────────────────────────┤
│  • Compare logits (KL divergence)          │
│  • Match hidden states (MSE)               │
│  • Temperature scaling (T=2.0)             │
│  • Weighted loss (α=0.5)                   │
│                                            │
│  Loss = α*distill + (1-α)*task + β*hidden │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│          BACKWARD PASS                      │
├─────────────────────────────────────────────┤
│  • Gradient computation                    │
│  • Gradient clipping (norm=1.0)           │
│  • Parameter update (AdamW)               │
│  • Learning rate scheduling               │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│      MEMORY & REPLAY UPDATE                 │
├─────────────────────────────────────────────┤
│  Memory Update:                            │
│  • Store hidden states in memory          │
│  • LRU replacement strategy               │
│  • Momentum-based updates                 │
│                                            │
│  Replay Buffer:                            │
│  • Add experience (input, label, priority)│
│  • Reservoir sampling                     │
│  • 10K sample capacity                    │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│      EXPERIENCE REPLAY (every N steps)      │
├─────────────────────────────────────────────┤
│  • Sample batch from buffer               │
│  • Forward pass on replayed data          │
│  • Compute replay loss                    │
│  • Additional backward pass               │
│  • Prevents catastrophic forgetting       │
└─────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════
                        COMPONENT DETAILS
═══════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────┐
│ CompactTransformer (Student)                                     │
├──────────────────────────────────────────────────────────────────┤
│ Parameters: ~8M (configurable)                                   │
│ Architecture:                                                    │
│   • Vocab size: 32K tokens                                      │
│   • Hidden size: 256 (default)                                  │
│   • Layers: 4 transformer blocks                                │
│   • Heads: 4 attention heads per layer                          │
│   • FFN size: 1024                                             │
│   • Max seq len: 512 tokens                                     │
│                                                                  │
│ Efficiency Features:                                            │
│   • LoRA adapters (rank=8) → ~1% trainable params              │
│   • 8-bit quantization → 4x memory reduction                   │
│   • Gradient checkpointing support                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ ExternalMemory                                                   │
├──────────────────────────────────────────────────────────────────┤
│ Capacity: 1000 key-value pairs                                  │
│ Mechanism:                                                       │
│   • Keys: Learned representations (256-dim)                     │
│   • Values: Associated information                              │
│   • Retrieval: Cosine similarity + Top-K (K=5)                 │
│   • Update: LRU with momentum (rate=0.01)                      │
│                                                                  │
│ Operations:                                                      │
│   • Read: O(memory_size) cosine similarity                      │
│   • Write: O(1) with LRU replacement                           │
│   • Aging: Track usage and recency                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ KnowledgeDistiller                                              │
├──────────────────────────────────────────────────────────────────┤
│ Strategies:                                                      │
│   • Logit distillation: KL divergence with T=2.0               │
│   • Hidden distillation: MSE between layer outputs             │
│   • Attention transfer: Match attention patterns (optional)    │
│                                                                  │
│ Loss Computation:                                               │
│   total_loss = α * distill_loss + (1-α) * task_loss           │
│              + β * hidden_loss                                 │
│                                                                  │
│ Parameters:                                                      │
│   • Temperature (T): 2.0 (default)                             │
│   • Alpha (α): 0.5 (distillation weight)                       │
│   • Beta (β): 0.1 (hidden loss weight)                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ ReplayBuffer                                                     │
├──────────────────────────────────────────────────────────────────┤
│ Capacity: 10,000 experiences                                    │
│ Storage: (input_ids, attention_mask, labels, priority)          │
│                                                                  │
│ Sampling Strategies:                                            │
│   1. Reservoir: Uniform over time                              │
│   2. Priority: Focus on high-loss samples (α=0.6)              │
│   3. Random: Simple uniform sampling                           │
│                                                                  │
│ Replay Schedule:                                                │
│   • Frequency: Every 5 steps (configurable)                    │
│   • Batch size: 32 samples                                     │
│   • Purpose: Prevent catastrophic forgetting                   │
└──────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════
                      TRAINING WORKFLOW
═══════════════════════════════════════════════════════════════════

Step 1: Initialization
  ├─ Load configuration (YAML)
  ├─ Initialize student model
  ├─ Initialize teacher model (frozen)
  ├─ Create memory bank
  ├─ Setup distillation
  ├─ Create replay buffer
  └─ Initialize optimizer & scheduler

Step 2: Training Loop (for each batch)
  ├─ Forward: Student processes input
  ├─ Memory: Query and retrieve relevant memories
  ├─ Forward: Teacher processes input (no grad)
  ├─ Distill: Compute combined loss
  ├─ Backward: Update student parameters
  ├─ Memory Update: Store current hidden states
  ├─ Replay Add: Store experience in buffer
  └─ Replay Step: Train on past experiences (periodic)

Step 3: Periodic Operations
  ├─ Logging (every 100 steps)
  │   ├─ Training loss
  │   ├─ Memory utilization
  │   └─ Buffer statistics
  ├─ Evaluation (every 500 steps)
  │   ├─ Validation loss
  │   └─ Performance metrics
  └─ Checkpointing (every 1000 steps)
      ├─ Model state
      ├─ Memory state
      └─ Buffer state


═══════════════════════════════════════════════════════════════════
                    EFFICIENCY FEATURES
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│ Parameter Efficiency                                        │
├─────────────────────────────────────────────────────────────┤
│ Base Model:        8M parameters (100%)                    │
│ With LoRA (r=8):   ~80K trainable (1%)                     │
│ Frozen Base:       7.92M frozen (99%)                      │
│                                                             │
│ Benefit: Fine-tune with minimal compute                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Memory Efficiency                                           │
├─────────────────────────────────────────────────────────────┤
│ FP32 Model:        ~32MB (8M params × 4 bytes)            │
│ INT8 Model:        ~8MB (8M params × 1 byte)              │
│                                                             │
│ Reduction: 4x memory savings                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Compute Efficiency                                          │
├─────────────────────────────────────────────────────────────┤
│ • Small model: 256 hidden vs 768+ in BERT                 │
│ • Top-K memory: O(K) vs O(N) retrieval                    │
│ • Gradient accumulation: Simulate large batches           │
│ • Mixed precision: FP16 training                          │
└─────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════
                    CONFIGURATION PROFILES
═══════════════════════════════════════════════════════════════════

Profile: DEFAULT (config/default.yaml)
  Hardware: Single GPU (4GB+)
  Model: 256 hidden, 4 layers (~8M params)
  Memory: 1000 slots
  Replay: 10K buffer
  Batch: 32
  Speed: ~100 steps/sec

Profile: LOW-RESOURCE (config/low_resource.yaml)
  Hardware: CPU or small GPU (<4GB)
  Model: 128 hidden, 2 layers (~2M params)
  Memory: 500 slots
  Replay: 5K buffer
  Batch: 16
  Features: LoRA + Quantization
  Speed: ~30 steps/sec


═══════════════════════════════════════════════════════════════════
                   SUCCESS METRICS (MVP)
═══════════════════════════════════════════════════════════════════

✓ Functional: All components working
✓ Efficient: <4GB GPU memory
✓ Learning: Loss converges
✓ Memory: >50% utilization
✓ Replay: Reduces forgetting <20%
✓ Modular: Components independent
✓ Documented: Comprehensive guides


═══════════════════════════════════════════════════════════════════
                        FILE STRUCTURE
═══════════════════════════════════════════════════════════════════

seci/
  core/
    model.py         (315 lines) - CompactTransformer
    teacher.py       (115 lines) - TeacherModel
  memory/
    external_memory.py (221 lines) - ExternalMemory
  distillation/
    distiller.py     (223 lines) - KnowledgeDistiller
  replay/
    buffer.py        (255 lines) - ReplayBuffer
  config/
    config.py        (150 lines) - SECIConfig
  utils/
    helpers.py       (159 lines) - Utilities

Total: ~1,438 lines of core implementation
```
