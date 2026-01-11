"""
Complete SECI Tutorial - Step-by-Step Guide

This tutorial walks through all major features of SECI with detailed
explanations and practical examples.

Topics covered:
1. Basic search queries
2. Web content scraping
3. Conversational context
4. Result ranking and filtering
5. Query enhancement
6. Caching for performance

Author: SECI Team
License: MIT
"""

import logging
import time
from typing import List

# SECI imports
from seci.search import SearchEngine, DuckDuckGoProvider
from seci.scraper import WebScraper
from seci.context import ContextManager
from seci.query_processor import QueryProcessor
from seci.utils import QueryEnhancer, ResultRanker, IntelligentCache

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a section header for better readability."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def example_1_basic_search():
    """
    Example 1: Basic Web Search
    
    Learn how to:
    - Initialize a search engine
    - Add search providers
    - Perform a simple search
    - Display results
    """
    print_section("Example 1: Basic Web Search")
    
    # Step 1: Create a search engine
    # The search engine manages multiple search providers
    search_engine = SearchEngine(max_results=10)
    
    # Step 2: Add a search provider
    # DuckDuckGo doesn't require an API key!
    search_engine.add_provider(DuckDuckGoProvider())
    
    print("✓ Search engine initialized with DuckDuckGo\n")
    
    # Step 3: Perform a search
    query = "Python programming language"
    print(f"Searching for: '{query}'")
    
    start_time = time.time()
    results = search_engine.search(query, num_results=5)
    search_time = time.time() - start_time
    
    # Step 4: Display results
    print(f"\nFound {len(results)} results in {search_time:.2f} seconds:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Snippet: {result.snippet[:100]}...")
        print(f"   Source: {result.source}")
        print()
    
    return results


def example_2_web_scraping(search_results: List):
    """
    Example 2: Web Content Scraping
    
    Learn how to:
    - Initialize a web scraper
    - Scrape content from URLs
    - Extract clean text
    - Handle errors gracefully
    """
    print_section("Example 2: Web Content Scraping")
    
    # Step 1: Create a web scraper
    scraper = WebScraper(
        timeout=10,              # Wait up to 10 seconds per page
        max_content_length=50000 # Limit content size to prevent memory issues
    )
    
    print("✓ Web scraper initialized\n")
    
    # Step 2: Scrape the first result
    if not search_results:
        print("No search results to scrape!")
        return
    
    url = search_results[0].url
    print(f"Scraping: {url}\n")
    
    try:
        start_time = time.time()
        content = scraper.scrape(url)
        scrape_time = time.time() - start_time
        
        # Step 3: Display scraped content
        print(f"✓ Scraped in {scrape_time:.2f} seconds")
        print(f"\nTitle: {content.title}")
        print(f"Author: {content.metadata.get('author', 'Unknown')}")
        print(f"Date: {content.metadata.get('date', 'Unknown')}")
        print(f"Content length: {len(content.content)} characters")
        print(f"\nFirst 300 characters:")
        print(content.content[:300] + "...")
        
        return content
        
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        print(f"✗ Scraping failed: {e}")
        return None


def example_3_conversation_context():
    """
    Example 3: Conversational Context
    
    Learn how to:
    - Maintain conversation history
    - Add user and assistant messages
    - Retrieve conversation history
    - Use session IDs for different conversations
    """
    print_section("Example 3: Conversational Context")
    
    # Step 1: Create a context manager
    context = ContextManager(max_history=20)  # Keep last 20 messages
    
    print("✓ Context manager initialized\n")
    
    # Step 2: Simulate a conversation
    session_id = "user-123"
    
    conversations = [
        ("user", "What is Python?"),
        ("assistant", "Python is a high-level programming language..."),
        ("user", "What are its main uses?"),  # "its" refers to Python
        ("assistant", "Python is used for web development, data science..."),
        ("user", "Can you give examples?"),  # Context understood
        ("assistant", "Sure! Django for web, Pandas for data...")
    ]
    
    # Step 3: Add messages to context
    print("Adding conversation messages:")
    for role, content in conversations:
        if role == "user":
            context.add_user_message(session_id, content)
        else:
            context.add_assistant_message(session_id, content)
        print(f"  {role.upper()}: {content[:50]}...")
    
    # Step 4: Retrieve and display history
    history = context.get_history(session_id)
    
    print(f"\n✓ Conversation has {len(history)} messages")
    print("\nFull conversation history:")
    for msg in history:
        role_label = "👤 USER" if msg.role == "user" else "🤖 ASSISTANT"
        print(f"\n{role_label}:")
        print(f"  {msg.content}")
    
    # Step 5: Demonstrate context benefits
    print("\n📝 Note: Context allows SECI to understand references like")
    print("   'its', 'them', 'that' in follow-up questions!")
    
    return context


def example_4_query_enhancement():
    """
    Example 4: Query Enhancement
    
    Learn how to:
    - Enhance queries automatically
    - Generate query variations
    - Extract keywords
    - Improve search results
    """
    print_section("Example 4: Query Enhancement")
    
    # Step 1: Create a query enhancer
    enhancer = QueryEnhancer()
    
    print("✓ Query enhancer initialized\n")
    
    # Step 2: Original query
    query = "ML basics"
    print(f"Original query: '{query}'\n")
    
    # Step 3: Enhance query
    enhanced = enhancer.enhance_for_search(
        query,
        use_variations=True,   # Generate variations
        max_variations=5       # Limit to 5 variations
    )
    
    # Step 4: Display enhancements
    print("Enhanced variations:")
    for i, variation in enumerate(enhanced, 1):
        print(f"  {i}. {variation}")
    
    # Step 5: Extract keywords
    keywords = enhancer.extract_keywords(query)
    print(f"\nExtracted keywords: {', '.join(keywords)}")
    
    print("\n✓ Query enhancement helps find more comprehensive results!")
    
    return enhanced


def example_5_result_ranking():
    """
    Example 5: Result Ranking
    
    Learn how to:
    - Score search results
    - Rank by relevance
    - Filter low-quality results
    - Understand ranking factors
    """
    print_section("Example 5: Result Ranking")
    
    # Step 1: Create a result ranker
    ranker = ResultRanker(
        keyword_weight=0.3,      # How important is keyword match?
        title_weight=0.25,       # How important is title match?
        snippet_weight=0.25,     # How important is snippet quality?
        credibility_weight=0.2   # How important is source credibility?
    )
    
    print("✓ Result ranker initialized")
    print(f"  Ranking weights:")
    print(f"    - Keyword match: 30%")
    print(f"    - Title relevance: 25%")
    print(f"    - Snippet quality: 25%")
    print(f"    - Source credibility: 20%\n")
    
    # Step 2: Get some results to rank
    search_engine = SearchEngine()
    search_engine.add_provider(DuckDuckGoProvider())
    
    query = "machine learning tutorial"
    print(f"Searching for: '{query}'")
    
    results = search_engine.search(query, num_results=10)
    
    # Step 3: Rank results
    print(f"\nRanking {len(results)} results...")
    ranked = ranker.rank_results(results, query)
    
    # Step 4: Display top results with scores
    print("\nTop 5 Results (with scores):\n")
    
    for i, (result, score) in enumerate(ranked[:5], 1):
        print(f"{i}. {result.title}")
        print(f"   Score: {score:.3f}")
        print(f"   URL: {result.url}")
        print()
    
    print("✓ Higher scores indicate more relevant results!")
    
    return ranked


def example_6_intelligent_caching():
    """
    Example 6: Intelligent Caching
    
    Learn how to:
    - Enable caching for performance
    - Cache query results
    - Measure cache hit rates
    - Clear cache when needed
    """
    print_section("Example 6: Intelligent Caching")
    
    # Step 1: Create cache
    cache = IntelligentCache(
        max_size=100,    # Store up to 100 queries
        ttl=3600         # Cache expires after 1 hour
    )
    
    print("✓ Cache initialized (max 100 queries, 1 hour TTL)\n")
    
    # Step 2: Simulate queries with caching
    queries = [
        "Python programming",
        "Machine learning basics",
        "Python programming",      # Repeated - will hit cache
        "Data science tools",
        "Python programming",      # Repeated again - cache hit
    ]
    
    search_engine = SearchEngine()
    search_engine.add_provider(DuckDuckGoProvider())
    
    print("Processing queries (watch for cache hits):\n")
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. Query: '{query}'")
        
        # Check cache first
        cached_result = cache.get(query)
        
        if cached_result is not None:
            print("   ⚡ CACHE HIT! (instant result)")
            result = cached_result
        else:
            print("   🔍 Searching... (first time)")
            start = time.time()
            result = search_engine.search(query, num_results=3)
            elapsed = time.time() - start
            print(f"   ✓ Found {len(result)} results in {elapsed:.2f}s")
            
            # Store in cache
            cache.set(query, result)
        
        print()
    
    # Step 3: Display cache statistics
    stats = cache.get_stats()
    print("Cache Statistics:")
    print(f"  Total queries: {stats['total_queries']}")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Cache misses: {stats['cache_misses']}")
    
    if stats['total_queries'] > 0:
        hit_rate = stats['cache_hits'] / stats['total_queries'] * 100
        print(f"  Hit rate: {hit_rate:.1f}%")
    
    print("\n✓ Caching dramatically improves performance for repeated queries!")


def example_7_complete_workflow():
    """
    Example 7: Complete Workflow
    
    Putting it all together:
    - Query enhancement
    - Parallel search
    - Content scraping
    - Result ranking
    - Response generation
    - Context management
    """
    print_section("Example 7: Complete Workflow")
    
    print("This example shows all components working together.\n")
    
    # Step 1: Initialize all components
    print("1. Initializing components...")
    
    search_engine = SearchEngine()
    search_engine.add_provider(DuckDuckGoProvider())
    
    scraper = WebScraper(timeout=10)
    context = ContextManager(max_history=20)
    
    processor = QueryProcessor(
        search_engine=search_engine,
        web_scraper=scraper,
        context_manager=context,
        max_sources=5,
        scrape_top_n=3
    )
    
    print("✓ All components initialized\n")
    
    # Step 2: Process a complex query
    query = "How does machine learning work?"
    session_id = "tutorial-session"
    
    print(f"2. Processing query: '{query}'")
    print("   This will:")
    print("   - Enhance the query")
    print("   - Search multiple sources")
    print("   - Scrape top results")
    print("   - Generate comprehensive answer")
    print("   - Store in conversation context\n")
    
    start_time = time.time()
    
    try:
        result = processor.process(query, session_id=session_id)
        
        elapsed = time.time() - start_time
        
        # Step 3: Display results
        print(f"✓ Completed in {elapsed:.2f} seconds\n")
        
        print("Search Results:")
        for i, sr in enumerate(result.search_results[:3], 1):
            print(f"  {i}. {sr.title}")
            print(f"     {sr.url}")
        
        print(f"\nGenerated Response:")
        print(f"{result.response[:400]}...")
        
        print(f"\nCitations:")
        for citation in result.citations[:3]:
            print(f"  [{citation['number']}] {citation['title']}")
        
        print(f"\n✓ Complete workflow executed successfully!")
        
    except Exception as e:
        logger.error(f"Error in workflow: {e}")
        print(f"✗ Error: {e}")


def main():
    """Run all examples."""
    
    print("\n" + "=" * 80)
    print(" " * 20 + "SECI Complete Tutorial")
    print(" " * 15 + "Learn by Example - Step by Step")
    print("=" * 80)
    
    print("\nThis tutorial demonstrates all major features of SECI.")
    print("Each example builds on the previous one.\n")
    
    input("Press Enter to start...")
    
    # Run examples
    try:
        # Example 1: Basic search
        results = example_1_basic_search()
        input("\nPress Enter for next example...")
        
        # Example 2: Web scraping
        if results:
            content = example_2_web_scraping(results)
        input("\nPress Enter for next example...")
        
        # Example 3: Conversation context
        context = example_3_conversation_context()
        input("\nPress Enter for next example...")
        
        # Example 4: Query enhancement
        enhanced = example_4_query_enhancement()
        input("\nPress Enter for next example...")
        
        # Example 5: Result ranking
        ranked = example_5_result_ranking()
        input("\nPress Enter for next example...")
        
        # Example 6: Caching
        example_6_intelligent_caching()
        input("\nPress Enter for final example...")
        
        # Example 7: Complete workflow
        example_7_complete_workflow()
        
    except KeyboardInterrupt:
        print("\n\nTutorial interrupted by user.")
    except Exception as e:
        logger.error(f"Tutorial error: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
    
    # Conclusion
    print_section("Tutorial Complete!")
    
    print("You've learned:")
    print("  ✓ How to search the web")
    print("  ✓ How to scrape content")
    print("  ✓ How to maintain conversation context")
    print("  ✓ How to enhance queries")
    print("  ✓ How to rank results")
    print("  ✓ How to use caching")
    print("  ✓ How to use the complete workflow")
    
    print("\nNext steps:")
    print("  • Read the User Guide: docs/USER_GUIDE.md")
    print("  • Explore the API: docs/API_REFERENCE.md")
    print("  • Try the examples: examples/")
    print("  • Build your own application!")
    
    print("\n" + "=" * 80)
    print("Happy coding with SECI! 🚀")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
