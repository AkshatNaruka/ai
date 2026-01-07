#!/usr/bin/env python3
"""
Simple CLI tool for testing SECI Search API
"""

import argparse
import sys
import requests
from typing import Optional
import json


def search(query: str, api_url: str = "http://localhost:8000", session_id: Optional[str] = None):
    """Perform a search query."""
    url = f"{api_url}/search"
    payload = {
        "query": query,
        "max_results": 5,
    }
    if session_id:
        payload["session_id"] = session_id
    
    try:
        print(f"\n🔍 Searching for: {query}\n")
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print(f"Session ID: {result['session_id']}")
        print(f"\n📝 Response:")
        print(f"{result['response']}\n")
        
        if result['citations']:
            print(f"📚 Citations ({len(result['citations'])}):")
            for citation in result['citations']:
                print(f"  [{citation['number']}] {citation['title']}")
                print(f"      {citation['url']}")
                print()
        
        print(f"✅ Found {result['metadata']['num_results']} results")
        print(f"📄 Scraped {result['metadata']['num_scraped']} pages")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to API at {api_url}")
        print("   Make sure the API server is running with: python api.py")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def get_history(session_id: str, api_url: str = "http://localhost:8000"):
    """Get conversation history."""
    url = f"{api_url}/conversation/{session_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        print(f"\n💬 Conversation History (Session: {session_id})")
        print(f"Created: {result['created_at']}")
        print(f"Updated: {result['updated_at']}")
        print(f"\nMessages ({len(result['messages'])}):\n")
        
        for msg in result['messages']:
            role_emoji = "👤" if msg['role'] == "user" else "🤖"
            print(f"{role_emoji} {msg['role'].upper()}:")
            print(f"   {msg['content'][:200]}...")
            print()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ Session '{session_id}' not found")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def health_check(api_url: str = "http://localhost:8000"):
    """Check API health."""
    url = f"{api_url}/health"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        result = response.json()
        
        print(f"\n✅ API is {result['status']}")
        print(f"Timestamp: {result['timestamp']}")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ API is offline or unreachable at {api_url}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="SECI Search API CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for information
  python cli_test.py search "What is artificial intelligence?"
  
  # Search with session ID
  python cli_test.py search "What is ML?" --session my-session
  
  # Get conversation history
  python cli_test.py history my-session
  
  # Check API health
  python cli_test.py health
        """
    )
    
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API URL (default: http://localhost:8000)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Perform a search query")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--session", help="Session ID for context")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Get conversation history")
    history_parser.add_argument("session_id", help="Session ID")
    
    # Health command
    subparsers.add_parser("health", help="Check API health")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "search":
        search(args.query, args.api_url, args.session)
    elif args.command == "history":
        get_history(args.session_id, args.api_url)
    elif args.command == "health":
        health_check(args.api_url)


if __name__ == "__main__":
    main()
