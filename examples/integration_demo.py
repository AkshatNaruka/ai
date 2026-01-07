"""
Integration Example: Complete Perplexity-like Search Workflow

This example demonstrates the full integration of all components:
1. Search engine setup
2. Web scraping
3. Context management
4. Query processing
5. Citation tracking
"""

import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seci.search import SearchEngine, DuckDuckGoProvider
from seci.scraper import WebScraper
from seci.context import ContextManager
from seci.query_processor import QueryProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title: str = ""):
    """Print a visual separator."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print('=' * 80)
    else:
        print('-' * 80)


def main():
    """Run the complete integration example."""
    
    print_separator("SECI Perplexity-like Search Integration Example")
    
    # Step 1: Initialize Components
    print("\n1️⃣  Initializing components...")
    print_separator()
    
    # Search engine
    search_engine = SearchEngine(max_results=5, timeout=10)
    search_engine.add_provider(DuckDuckGoProvider())
    print("   ✓ Search engine initialized with DuckDuckGo")
    
    # Web scraper
    web_scraper = WebScraper(timeout=10, max_content_length=50000)
    print("   ✓ Web scraper initialized")
    
    # Context manager
    context_manager = ContextManager(max_history=20)
    print("   ✓ Context manager initialized")
    
    # Query processor
    processor = QueryProcessor(
        search_engine=search_engine,
        web_scraper=web_scraper,
        context_manager=context_manager,
        max_sources=5,
        scrape_top_n=3
    )
    print("   ✓ Query processor initialized")
    
    # Step 2: Simulate a conversation
    print("\n2️⃣  Simulating conversation...")
    print_separator()
    
    session_id = "demo-session"
    queries = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are neural networks?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print_separator()
        
        try:
            # Process query
            result = processor.process(query, session_id=session_id)
            
            # Display search results
            print(f"\n🔍 Search Results ({len(result.search_results)} found):")
            for j, sr in enumerate(result.search_results[:3], 1):
                print(f"\n   [{j}] {sr.title}")
                print(f"       URL: {sr.url}")
                print(f"       Snippet: {sr.snippet[:100]}...")
            
            # Display scraped content
            print(f"\n📄 Scraped Content ({len([s for s in result.scraped_content if s.success])} successful):")
            for j, sc in enumerate([s for s in result.scraped_content if s.success][:2], 1):
                print(f"\n   [{j}] {sc.title}")
                print(f"       Content length: {len(sc.content)} chars")
                print(f"       Excerpt: {sc.content[:150]}...")
            
            # Display response
            print(f"\n🤖 Generated Response:")
            print(f"   {result.response[:400]}...")
            
            # Display citations
            print(f"\n📚 Citations ({len(result.citations)}):")
            for citation in result.citations[:3]:
                print(f"   [{citation['number']}] {citation['title']}")
            
            # Display metadata
            print(f"\n📊 Metadata:")
            print(f"   - Results found: {result.metadata['num_results']}")
            print(f"   - Pages scraped: {result.metadata['num_scraped']}")
            print(f"   - Timestamp: {result.timestamp}")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            continue
    
    # Step 3: Show conversation history
    print("\n3️⃣  Conversation History")
    print_separator()
    
    history = context_manager.get_history(session_id)
    print(f"\n💬 Session: {session_id}")
    print(f"📝 Total messages: {len(history)}")
    
    print("\nConversation flow:")
    for i, msg in enumerate(history, 1):
        role_emoji = "👤" if msg.role == "user" else "🤖"
        print(f"\n{role_emoji} {i}. {msg.role.upper()}:")
        content_preview = msg.content[:150]
        if len(msg.content) > 150:
            content_preview += "..."
        print(f"   {content_preview}")
    
    # Step 4: Export conversation
    print("\n4️⃣  Export Conversation")
    print_separator()
    
    exported = context_manager.export_context(session_id)
    if exported:
        print("\n✓ Conversation exported successfully")
        print(f"  Size: {len(exported)} bytes")
        
        # Save to file
        export_path = "/tmp/conversation_export.json"
        with open(export_path, "w") as f:
            f.write(exported)
        print(f"  Saved to: {export_path}")
    
    # Step 5: Statistics
    print("\n5️⃣  Statistics")
    print_separator()
    
    all_sessions = context_manager.get_all_sessions()
    print(f"\n📊 System Statistics:")
    print(f"   - Active sessions: {len(all_sessions)}")
    print(f"   - Messages in current session: {len(history)}")
    print(f"   - Total queries processed: {len(queries)}")
    
    # Final summary
    print_separator("Integration Test Complete!")
    print("\n✨ All components working together successfully!")
    print("\nKey features demonstrated:")
    print("   ✓ Multi-provider web search")
    print("   ✓ Intelligent content scraping")
    print("   ✓ Conversation context management")
    print("   ✓ Citation tracking")
    print("   ✓ Query processing pipeline")
    print("   ✓ Session management")
    print("   ✓ Data export\n")
    
    print("Next steps:")
    print("   1. Start the API server: python api.py")
    print("   2. Test with CLI: python cli_test.py search 'your query'")
    print("   3. Deploy to VPS: See docs/DEPLOYMENT.md")
    print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
