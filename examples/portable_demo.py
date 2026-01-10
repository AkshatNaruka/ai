#!/usr/bin/env python3
"""
Demo: Portable AI Assistant (Jarvis) Usage Examples

This script demonstrates how SECI can be used as a portable AI assistant
that works on any platform with simple commands.
"""

import sys
import subprocess
import time


def print_header(text):
    """Print a section header."""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")


def run_command(cmd, description):
    """Run a command and display output."""
    print(f"📝 {description}")
    print(f"💻 Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("Output:")
        print(result.stdout)
    
    if result.stderr and result.returncode != 0:
        print("Error:")
        print(result.stderr)
    
    print()
    return result.returncode == 0


def main():
    """Run demonstration."""
    
    print_header("SECI AI Assistant (Jarvis) - Portable Driver Demo")
    
    print("""
This demonstration shows how SECI can be installed and used on any device
like a driver, with simple natural language commands - just like Jarvis from Ironman!

Key Features:
  ✓ Cross-platform (Linux, macOS, Windows, Raspberry Pi, Android)
  ✓ One-command installation
  ✓ Natural language interface
  ✓ Minimal or full mode based on device capabilities
  ✓ Can run as a service or interactive CLI
    """)
    
    input("Press Enter to continue...")
    
    # Demo 1: Installation
    print_header("1. Installation - Any Platform")
    
    print("""
Installation is as simple as:

    git clone https://github.com/AkshatNaruka/ai.git
    cd ai
    python install.py

The installer:
  • Detects your platform automatically
  • Checks system resources
  • Installs appropriate dependencies
  • Configures the system for you
  • Sets up CLI commands
    """)
    
    input("Press Enter to see installer help...")
    run_command("python install.py --help", "Installer Help")
    
    # Demo 2: CLI Commands
    print_header("2. Simple CLI Commands")
    
    print("""
Once installed, you can interact with Jarvis using simple commands:
    """)
    
    input("Press Enter to see available commands...")
    run_command("python jarvis.py --help", "Jarvis CLI Help")
    
    # Demo 3: Status Check
    print_header("3. System Status")
    
    print("""
Check the status of your AI assistant:
    """)
    
    input("Press Enter to check status...")
    run_command("python jarvis.py status", "Check System Status")
    
    # Demo 4: Configuration
    print_header("4. Configuration Management")
    
    print("""
Configuration is stored in ~/.seci/config.json and can be managed easily:
    """)
    
    input("Press Enter to see configuration...")
    run_command("python jarvis.py config --show", "Show Configuration")
    
    # Demo 5: Interactive Mode
    print_header("5. Interactive Mode")
    
    print("""
The most powerful feature is interactive mode, where you can have a
conversation with Jarvis:

    python jarvis.py --interactive

Then you can:
    You: ask What is machine learning?
    JARVIS: [provides detailed answer with sources]
    
    You: search latest AI news
    JARVIS: [shows search results]
    
    You: help
    [shows available commands]

(Interactive mode requires API server to be running)
    """)
    
    print("Note: Interactive mode demo skipped (requires API server)")
    
    # Demo 6: Docker Deployment
    print_header("6. Docker Deployment")
    
    print("""
For even easier deployment, use Docker:

    # Build and run
    docker-compose up -d
    
    # Or with docker directly
    docker build -t jarvis .
    docker run -d -p 8000:8000 jarvis

The API will be available at http://localhost:8000
    """)
    
    # Demo 7: Platform-Specific Examples
    print_header("7. Platform-Specific Examples")
    
    print("""
Linux (Ubuntu/Debian):
    sudo apt install python3 python3-pip git
    git clone https://github.com/AkshatNaruka/ai.git
    cd ai && python3 install.py
    
Raspberry Pi:
    # Minimal mode for limited resources
    python3 install.py --minimal
    
Android (Termux):
    pkg install python git clang
    git clone https://github.com/AkshatNaruka/ai.git
    cd ai && python install.py --minimal
    
macOS:
    brew install python git
    git clone https://github.com/AkshatNaruka/ai.git
    cd ai && python3 install.py
    
Windows (PowerShell):
    git clone https://github.com/AkshatNaruka/ai.git
    cd ai
    python install.py
    """)
    
    # Demo 8: Service Mode
    print_header("8. Running as a Service")
    
    print("""
SECI can run as a background service on various platforms:

Linux (systemd):
    sudo cp systemd/jarvis.service /etc/systemd/system/
    sudo systemctl enable jarvis
    sudo systemctl start jarvis

macOS (launchd):
    # Use generated plist file
    launchctl load ~/Library/LaunchAgents/com.seci.jarvis.plist

Windows:
    # Use Windows Service manager or Task Scheduler
    python jarvis.py serve  # Run in background

Once running as a service, you can access Jarvis via:
  • HTTP API at http://localhost:8000
  • CLI commands: python jarvis.py ask "..."
  • Web interface (if configured)
    """)
    
    # Demo 9: Minimal vs Full Mode
    print_header("9. Minimal vs Full Mode")
    
    print("""
SECI adapts to your device:

Full Mode (2GB+ RAM):
  • Complete AI features
  • PyTorch models
  • Advanced transformers
  • Local training
  
Minimal Mode (1GB RAM):
  • Web search & scraping
  • API server
  • Conversational interface
  • No heavy ML dependencies
  
This makes SECI usable on:
  ✓ Cloud servers
  ✓ Desktop computers
  ✓ Laptops
  ✓ Raspberry Pi
  ✓ IoT devices
  ✓ Android phones (via Termux)
    """)
    
    # Demo 10: Real-World Use Cases
    print_header("10. Real-World Use Cases")
    
    print("""
1. Personal Assistant:
   python jarvis.py ask "What's the weather like today?"
   
2. Research Helper:
   python jarvis.py search "machine learning papers 2024"
   
3. Development Aid:
   python jarvis.py ask "How do I implement a REST API in Python?"
   
4. Information Lookup:
   python jarvis.py ask "Who won the Nobel Prize in Physics?"
   
5. Home Automation:
   # Run on Raspberry Pi as a service
   # Integrate with home automation systems
   
6. Mobile Assistant:
   # Install on Android via Termux
   # Use anywhere, anytime
   
7. Educational Tool:
   # Interactive learning
   python jarvis.py --interactive
   You: ask Explain quantum computing
   
8. API Backend:
   # Deploy on cloud
   # Use as backend for web/mobile apps
   curl -X POST http://your-server:8000/search \\
     -d '{"query": "your question"}'
    """)
    
    # Summary
    print_header("Summary: Why SECI is Like a Portable Driver")
    
    print("""
✓ Universal Installation
  One command works on any platform - no complex setup

✓ Adaptive Configuration  
  Automatically adjusts to your device capabilities

✓ Simple Interface
  Natural language commands - no programming required

✓ Portable & Lightweight
  Minimal mode works on resource-constrained devices

✓ Multiple Deployment Options
  CLI, API server, Docker, service mode

✓ Cross-Platform
  Linux, macOS, Windows, ARM, Android support

✓ Like Jarvis from Ironman
  Install anywhere, ask anything, get intelligent responses

This makes SECI truly portable - install it on your laptop, deploy it to the
cloud, run it on Raspberry Pi, or even use it on your Android phone. It's
always ready to help, just like a driver that works on any device!
    """)
    
    print("\n" + "="*70)
    print("Demo Complete!".center(70))
    print("="*70)
    print("\nTo get started:")
    print("  1. Run: python install.py")
    print("  2. Try: python jarvis.py --interactive")
    print("  3. Explore: python jarvis.py --help")
    print("\nFor full documentation, see:")
    print("  • QUICKSTART.md")
    print("  • README.md")
    print("  • docs/platforms/INSTALLATION.md")
    print()


if __name__ == "__main__":
    main()
