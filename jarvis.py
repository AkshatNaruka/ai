#!/usr/bin/env python3
"""
Jarvis - SECI AI Assistant CLI

A simple, natural language interface to the SECI AI system.
Can be installed and run anywhere like a driver.
"""

import sys
import argparse
import os
from pathlib import Path
import json
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_jarvis(text, color=Colors.OKCYAN):
    """Print message from Jarvis."""
    print(f"{color}{Colors.BOLD}JARVIS:{Colors.ENDC} {text}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}ERROR:{Colors.ENDC} {text}")


def load_config():
    """Load user configuration."""
    config_file = Path.home() / ".seci" / "config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
    
    # Default config
    return {
        'api_port': 8000,
        'api_host': 'localhost',
        'enable_search': True,
        'max_results': 5,
        'session_id': None,
    }


def save_config(config):
    """Save user configuration."""
    config_dir = Path.home() / ".seci"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def check_server_running(host='localhost', port=8000):
    """Check if API server is running."""
    try:
        import requests
        response = requests.get(f"http://{host}:{port}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_server_background(port=8000):
    """Start API server in the background."""
    import subprocess
    
    print_jarvis("Starting API server in the background...")
    
    try:
        # Start server as daemon process
        process = subprocess.Popen(
            [sys.executable, "api.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Wait a moment for server to start
        import time
        time.sleep(3)
        
        if check_server_running(port=port):
            print_jarvis(f"API server started on port {port}", Colors.OKGREEN)
            return True
        else:
            print_error("Server started but not responding")
            return False
            
    except Exception as e:
        print_error(f"Failed to start server: {e}")
        return False


def ask_question(query: str, config: dict):
    """Ask Jarvis a question."""
    import requests
    
    host = config.get('api_host', 'localhost')
    port = config.get('api_port', 8000)
    api_url = f"http://{host}:{port}"
    
    # Check if server is running
    if not check_server_running(host, port):
        print_jarvis("API server is not running. Starting it now...")
        if not start_server_background(port):
            print_error("Please start the API server manually: python api.py")
            return
    
    print_jarvis(f"Processing your request: \"{query}\"")
    
    payload = {
        "query": query,
        "max_results": config.get('max_results', 5),
    }
    
    if config.get('session_id'):
        payload["session_id"] = config['session_id']
    
    try:
        response = requests.post(f"{api_url}/search", json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        print()
        print_jarvis("Here's what I found:", Colors.OKGREEN)
        print()
        print(result['response'])
        print()
        
        if result.get('citations'):
            print(f"{Colors.BOLD}Sources:{Colors.ENDC}")
            for citation in result['citations'][:5]:
                print(f"  [{citation['number']}] {citation['title']}")
                print(f"      {citation['url']}")
            print()
        
        # Save session ID for context
        if result.get('session_id') and not config.get('session_id'):
            config['session_id'] = result['session_id']
            save_config(config)
            
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get response: {e}")
    except KeyError as e:
        print_error(f"Invalid response format: {e}")


def search_web(query: str, config: dict):
    """Search the web."""
    import requests
    
    host = config.get('api_host', 'localhost')
    port = config.get('api_port', 8000)
    api_url = f"http://{host}:{port}"
    
    if not check_server_running(host, port):
        print_jarvis("API server is not running. Starting it now...")
        if not start_server_background(port):
            print_error("Please start the API server manually: python api.py")
            return
    
    print_jarvis(f"Searching for: \"{query}\"")
    
    payload = {
        "query": query,
        "max_results": config.get('max_results', 5),
        "scrape_content": False,  # Just search, don't scrape
    }
    
    try:
        response = requests.post(f"{api_url}/search", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print()
        print_jarvis(f"Found {len(result.get('search_results', []))} results:", Colors.OKGREEN)
        print()
        
        for i, res in enumerate(result.get('search_results', [])[:10], 1):
            print(f"{Colors.BOLD}[{i}] {res['title']}{Colors.ENDC}")
            print(f"    {res['url']}")
            if res.get('snippet'):
                print(f"    {res['snippet'][:150]}...")
            print()
            
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to search: {e}")


def interactive_mode(config: dict):
    """Run Jarvis in interactive mode."""
    print()
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'JARVIS - SECI AI Assistant'.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print()
    print_jarvis("Hello! I'm Jarvis, your AI assistant.", Colors.OKGREEN)
    print_jarvis("I can help you search the web, answer questions, and more.")
    print()
    print(f"{Colors.BOLD}Commands:{Colors.ENDC}")
    print("  ask <question>    - Ask me a question")
    print("  search <query>    - Search the web")
    print("  config            - Show configuration")
    print("  clear             - Clear conversation history")
    print("  help              - Show this help")
    print("  exit/quit         - Exit interactive mode")
    print()
    
    while True:
        try:
            user_input = input(f"{Colors.OKBLUE}You:{Colors.ENDC} ").strip()
            
            if not user_input:
                continue
            
            # Parse command
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if cmd in ['exit', 'quit', 'q']:
                print_jarvis("Goodbye!", Colors.OKGREEN)
                break
            
            elif cmd == 'help':
                print()
                print(f"{Colors.BOLD}Available commands:{Colors.ENDC}")
                print("  ask <question>    - Ask me a question")
                print("  search <query>    - Search the web")
                print("  config            - Show configuration")
                print("  clear             - Clear conversation history")
                print("  help              - Show this help")
                print("  exit/quit         - Exit")
                print()
            
            elif cmd == 'ask':
                if not args:
                    print_error("Please provide a question")
                    continue
                ask_question(args, config)
            
            elif cmd == 'search':
                if not args:
                    print_error("Please provide a search query")
                    continue
                search_web(args, config)
            
            elif cmd == 'config':
                print()
                print(f"{Colors.BOLD}Current Configuration:{Colors.ENDC}")
                for key, value in config.items():
                    print(f"  {key}: {value}")
                print()
            
            elif cmd == 'clear':
                if config.get('session_id'):
                    config['session_id'] = None
                    save_config(config)
                    print_jarvis("Conversation history cleared", Colors.OKGREEN)
                else:
                    print_jarvis("No active session to clear")
            
            else:
                # Assume it's a question if no command matched
                ask_question(user_input, config)
            
        except KeyboardInterrupt:
            print()
            print_jarvis("Goodbye!", Colors.OKGREEN)
            break
        except EOFError:
            print()
            break
        except Exception as e:
            print_error(f"An error occurred: {e}")
            logger.exception("Error in interactive mode")


def show_status(config: dict):
    """Show system status."""
    host = config.get('api_host', 'localhost')
    port = config.get('api_port', 8000)
    
    print()
    print(f"{Colors.BOLD}SECI AI Assistant Status{Colors.ENDC}")
    print("─" * 50)
    print()
    
    # Check server
    server_status = "Running ✓" if check_server_running(host, port) else "Stopped ✗"
    print(f"API Server: {server_status}")
    print(f"API URL: http://{host}:{port}")
    print()
    
    # Show config
    print(f"{Colors.BOLD}Configuration:{Colors.ENDC}")
    print(f"  Search enabled: {config.get('enable_search', True)}")
    print(f"  Max results: {config.get('max_results', 5)}")
    print(f"  Session ID: {config.get('session_id', 'None')}")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Jarvis - SECI AI Assistant CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python jarvis.py --interactive
  
  # Ask a question
  python jarvis.py ask "What is artificial intelligence?"
  
  # Search the web
  python jarvis.py search "latest AI news"
  
  # Show status
  python jarvis.py status
  
  # Start API server
  python jarvis.py serve
        """
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a question')
    ask_parser.add_argument('query', nargs='+', help='Question to ask')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search the web')
    search_parser.add_argument('query', nargs='+', help='Search query')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start API server')
    serve_parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'),
                              help='Set configuration value')
    config_parser.add_argument('--show', action='store_true',
                              help='Show current configuration')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    # Load config
    config = load_config()
    
    # Handle commands
    if args.interactive:
        interactive_mode(config)
    
    elif args.command == 'ask':
        query = ' '.join(args.query)
        ask_question(query, config)
    
    elif args.command == 'search':
        query = ' '.join(args.query)
        search_web(query, config)
    
    elif args.command == 'status':
        show_status(config)
    
    elif args.command == 'serve':
        print_jarvis(f"Starting API server on {args.host}:{args.port}...")
        import subprocess
        try:
            subprocess.run([
                sys.executable, "api.py"
            ])
        except KeyboardInterrupt:
            print()
            print_jarvis("Server stopped", Colors.OKGREEN)
    
    elif args.command == 'config':
        if args.set:
            key, value = args.set
            # Try to parse value as JSON for proper types
            try:
                value = json.loads(value)
            except:
                pass  # Keep as string
            config[key] = value
            save_config(config)
            print_jarvis(f"Configuration updated: {key} = {value}", Colors.OKGREEN)
        
        elif args.show or not (args.set):
            print()
            print(f"{Colors.BOLD}Current Configuration:{Colors.ENDC}")
            print(json.dumps(config, indent=2))
            print()
    
    else:
        # No command specified, show help
        parser.print_help()


if __name__ == "__main__":
    main()
