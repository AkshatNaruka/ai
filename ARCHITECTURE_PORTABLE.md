# SECI Portable Driver System - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SECI AI ASSISTANT (JARVIS)                       │
│                  Portable Driver System                             │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │   INSTALLER    │       │   JARVIS CLI   │
            │  (install.py)  │       │  (jarvis.py)   │
            └───────┬────────┘       └───────┬────────┘
                    │                        │
        ┌───────────┴──────────────┐        │
        │                           │        │
┌───────▼─────┐            ┌───────▼────┐   │
│  Platform   │            │  Resource  │   │
│  Detection  │            │ Detection  │   │
│  - Linux    │            │  - RAM     │   │
│  - macOS    │            │  - CPU     │   │
│  - Windows  │            │  - GPU     │   │
│  - ARM      │            │            │   │
└─────────────┘            └────────────┘   │
                                            │
        ┌───────────────────────────────────┤
        │                                   │
┌───────▼────────┐                 ┌────────▼────────┐
│  FULL MODE     │                 │  MINIMAL MODE   │
│  - PyTorch     │                 │  - No ML deps   │
│  - Transformers│                 │  - Search only  │
│  - Training    │                 │  - Lightweight  │
│  - 2GB+ RAM    │                 │  - 1GB RAM      │
└───────┬────────┘                 └────────┬────────┘
        │                                   │
        └───────────────┬───────────────────┘
                        │
            ┌───────────▼────────────┐
            │                        │
    ┌───────▼────────┐      ┌───────▼────────┐
    │   CLI MODE     │      │   API MODE     │
    │  - Interactive │      │  - REST API    │
    │  - Commands    │      │  - FastAPI     │
    │  - Questions   │      │  - Port 8000   │
    └───────┬────────┘      └───────┬────────┘
            │                       │
            └───────────┬───────────┘
                        │
            ┌───────────▼────────────┐
            │                        │
    ┌───────▼────────┐      ┌───────▼────────┐
    │   FOREGROUND   │      │   BACKGROUND   │
    │  - Direct run  │      │  - Service     │
    │  - Terminal    │      │  - systemd     │
    │  - Interactive │      │  - Docker      │
    └────────────────┘      └────────────────┘
```

## Installation Flow

```
User runs: python install.py
        │
        ├─▶ Detect Platform (OS, Architecture)
        │
        ├─▶ Check Python Version (3.8+)
        │
        ├─▶ Detect System Resources
        │   ├─▶ RAM available
        │   ├─▶ CPU cores
        │   └─▶ GPU (if available)
        │
        ├─▶ Create Virtual Environment
        │   └─▶ venv/ directory
        │
        ├─▶ Install Dependencies
        │   ├─▶ Full Mode (requirements.txt)
        │   └─▶ Minimal Mode (requirements-minimal.txt)
        │
        ├─▶ Install SECI Package
        │   └─▶ pip install -e .
        │
        ├─▶ Create CLI Entry Points
        │   ├─▶ jarvis command
        │   └─▶ seci-install command
        │
        ├─▶ Generate Service Templates
        │   └─▶ systemd/jarvis.service
        │
        ├─▶ Run Configuration Wizard
        │   └─▶ ~/.seci/config.json
        │
        └─▶ Display Success Message
            └─▶ Show quick start commands
```

## Usage Flow

```
User: python jarvis.py --interactive
        │
        ├─▶ Load Configuration
        │   └─▶ ~/.seci/config.json
        │
        ├─▶ Check API Server
        │   ├─▶ Running? → Connect
        │   └─▶ Not running? → Start
        │
        ├─▶ Enter Interactive Loop
        │   │
        │   ├─▶ User: ask "What is AI?"
        │   │   │
        │   │   ├─▶ Send to API Server
        │   │   │
        │   │   ├─▶ Search Web (if needed)
        │   │   │   ├─▶ DuckDuckGo
        │   │   │   └─▶ Google (if configured)
        │   │   │
        │   │   ├─▶ Scrape Content
        │   │   │
        │   │   ├─▶ Generate Response
        │   │   │
        │   │   └─▶ Display with Citations
        │   │
        │   ├─▶ User: search "topic"
        │   │   │
        │   │   └─▶ Show Search Results
        │   │
        │   └─▶ User: exit
        │       │
        │       └─▶ Goodbye!
        │
        └─▶ Save Session
```

## Platform Support Matrix

```
┌────────────────┬──────────┬──────────────┬──────────────┐
│   Platform     │  Status  │   Mode       │  Install     │
├────────────────┼──────────┼──────────────┼──────────────┤
│ Linux x86_64   │    ✅    │ Full/Minimal │ Standard     │
│ macOS x86_64   │    ✅    │ Full/Minimal │ Standard     │
│ macOS ARM64    │    ✅    │ Full/Minimal │ Standard     │
│ Windows 10/11  │    ✅    │ Full/Minimal │ Standard     │
│ Raspberry Pi   │    ✅    │ Minimal      │ --minimal    │
│ Android/Termux │    ✅    │ Minimal      │ --minimal    │
│ Docker         │    ✅    │ Full         │ docker build │
│ Cloud (AWS)    │    ✅    │ Full         │ Standard     │
│ Cloud (GCP)    │    ✅    │ Full         │ Standard     │
│ Cloud (Azure)  │    ✅    │ Full         │ Standard     │
└────────────────┴──────────┴──────────────┴──────────────┘
```

## Deployment Options

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT OPTIONS                        │
└─────────────────────────────────────────────────────────────┘

1. DIRECT CLI
   python jarvis.py --interactive
   │
   ├─▶ Best for: Personal use, testing, development
   ├─▶ Pros: Simple, immediate, interactive
   └─▶ Cons: Must be manually started

2. SYSTEMD SERVICE (Linux)
   sudo systemctl start jarvis
   │
   ├─▶ Best for: Servers, always-on systems
   ├─▶ Pros: Auto-start, monitoring, logs
   └─▶ Cons: Linux only

3. DOCKER CONTAINER
   docker-compose up -d
   │
   ├─▶ Best for: Cloud, scalability, isolation
   ├─▶ Pros: Portable, reproducible, scalable
   └─▶ Cons: Requires Docker

4. API SERVER
   python api.py
   │
   ├─▶ Best for: Web apps, mobile apps, integrations
   ├─▶ Pros: RESTful, accessible, programmable
   └─▶ Cons: Network required

5. BACKGROUND PROCESS
   python jarvis.py serve &
   │
   ├─▶ Best for: Quick testing, temporary use
   ├─▶ Pros: Fast to start, no configuration
   └─▶ Cons: Not persistent
```

## Component Interaction

```
┌──────────────┐
│     User     │
└──────┬───────┘
       │
       ├─▶ CLI Commands
       │   └─▶ jarvis.py
       │       ├─▶ ask
       │       ├─▶ search
       │       ├─▶ status
       │       └─▶ config
       │
       ├─▶ API Requests
       │   └─▶ api.py (FastAPI)
       │       ├─▶ POST /search
       │       ├─▶ GET /conversation/{id}
       │       └─▶ GET /health
       │
       └─▶ Interactive Mode
           └─▶ jarvis.py --interactive
               │
               ├─▶ QueryProcessor
               │   ├─▶ SearchEngine
               │   │   ├─▶ DuckDuckGo
               │   │   └─▶ Google
               │   │
               │   ├─▶ WebScraper
               │   │   └─▶ Extract content
               │   │
               │   └─▶ ContextManager
               │       └─▶ Session history
               │
               └─▶ Response with Citations
```

## Key Features

```
┌─────────────────────────────────────────────────────┐
│           JARVIS-LIKE CAPABILITIES                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ✓ Universal Installation                          │
│    └─▶ One command works everywhere                │
│                                                     │
│  ✓ Natural Language Interface                      │
│    └─▶ "ask", "search", simple commands            │
│                                                     │
│  ✓ Auto-Configuration                              │
│    └─▶ Detects and adapts to device                │
│                                                     │
│  ✓ Resource Adaptive                               │
│    └─▶ Full mode (powerful) or Minimal (lightweight)│
│                                                     │
│  ✓ Multiple Modes                                  │
│    └─▶ CLI, API, Interactive, Service              │
│                                                     │
│  ✓ Cross-Platform                                  │
│    └─▶ Desktop, Mobile, Server, IoT                │
│                                                     │
│  ✓ Easy Deployment                                 │
│    └─▶ Docker, systemd, standalone                 │
│                                                     │
│  ✓ Conversational                                  │
│    └─▶ Maintains context, provides sources         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## System Requirements

```
┌──────────────┬─────────────┬──────────────┬───────────────┐
│    Mode      │     RAM     │     Disk     │   Features    │
├──────────────┼─────────────┼──────────────┼───────────────┤
│  Minimal     │   1GB min   │   500MB      │ Search, API   │
│              │   2GB rec   │   1GB rec    │ No ML         │
├──────────────┼─────────────┼──────────────┼───────────────┤
│  Full        │   2GB min   │   1GB min    │ All features  │
│              │   4GB rec   │   2GB rec    │ + Training    │
│              │   8GB opt   │   4GB opt    │ + GPU support │
└──────────────┴─────────────┴──────────────┴───────────────┘

Common to all modes:
• Python 3.8+
• Internet connection (for search)
• Any OS (Linux, macOS, Windows, etc.)
```

---

**This architecture makes SECI truly portable - like a driver that can be**
**installed anywhere and run everywhere, just like Jarvis from Ironman! 🤖**
