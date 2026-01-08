"""
Example demonstrating enhanced SECI capabilities.
Shows smarter, better, and faster features in action.
"""

import logging
from seci.search import SearchEngine, DuckDuckGoProvider, AsyncSearchEngine
from seci.scraper import WebScraper
from seci.context import ContextManager
from seci.enhanced_processor import EnhancedQueryProcessor
from seci.utils import QueryEnhancer, ResultRanker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_query_enhancement():
    """Demonstrate query enhancement capabilities (SMARTER)."""
    print("\n" + "="*60)
    print("DEMO 1: SMARTER - Query Enhancement")
    print("="*60)
    
    enhancer = QueryEnhancer()
    
    # Test queries
    test_queries = [
        "What is machine learning?",
        "How to train a neural network?",
        "Why does gradient descent work?",
    ]
    
    for query in test_queries:
        print(f"\nOriginal query: {query}")
        
        # Extract keywords
        keywords = enhancer.extract_keywords(query)
        print(f"  Keywords: {keywords}")
        
        # Analyze intent
        analysis = enhancer.analyze_query_intent(query)
        print(f"  Intent: {analysis['type']}, Complexity: {analysis['complexity']}")
        
        # Generate variations
        variations = enhancer.expand_query(query, max_variations=2)
        print(f"  Variations: {variations}")
        
        # Enhanced queries
        enhanced = enhancer.enhance_for_search(query, use_variations=True)
        print(f"  Enhanced: {enhanced}")


def demo_result_ranking():
    """Demonstrate result ranking capabilities (BETTER)."""
    print("\n" + "="*60)
    print("DEMO 2: BETTER - Result Ranking")
    print("="*60)
    
    # Mock search results
    class MockResult:
        def __init__(self, title, url, snippet):
            self.title = title
            self.url = url
            self.snippet = snippet
    
    results = [
        MockResult(
            "Introduction to AI",
            "https://example.com/ai-intro",
            "AI is the simulation of human intelligence processes by machines"
        ),
        MockResult(
            "Machine Learning Basics",
            "https://wikipedia.org/wiki/machine_learning",
            "Machine learning is a subset of AI that enables computers to learn"
        ),
        MockResult(
            "AI Tutorial",
            "https://edu.example.edu/ai",
            "Complete tutorial on artificial intelligence and ML"
        ),
    ]
    
    query = "What is artificial intelligence?"
    
    ranker = ResultRanker()
    ranked = ranker.rank_results(results, query)
    
    print(f"\nQuery: {query}")
    print("\nRanked Results:")
    for i, ranked_result in enumerate(ranked, 1):
        print(f"\n{i}. {ranked_result.result.title}")
        print(f"   URL: {ranked_result.result.url}")
        print(f"   Score: {ranked_result.score:.3f}")
        print(f"   Factors: {ranked_result.ranking_factors}")


def demo_async_search():
    """Demonstrate async parallel search (FASTER)."""
    print("\n" + "="*60)
    print("DEMO 3: FASTER - Async Parallel Search")
    print("="*60)
    
    # Initialize search engine
    search_engine = SearchEngine()
    search_engine.add_provider(DuckDuckGoProvider())
    
    # Initialize async search
    async_engine = AsyncSearchEngine(
        providers=search_engine.providers,
        max_results=5,
        timeout=10
    )
    
    query = "Python programming language"
    
    print(f"\nQuery: {query}")
    print("Searching across providers in parallel...")
    
    # Perform parallel search
    from seci.search import search_parallel_sync
    import time
    
    start_time = time.time()
    async_results = search_parallel_sync(async_engine, query, num_results=5)
    duration = time.time() - start_time
    
    print(f"\nSearch completed in {duration:.2f} seconds")
    
    # Show statistics
    stats = async_engine.get_statistics(async_results)
    print(f"\nStatistics:")
    print(f"  Providers: {stats['total_providers']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Total results: {stats['total_results']}")
    print(f"  Average duration: {stats['avg_duration']:.2f}s")
    
    # Show results from each provider
    for provider, info in stats['providers'].items():
        print(f"\n  {provider}:")
        print(f"    Results: {info['results']}")
        print(f"    Duration: {info['duration']:.2f}s")
        print(f"    Success: {info['success']}")


def demo_intelligent_caching():
    """Demonstrate intelligent caching (FASTER)."""
    print("\n" + "="*60)
    print("DEMO 4: FASTER - Intelligent Caching")
    print("="*60)
    
    from seci.utils import QueryCache
    import time
    
    cache = QueryCache(max_size=100, default_ttl=3600)
    
    # Test queries
    queries = [
        "What is Python?",
        "what is python?",  # Should hit cache (normalized)
        "What is Python",   # Should hit cache (normalized)
        "What is Java?",    # New query
    ]
    
    print("\nTesting cache with query variations:")
    
    for query in queries:
        # Check cache
        cached = cache.get_query(query)
        
        if cached:
            print(f"\n✓ Cache HIT: '{query}'")
        else:
            print(f"\n✗ Cache MISS: '{query}'")
            # Simulate processing
            result = f"Answer for: {query}"
            cache.set_query(query, result)
            print(f"  Cached result for future use")
    
    # Show statistics
    stats = cache.get_statistics()
    print(f"\nCache Statistics:")
    print(f"  Size: {stats['size']}/{stats['max_size']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']:.2%}")


def demo_enhanced_processor():
    """Demonstrate full enhanced processor (ALL FEATURES)."""
    print("\n" + "="*60)
    print("DEMO 5: COMPLETE - Enhanced Query Processor")
    print("="*60)
    
    # Initialize components
    search_engine = SearchEngine()
    search_engine.add_provider(DuckDuckGoProvider())
    
    web_scraper = WebScraper(timeout=10)
    context_manager = ContextManager()
    
    # Initialize enhanced processor
    processor = EnhancedQueryProcessor(
        search_engine=search_engine,
        web_scraper=web_scraper,
        context_manager=context_manager,
        enable_async_search=True,
        enable_query_enhancement=True,
        enable_result_ranking=True,
        enable_caching=True,
    )
    
    print("\nEnhanced Processor Features:")
    print("  ✓ Async parallel search")
    print("  ✓ Query enhancement")
    print("  ✓ Result ranking")
    print("  ✓ Intelligent caching")
    
    # Process a query
    query = "What is artificial intelligence?"
    print(f"\nProcessing query: {query}")
    
    import time
    start_time = time.time()
    
    result = processor.process(query, session_id="demo-session")
    
    duration = time.time() - start_time
    
    print(f"\nQuery processed in {duration:.2f} seconds")
    print(f"\nResponse: {result.response[:200]}...")
    print(f"\nCitations: {len(result.citations)}")
    for i, citation in enumerate(result.citations[:3], 1):
        print(f"  [{i}] {citation['title']}")
    
    # Show cache stats
    cache_stats = processor.get_cache_statistics()
    if cache_stats:
        print(f"\nCache Statistics:")
        print(f"  Hit rate: {cache_stats.get('hit_rate', 0):.2%}")
        print(f"  Total requests: {cache_stats.get('total_requests', 0)}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("SECI ENHANCED CAPABILITIES DEMONSTRATION")
    print("Smarter, Better, and Faster Features")
    print("="*60)
    
    try:
        # Demo 1: Query Enhancement (Smarter)
        demo_query_enhancement()
        
        # Demo 2: Result Ranking (Better)
        demo_result_ranking()
        
        # Demo 3: Async Search (Faster)
        demo_async_search()
        
        # Demo 4: Intelligent Caching (Faster)
        demo_intelligent_caching()
        
        # Demo 5: Enhanced Processor (All features)
        demo_enhanced_processor()
        
        print("\n" + "="*60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nEnhanced Features Summary:")
        print("  🧠 SMARTER: Query enhancement with expansion and reformulation")
        print("  ⭐ BETTER: Intelligent ranking based on relevance and credibility")
        print("  ⚡ FASTER: Async parallel search and multi-level caching")
        print("\n")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
