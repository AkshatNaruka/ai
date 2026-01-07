"""
Example: Perplexity-like search with SECI

This example demonstrates how to use SECI's search capabilities
to perform web searches, scrape content, and maintain conversation context.
"""

import logging
from seci.search import SearchEngine, DuckDuckGoProvider
from seci.scraper import WebScraper
from seci.context import ContextManager
from seci.query_processor import QueryProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run example search queries."""
    
    print("=" * 80)
    print("SECI - Perplexity-like Search Example")
    print("=" * 80)
    
    # Initialize components
    print("\n1. Initializing components...")
    
    # Search engine with DuckDuckGo
    search_engine = SearchEngine(max_results=5)
    search_engine.add_provider(DuckDuckGoProvider())
    
    # Web scraper
    web_scraper = WebScraper(timeout=10)
    
    # Context manager for conversation
    context_manager = ContextManager(max_history=10)
    
    # Query processor
    processor = QueryProcessor(
        search_engine=search_engine,
        web_scraper=web_scraper,
        context_manager=context_manager,
        max_sources=5,
        scrape_top_n=3,
    )
    
    print("✓ Components initialized\n")
    
    # Example queries
    queries = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are the latest developments in AI?",
    ]
    
    session_id = "example-session"
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Processing query: '{query}'")
        print("-" * 80)
        
        try:
            # Process query
            result = processor.process(query, session_id=session_id)
            
            # Display results
            print(f"\nSearch Results ({len(result.search_results)} found):")
            for j, search_result in enumerate(result.search_results[:3], 1):
                print(f"\n  [{j}] {search_result.title}")
                print(f"      {search_result.url}")
                print(f"      {search_result.snippet[:100]}...")
            
            print(f"\nGenerated Response:")
            print(f"{result.response[:500]}...")
            
            print(f"\nCitations: {len(result.citations)}")
            for citation in result.citations[:3]:
                print(f"  [{citation['number']}] {citation['title']}")
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            continue
    
    # Show conversation history
    print("\n" + "=" * 80)
    print("Conversation History")
    print("=" * 80)
    
    history = context_manager.get_history(session_id)
    print(f"\nTotal messages: {len(history)}")
    
    for msg in history[-6:]:  # Show last 6 messages
        role_label = "USER" if msg.role == "user" else "ASSISTANT"
        print(f"\n{role_label}: {msg.content[:100]}...")
    
    print("\n" + "=" * 80)
    print("Example completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
