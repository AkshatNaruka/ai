# SECI System Workflow

This document explains how SECI works from the user's perspective, covering all major workflows in the system.

## Table of Contents
- [User Workflows](#user-workflows)
- [CLI Workflow](#cli-workflow)
- [API Workflow](#api-workflow)
- [Training Workflow](#training-workflow)
- [Search Workflow](#search-workflow)
- [Complete Example Scenarios](#complete-example-scenarios)

## User Workflows

SECI supports three main user workflows:
1. **Interactive Chat**: Natural conversation with the AI
2. **Command-Line Queries**: Quick one-off questions
3. **API Integration**: Programmatic access for applications

## CLI Workflow

### 1. Interactive Mode Workflow

**Step-by-Step Process:**

```
┌─────────────────────────────────────────────┐
│ Step 1: User Starts Interactive Mode        │
└─────────────────┬───────────────────────────┘
                  │
                  │ $ python jarvis.py --interactive
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Step 2: System Initialization               │
│  • Load configuration                       │
│  • Initialize search engine                 │
│  • Initialize AI components                 │
│  • Create conversation session              │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Step 3: Display Welcome & Prompt            │
│  JARVIS: Hello! I'm ready to help.         │
│  You: _                                     │
└─────────────────┬───────────────────────────┘
                  │
                  │ User types: ask What is AI?
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Step 4: Parse User Input                    │
│  • Detect command type (ask/search/help)    │
│  • Extract query text                       │
│  • Validate input                           │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Step 5: Process Query                       │
│  [Details in Search Workflow section]       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Step 6: Display Response                    │
│  JARVIS: [Detailed answer with citations]  │
│  [1] Source 1                               │
│  [2] Source 2                               │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Step 7: Wait for Next Input                 │
│  You: _                                     │
│  (Continues conversation with context)      │
└─────────────────────────────────────────────┘
```

**Example Session:**

```bash
$ python jarvis.py --interactive

╔═══════════════════════════════════════════╗
║     JARVIS - SECI AI Assistant v0.1.0     ║
╚═══════════════════════════════════════════╝

Available commands:
  ask <question>    - Ask a question
  search <query>    - Search the web
  help             - Show this message
  status           - Show system status
  exit             - Exit the program

JARVIS: Hello! I'm ready to help. What would you like to know?

You: ask What is machine learning?

JARVIS: Searching and analyzing information...

Machine learning is a subset of artificial intelligence (AI) that 
enables systems to learn and improve from experience without being 
explicitly programmed. It focuses on developing computer programs 
that can access data and use it to learn for themselves.

Key concepts:
1. Algorithms learn patterns from data
2. Performance improves with more data
3. Three main types: supervised, unsupervised, reinforcement learning

Sources:
[1] Machine Learning - Wikipedia
    https://en.wikipedia.org/wiki/Machine_learning
[2] What is Machine Learning? - IBM
    https://www.ibm.com/cloud/learn/machine-learning

You: search latest Python tutorials

JARVIS: Searching the web...

Top Results:
1. Python Tutorial - W3Schools
   https://www.w3schools.com/python/
   Complete Python tutorial with examples...

2. Learn Python - Python.org
   https://docs.python.org/3/tutorial/
   Official Python tutorial...

[... more results ...]

You: exit

JARVIS: Goodbye! Have a great day!
```

### 2. Command-Line Mode Workflow

**Quick Questions Without Conversation:**

```
User Command
    ↓
$ python jarvis.py ask "What is quantum computing?"
    ↓
┌─────────────────────────────────────┐
│  Parse Command                      │
│   • Command: ask                    │
│   • Query: "What is quantum..."     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Process Query                      │
│   [Search + AI Processing]          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Display Result                     │
│   • Print response                  │
│   • Print citations                 │
│   • Exit                            │
└─────────────────────────────────────┘
    ↓
[Response displayed]
[Program exits]
```

**Example Usage:**

```bash
# Ask a question
$ python jarvis.py ask "Explain neural networks in simple terms"
[Response with citations]

# Search the web
$ python jarvis.py search "best Python libraries 2024"
[Search results displayed]

# Check status
$ python jarvis.py status
✓ SECI is installed and ready
✓ Python 3.10.5
✓ PyTorch 2.0.1
✓ All dependencies installed
✓ Search engine: DuckDuckGo (active)
```

## API Workflow

### REST API Request Flow

```
Client Application
    ↓
POST /search
{
  "query": "What is AI?",
  "session_id": "user-123",
  "max_results": 5
}
    ↓
┌─────────────────────────────────────┐
│ Step 1: API Endpoint Handler        │
│  • Validate request                 │
│  • Extract parameters               │
│  • Create/load session              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Step 2: Query Processor             │
│  • Enhance query                    │
│  • Search web                       │
│  • Scrape content                   │
│  • Generate response                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Step 3: Format Response             │
│  • Create JSON response             │
│  • Add metadata                     │
│  • Include citations                │
└──────────────┬──────────────────────┘
               │
               ▼
{
  "response": "AI is...",
  "citations": [...],
  "session_id": "user-123",
  "query_time": 2.34
}
    ↓
Client Application
```

**Example API Usage:**

```python
import requests

# Start API server first: python api.py

# Make a search request
response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "What is machine learning?",
        "session_id": "my-session",
        "max_results": 5,
        "scrape_content": True
    }
)

result = response.json()
print(result['response'])
print(f"Sources: {len(result['citations'])}")

# Get conversation history
history = requests.get(
    "http://localhost:8000/conversation/my-session"
)
print(history.json())

# Continue conversation with context
response2 = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "Tell me more about neural networks",
        "session_id": "my-session"  # Same session = maintains context
    }
)
```

## Training Workflow

### Complete Training Pipeline

```
┌──────────────────────────────────────────┐
│ Step 1: Setup                            │
│  • Load configuration from YAML          │
│  • Set random seeds                      │
│  • Initialize device (CPU/GPU)           │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 2: Initialize Components            │
│  • Student model (compact transformer)   │
│  • Teacher model (frozen)                │
│  • External memory                       │
│  • Replay buffer                         │
│  • Knowledge distiller                   │
│  • Optimizer & scheduler                 │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 3: Training Loop                    │
│  FOR each epoch:                         │
│    FOR each batch:                       │
│      ├─ Forward pass (student)           │
│      ├─ Memory retrieval                 │
│      ├─ Forward pass (teacher)           │
│      ├─ Compute distillation loss        │
│      ├─ Backward pass                    │
│      ├─ Update weights                   │
│      ├─ Update memory                    │
│      ├─ Add to replay buffer             │
│      └─ Periodic replay training         │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 4: Checkpointing                    │
│  Every N steps:                          │
│  • Save model weights                    │
│  • Save memory state                     │
│  • Save buffer state                     │
│  • Save optimizer state                  │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 5: Validation (Optional)            │
│  • Evaluate on validation set            │
│  • Compute metrics                       │
│  • Log results                           │
└──────────────────────────────────────────┘
```

**Example Training Script:**

```bash
# Basic training
python train.py \
  --config config/default.yaml \
  --output_dir ./outputs \
  --num_epochs 3

# Low-resource training
python train.py \
  --config config/low_resource.yaml \
  --output_dir ./outputs \
  --num_epochs 5

# With custom settings
python train.py \
  --config config/default.yaml \
  --learning_rate 5e-5 \
  --batch_size 16 \
  --save_steps 1000
```

**Detailed Training Step:**

```python
# Pseudocode for one training step
def training_step(batch):
    # 1. Student forward pass
    student_outputs = student(batch.input_ids)
    # Output: logits [batch, seq_len, vocab_size]
    #         hidden_states [num_layers, batch, seq_len, hidden]
    
    # 2. Memory retrieval
    memory_output = memory.read(student_outputs.hidden_states[-1])
    # Retrieve relevant past knowledge
    
    # 3. Teacher forward pass (no gradients)
    with torch.no_grad():
        teacher_outputs = teacher(batch.input_ids)
    
    # 4. Compute distillation loss
    loss_dict = distiller(
        student_outputs=student_outputs,
        teacher_outputs=teacher_outputs,
        labels=batch.labels
    )
    total_loss = loss_dict['loss']
    
    # 5. Backward pass
    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()
    scheduler.step()
    
    # 6. Update memory with new hidden states
    memory.update_from_hidden_states(
        student_outputs.hidden_states[-1]
    )
    
    # 7. Add experience to replay buffer
    replay_buffer.add(
        input_ids=batch.input_ids,
        attention_mask=batch.attention_mask,
        labels=batch.labels,
        priority=total_loss.item()
    )
    
    # 8. Periodic replay (every 10 steps)
    if step % 10 == 0:
        replay_batch = replay_buffer.sample(batch_size=32)
        # Train on replay batch (steps 1-5)
    
    return loss_dict
```

## Search Workflow

### Complete Search & Response Generation

```
User Query: "What is machine learning?"
    ↓
┌──────────────────────────────────────────┐
│ Step 1: Query Enhancement               │
│                                          │
│ Input: "What is machine learning?"      │
│ Output:                                  │
│  • "What is machine learning?"          │
│  • "machine learning definition"        │
│  • "ML explained"                        │
│  • "machine learning basics"            │
│                                          │
│ Keywords: [machine, learning, ML]       │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 2: Parallel Multi-Provider Search   │
│                                          │
│ ┌─────────────────┐                     │
│ │ DuckDuckGo      │───┐                 │
│ │ Searching...    │   │                 │
│ └─────────────────┘   │                 │
│                       ├─→ Async Wait    │
│ ┌─────────────────┐   │                 │
│ │ Google          │───┘                 │
│ │ Searching...    │                     │
│ └─────────────────┘                     │
│                                          │
│ Results: ~20 search results (0.5-1s)    │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 3: Result Aggregation & Ranking     │
│                                          │
│ For each result:                         │
│  • Calculate relevance score             │
│    - Keyword match (30%)                 │
│    - Title relevance (25%)               │
│    - Snippet quality (25%)               │
│    - Source credibility (20%)            │
│  • Filter low-quality results            │
│  • Remove duplicates                     │
│  • Sort by total score                   │
│                                          │
│ Top 10 results selected                  │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 4: Content Scraping (Top 3 URLs)    │
│                                          │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐│
│ │ URL 1    │  │ URL 2    │  │ URL 3    ││
│ │ Scraping │  │ Scraping │  │ Scraping ││
│ └────┬─────┘  └────┬─────┘  └────┬─────┘│
│      │             │             │       │
│      └─────────────┴─────────────┘       │
│                    │                     │
│         Extract main content             │
│         Remove ads/navigation            │
│         Get metadata                     │
│                                          │
│ 3 pages of clean content (~2-3s)         │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 5: Response Generation              │
│                                          │
│ Inputs:                                  │
│  • Original query                        │
│  • Search results                        │
│  • Scraped content                       │
│  • Conversation context (if any)         │
│                                          │
│ Process:                                 │
│  • Identify key information              │
│  • Synthesize from multiple sources      │
│  • Structure response logically          │
│  • Add citations                         │
│  • Format for readability                │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Step 6: Context Management               │
│                                          │
│ Store in conversation:                   │
│  • User query                            │
│  • Generated response                    │
│  • Timestamp                             │
│  • Citations used                        │
│                                          │
│ Enable follow-up questions               │
└─────────────┬────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ Final Response                           │
│                                          │
│ Machine learning is a subset of AI...   │
│ [Detailed explanation]                   │
│                                          │
│ Citations:                               │
│ [1] Machine Learning - Wikipedia         │
│ [2] What is ML? - IBM                    │
│ [3] ML Basics - MIT                      │
└──────────────────────────────────────────┘
```

### Caching Workflow

**Smart Cache Lookup:**

```
Query: "What is AI?"
    ↓
┌──────────────────────────────────────────┐
│ Check Cache                              │
│  • Normalize query: lowercase, trim      │
│  • Check for exact match                 │
│  • Check for similar queries             │
└─────────────┬────────────────────────────┘
              │
        ┌─────┴─────┐
        │           │
    Cache HIT   Cache MISS
        │           │
        ▼           ▼
┌──────────┐   ┌──────────┐
│ Return   │   │ Execute  │
│ Cached   │   │ Search   │
│ Result   │   │ Workflow │
│ (Fast)   │   └────┬─────┘
└──────────┘        │
                    ▼
              ┌──────────┐
              │ Store in │
              │ Cache    │
              └──────────┘
```

**Cache Strategy:**
- **TTL**: 1 hour by default
- **Size**: LRU eviction when full
- **Key**: Normalized query text
- **Hit Rate**: Typically 80-95% on repeated queries

## Complete Example Scenarios

### Scenario 1: Research Assistant

**User Goal**: Learn about quantum computing

```bash
# Session starts
$ python jarvis.py --interactive

You: ask What is quantum computing?

JARVIS: [Detailed explanation with 3 citations]

You: ask How does it differ from classical computing?

JARVIS: [Comparison with context from previous question]

You: search quantum computing companies

JARVIS: [Search results for companies in the field]

You: ask Which one is leading?

JARVIS: [Analysis based on search results and previous context]
```

**What Happens Behind the Scenes:**
1. Each "ask" triggers the full search workflow
2. Context is maintained across questions
3. Follow-up questions use previous conversation
4. Responses become more contextual over time

### Scenario 2: Quick Information Lookup

**User Goal**: Get a quick fact

```bash
$ python jarvis.py ask "Who invented the transistor?"

Response: The transistor was invented by three scientists at Bell 
Laboratories: John Bardeen, Walter Brattain, and William Shockley 
in 1947. They were awarded the Nobel Prize in Physics in 1956 for 
this invention.

[1] Transistor - Wikipedia
[2] The Invention of the Transistor - PBS
```

**What Happens:**
1. Single command execution (no conversation)
2. Quick search and response generation
3. Display result and exit
4. Total time: ~2-3 seconds

### Scenario 3: API Integration

**User Goal**: Build a custom chatbot

```python
# chatbot.py
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
SECI_API = "http://localhost:8000"

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json['user_id']
    
    # Forward to SECI
    response = requests.post(
        f"{SECI_API}/search",
        json={
            "query": user_message,
            "session_id": f"user-{user_id}"
        }
    )
    
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=5000)
```

**Workflow:**
1. User sends message to custom chatbot (port 5000)
2. Chatbot forwards to SECI API (port 8000)
3. SECI processes query with search workflow
4. Response sent back through chatbot
5. User receives answer

### Scenario 4: Continuous Learning

**User Goal**: Train model on custom domain

```python
# custom_training.py
from seci.config.config import SECIConfig
from train import SECITrainer

# Load configuration
config = SECIConfig.from_yaml("config/default.yaml")

# Customize for your domain
config.model.vocab_size = 32000  # Your tokenizer vocab size
config.training.learning_rate = 5e-5
config.training.num_epochs = 10

# Create trainer
trainer = SECITrainer(config)

# Load your domain-specific data
train_loader = load_your_data()

# Train
trainer.train(train_loader, num_epochs=config.training.num_epochs)

# Model now specialized for your domain!
```

**Workflow:**
1. Configure model for your domain
2. Prepare domain-specific data
3. Train using SECI framework
4. Components work together:
   - Student learns from data
   - Memory stores domain knowledge
   - Replay prevents forgetting
   - Distillation transfers understanding

## Workflow Optimization Tips

### For Users

1. **Use Interactive Mode for Exploration**
   - Better for multi-turn conversations
   - Maintains context automatically
   - More engaging experience

2. **Use Command Mode for Scripts**
   - Perfect for automation
   - Quick one-off queries
   - Easy to integrate in shell scripts

3. **Use API for Applications**
   - Build custom interfaces
   - Integrate with existing systems
   - Scale to multiple users

### For Developers

1. **Cache Aggressively**
   - Most queries are repeated
   - Cache at multiple levels
   - Monitor hit rates

2. **Parallelize Everything**
   - Search providers in parallel
   - Content scraping in parallel
   - Reduces total latency by 2-3x

3. **Monitor Performance**
   - Track query times
   - Log slow operations
   - Profile bottlenecks

## Next Steps

- **For Implementation**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **For Development**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **For Customization**: See [CONFIGURATION.md](CONFIG_STRATEGY.md)
- **For API Details**: See [API_REFERENCE.md](API_REFERENCE.md)

---

**Understanding the workflow helps you use SECI effectively!**
