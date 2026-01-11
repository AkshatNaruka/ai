# SECI Architecture Guide

This document explains the SECI system architecture in detail, suitable for developers who want to understand how the system works.

## Table of Contents
- [High-Level Overview](#high-level-overview)
- [System Architecture](#system-architecture)
- [Core AI Components](#core-ai-components)
- [Search System Architecture](#search-system-architecture)
- [Data Flow](#data-flow)
- [Component Interactions](#component-interactions)
- [Design Decisions](#design-decisions)
- [Performance Considerations](#performance-considerations)

## High-Level Overview

SECI is a **modular AI system** combining:
1. **Continual Learning AI**: A compact transformer that learns without forgetting
2. **Web Search & Scraping**: Multi-provider search with intelligent content extraction
3. **Natural Language Interface**: CLI and API for easy interaction

### Architecture Philosophy

**Three Core Principles:**
1. **Modularity**: Each component has a single, well-defined responsibility
2. **Efficiency**: Designed to run on resource-constrained devices
3. **Extensibility**: Easy to add new features and providers

## System Architecture

### Overall System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         SECI System                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────────────────────┐    │
│  │              │         │     AI Core System           │     │
│  │   User       │────────▶│                              │     │
│  │  Interface   │         │  ┌────────────────────────┐  │     │
│  │              │         │  │  Compact Transformer   │  │     │
│  │ • CLI        │         │  │  (Student Model)       │  │     │
│  │ • API        │         │  └──────────┬─────────────┘  │     │
│  │ • Interactive│         │             │                 │     │
│  └──────────────┘         │  ┌──────────▼─────────────┐  │     │
│                           │  │  External Memory       │  │     │
│                           │  │  (Knowledge Bank)      │  │     │
│                           │  └──────────┬─────────────┘  │     │
│                           │             │                 │     │
│                           │  ┌──────────▼─────────────┐  │     │
│                           │  │  Teacher Model         │  │     │
│                           │  │  (Distillation)        │  │     │
│                           │  └────────────────────────┘  │     │
│                           │                              │     │
│                           │  ┌────────────────────────┐  │     │
│                           │  │  Replay Buffer         │  │     │
│                           │  │  (Experience Storage)  │  │     │
│                           │  └────────────────────────┘  │     │
│                           └──────────────────────────────┘     │
│                                                                  │
│  ┌───────────────────────────────────────────────────────┐    │
│  │             Search & Web System                        │     │
│  │                                                        │     │
│  │  ┌──────────────┐    ┌──────────────┐               │     │
│  │  │ Search       │───▶│ Web Scraper  │               │     │
│  │  │ Engine       │    │              │               │     │
│  │  │              │    └──────────────┘               │     │
│  │  │ • DuckDuckGo │                                    │     │
│  │  │ • Google     │    ┌──────────────┐               │     │
│  │  │ • Bing       │───▶│ Content      │               │     │
│  │  └──────────────┘    │ Extractor    │               │     │
│  │                      └──────────────┘               │     │
│  │                                                        │     │
│  │  ┌──────────────────────────────────────────┐       │     │
│  │  │        Query Processor                    │       │     │
│  │  │  • Query Enhancement                      │       │     │
│  │  │  • Result Ranking                         │       │     │
│  │  │  • Context Management                     │       │     │
│  │  │  • Response Generation                    │       │     │
│  │  └──────────────────────────────────────────┘       │     │
│  └───────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Core AI Components

### 1. Compact Transformer (Student Model)

**Purpose**: The main AI brain - a small, efficient neural network

**Architecture:**
```
Input Tokens (text)
    ↓
[Embedding Layer] → Convert tokens to vectors
    ↓
[Transformer Block 1]
    ├─ Multi-Head Attention → Focus on relevant parts
    ├─ Feed Forward Network → Process information
    └─ Layer Normalization → Stabilize learning
    ↓
[Transformer Block 2]
    ↓
[Transformer Block 3]
    ↓
[Transformer Block 4]
    ↓
[Output Layer] → Predict next token
```

**Key Characteristics:**
- **Size**: ~8M parameters (default), ~2M (minimal)
- **Hidden Size**: 256 dimensions (default), 128 (minimal)
- **Layers**: 4 layers (default), 2 (minimal)
- **Attention Heads**: 4 heads
- **Context Length**: Up to 512 tokens

**Code Location**: `seci/core/model.py`

**Design Decisions:**
- **Why so small?** To run on any device, even Raspberry Pi
- **Pre-norm architecture**: Better training stability
- **LoRA support**: Fine-tune with <1% parameters
- **Quantization**: Reduce memory usage by 50%

### 2. External Memory

**Purpose**: Long-term knowledge storage and retrieval

**How It Works:**
```
1. Store Important Information
   Hidden States → [Memory Keys]
   Content → [Memory Values]

2. Retrieve Relevant Knowledge
   Query → Attention Mechanism → Top-K Most Relevant
   
3. Update Strategy
   New Important Info → Replace Least Recently Used
```

**Memory Structure:**
```python
Memory = {
    'keys': Tensor[1000, 256],     # 1000 memory slots
    'values': Tensor[1000, 256],   # 256-dim vectors
    'usage_count': int[1000],      # Access tracking
    'last_access': int[1000]       # Recency tracking
}
```

**Key Features:**
- **Capacity**: 1000 slots by default
- **Retrieval**: Attention-based, top-5 most relevant
- **Update**: Momentum-based writing with LRU eviction
- **Persistence**: Can save/load from disk

**Code Location**: `seci/memory/external_memory.py`

### 3. Knowledge Distillation System

**Purpose**: Transfer knowledge from a large "teacher" model to our compact "student"

**Process:**
```
1. Teacher Processes Input
   Input → Large Model → Soft Predictions

2. Student Processes Same Input
   Input → Compact Model → Student Predictions

3. Learning
   Compare teacher vs student → Adjust student to match teacher
   Also learn from correct answers
```

**Loss Function:**
```python
Total Loss = α × Distillation Loss + (1-α) × Task Loss

Distillation Loss = KL_Divergence(Student_Probs, Teacher_Probs)
Task Loss = CrossEntropy(Student_Probs, True_Labels)

α = 0.5 (balance parameter)
```

**Why Distillation?**
- Student learns from teacher's "understanding" not just answers
- Softer probability distributions contain more information
- Faster convergence than training from scratch

**Code Location**: `seci/distillation/distiller.py`

### 4. Experience Replay Buffer

**Purpose**: Store and replay past experiences to prevent catastrophic forgetting

**Buffer Structure:**
```python
Buffer = {
    'input_ids': List[Tensor],      # Past inputs
    'attention_mask': List[Tensor], # Masks
    'labels': List[Tensor],         # Targets
    'priorities': List[float]       # Importance scores
}
```

**Sampling Strategies:**

1. **Reservoir Sampling** (Default)
   - Uniform probability over all time
   - Fair representation of all experiences

2. **Priority Sampling**
   - Focus on hard examples
   - Higher loss → Higher priority

3. **Random Sampling**
   - Simple uniform random selection

**Code Location**: `seci/replay/buffer.py`

## Search System Architecture

### Search Engine

**Multi-Provider Architecture:**
```
Query
  ↓
[Query Enhancer] → Improve query quality
  ↓
[Provider Manager]
  ├──▶ DuckDuckGo Provider
  ├──▶ Google Provider (optional)
  └──▶ Bing Provider (optional)
  ↓
[Result Aggregator] → Combine results
  ↓
[Result Ranker] → Score and sort
  ↓
Ranked Results
```

**Provider Interface:**
```python
class SearchProvider:
    def search(query: str, num_results: int) -> List[SearchResult]
    
SearchResult = {
    'title': str,
    'url': str,
    'snippet': str,
    'source': str
}
```

**Code Location**: `seci/search/`

### Web Scraper

**Content Extraction Pipeline:**
```
URL
  ↓
[HTTP Request] → Fetch HTML
  ↓
[HTML Parser] → BeautifulSoup parsing
  ↓
[Content Extractor] → Trafilatura extraction
  ├─ Remove ads, navigation, footers
  ├─ Extract main content
  └─ Convert to clean text
  ↓
[Metadata Extractor] → Title, author, date
  ↓
Clean Content + Metadata
```

**Features:**
- **Smart Extraction**: Multiple extraction methods with fallback
- **Error Handling**: Graceful failure on problematic URLs
- **Timeouts**: Configurable request timeouts
- **Content Limits**: Prevent memory issues with huge pages

**Code Location**: `seci/scraper/`

### Query Processor

**The Orchestrator** - Combines all components:

```
User Query
  ↓
[1. Query Enhancement]
  ├─ Expand query
  ├─ Generate variations
  └─ Extract keywords
  ↓
[2. Parallel Search]
  ├─ Search Provider 1 (async)
  ├─ Search Provider 2 (async)
  └─ Search Provider 3 (async)
  ↓
[3. Result Ranking]
  ├─ Score by relevance
  ├─ Score by credibility
  └─ Filter low-quality
  ↓
[4. Content Scraping]
  ├─ Scrape top N URLs (parallel)
  └─ Extract main content
  ↓
[5. Response Generation]
  ├─ Synthesize information
  ├─ Add citations
  └─ Format response
  ↓
[6. Context Update]
  └─ Store in conversation history
  ↓
Final Response with Citations
```

**Code Location**: `seci/query_processor.py`, `seci/enhanced_processor.py`

## Data Flow

### Training Flow

```
Step 1: Data Batch Arrives
  input_ids: [batch_size, seq_len]
  labels: [batch_size, seq_len]

Step 2: Student Forward Pass
  student(input_ids) → logits, hidden_states

Step 3: Memory Retrieval
  memory.read(hidden_states) → relevant_memories

Step 4: Teacher Forward Pass
  teacher(input_ids) → teacher_logits, teacher_hidden

Step 5: Loss Computation
  distill_loss = KL(student_logits, teacher_logits)
  task_loss = CrossEntropy(student_logits, labels)
  total_loss = α × distill_loss + (1-α) × task_loss

Step 6: Backpropagation
  total_loss.backward()
  optimizer.step()

Step 7: Memory Update
  memory.update(hidden_states)

Step 8: Buffer Update
  buffer.add(input_ids, labels, priority=loss)

Step 9: Periodic Replay (every N steps)
  replay_batch = buffer.sample()
  Train on replay_batch (steps 2-6)
```

### Query Processing Flow

```
Step 1: User Query
  "What is machine learning?"

Step 2: Query Enhancement
  Original: "What is machine learning?"
  Enhanced: ["What is machine learning?",
             "machine learning definition",
             "ML explained",
             "machine learning basics"]

Step 3: Parallel Search
  DuckDuckGo → 10 results (0.5s)
  Google → 10 results (0.6s)
  Total: ~20 results in 0.6s (parallel)

Step 4: Result Ranking
  Score each result:
  - Keyword match: 0.3
  - Title relevance: 0.25
  - Snippet quality: 0.25
  - Source credibility: 0.2
  Sort by total score

Step 5: Content Scraping
  Top 3 URLs → Scrape in parallel
  Extract: title, content, metadata

Step 6: Response Generation
  Combine information from sources
  Generate coherent answer
  Add numbered citations

Step 7: Context Storage
  Store query + response in session
  Enable follow-up questions
```

## Component Interactions

### Interaction Diagram

```
┌─────────────┐
│   Jarvis    │ (User Interface)
│     CLI     │
└──────┬──────┘
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌─────────────┐      ┌─────────────────┐
│   Query     │      │   Training      │
│  Processor  │      │   Pipeline      │
└──────┬──────┘      └────────┬────────┘
       │                      │
       │                      ▼
       │              ┌───────────────┐
       │              │    Student    │
       │              │   Model       │
       │              └───────┬───────┘
       │                      │
       ▼                      ▼
┌─────────────┐      ┌───────────────┐
│   Search    │      │   External    │
│   Engine    │      │   Memory      │
└──────┬──────┘      └───────────────┘
       │
       ▼
┌─────────────┐      ┌───────────────┐
│    Web      │      │    Replay     │
│  Scraper    │      │    Buffer     │
└─────────────┘      └───────────────┘
```

### Communication Patterns

**1. Request-Response** (CLI ↔ Query Processor)
```python
query = "What is AI?"
result = query_processor.process(query)
print(result.response)
```

**2. Pipeline** (Training Flow)
```python
for batch in dataloader:
    outputs = student(batch)
    memories = memory.read(outputs)
    teacher_outputs = teacher(batch)
    loss = distiller(outputs, teacher_outputs)
    loss.backward()
```

**3. Publish-Subscribe** (Memory Updates)
```python
# Memory subscribes to hidden states
model.register_hook(lambda states: memory.update(states))
```

## Design Decisions

### Why These Choices?

#### 1. Compact Architecture
**Decision**: Small model (~8M params) instead of billions

**Reasoning**:
- ✅ Runs on any device (even mobile)
- ✅ Fast inference (<100ms)
- ✅ Privacy-focused (runs locally)
- ❌ Trade-off: Less capable than GPT-4

**Use Case Fit**: Personal assistant, not production LLM

#### 2. External Memory
**Decision**: Separate memory module instead of in-model

**Reasoning**:
- ✅ Larger capacity without increasing model size
- ✅ Can update memory without retraining
- ✅ Explicit control over what to remember
- ❌ Trade-off: Extra component to manage

**Alternative Considered**: Increase model size → Rejected (too resource-intensive)

#### 3. Multi-Provider Search
**Decision**: Support multiple search providers

**Reasoning**:
- ✅ No single point of failure
- ✅ Can compare/aggregate results
- ✅ Work around rate limits
- ❌ Trade-off: More complex code

**Alternative Considered**: Single provider → Rejected (less reliable)

#### 4. Modular Design
**Decision**: Separate components with clean interfaces

**Reasoning**:
- ✅ Easy to test each component
- ✅ Can swap implementations
- ✅ Easier to understand
- ❌ Trade-off: More files to navigate

**Alternative Considered**: Monolithic design → Rejected (hard to maintain)

## Performance Considerations

### Computational Efficiency

**Model Size vs Speed Trade-offs:**

| Configuration | Parameters | Inference Time | Memory Usage | Use Case |
|--------------|-----------|----------------|--------------|----------|
| Minimal | ~2M | 20-30ms | <512MB | IoT, Mobile |
| Default | ~8M | 50-100ms | <2GB | Laptops, Desktops |
| Large (Teacher) | ~30M | 200-500ms | <4GB | Training Only |

### Memory Efficiency

**Memory Footprint:**
```
Model Weights: 32MB (8M params × 4 bytes)
External Memory: 1MB (1000 × 256 × 4 bytes)
Replay Buffer: ~100MB (10K samples)
Runtime Overhead: ~500MB
Total: ~650MB
```

**Optimization Techniques:**
1. **Quantization**: 8-bit weights → 50% memory reduction
2. **Gradient Checkpointing**: Trade compute for memory
3. **Efficient Attention**: Reduced memory complexity

### Search Performance

**Latency Breakdown:**
```
Query Enhancement: ~10ms
Parallel Search: ~500-1000ms (network bound)
Result Ranking: ~5ms
Content Scraping: ~1-2s per page (network bound)
Response Generation: ~50ms

Total: 2-4 seconds typical
```

**Optimizations:**
1. **Async Search**: 2-3x faster than sequential
2. **Caching**: 95%+ hit rate on repeated queries
3. **Connection Pooling**: Reuse HTTP connections

### Scalability

**Current Limitations:**
- Single process (no distributed training)
- In-memory storage (no database)
- Local-only (no cloud sync)

**Scaling Path** (see [ROADMAP.md](ROADMAP.md)):
1. Add distributed training support
2. Add persistent storage (SQLite/PostgreSQL)
3. Add cloud synchronization option
4. Add multi-user support

## File Structure

```
seci/
├── core/
│   ├── model.py          # Compact Transformer
│   └── teacher.py        # Teacher Model
├── memory/
│   └── external_memory.py # External Memory
├── distillation/
│   └── distiller.py      # Knowledge Distillation
├── replay/
│   └── buffer.py         # Experience Replay
├── search/
│   ├── search_engine.py  # Search Engine
│   ├── providers.py      # Search Providers
│   └── async_search.py   # Async Search
├── scraper/
│   ├── scraper.py        # Web Scraper
│   └── content_extractor.py # Content Extraction
├── utils/
│   ├── query_enhancer.py # Query Enhancement
│   ├── result_ranker.py  # Result Ranking
│   └── intelligent_cache.py # Caching
├── query_processor.py    # Query Orchestrator
├── enhanced_processor.py # Enhanced Version
└── config/
    └── config.py         # Configuration
```

## Next Steps

- **For Implementation Details**: See [MODULE_RESPONSIBILITIES.md](MODULE_RESPONSIBILITIES.md)
- **For Data Flow**: See [EXECUTION_FLOW.md](EXECUTION_FLOW.md)
- **For API Reference**: See [API_REFERENCE.md](API_REFERENCE.md)
- **For Development**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

---

**Questions?** Check the [FAQ](FAQ.md) or ask on GitHub Discussions.
