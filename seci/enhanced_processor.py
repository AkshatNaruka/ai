"""
Enhanced query processor with advanced capabilities.
Implements smarter, better, and faster query processing.
"""

from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from .query_processor import QueryProcessor, ProcessedQuery
from .search import SearchEngine, AsyncSearchEngine, search_parallel_sync
from .scraper import WebScraper, ScrapedContent
from .context import ContextManager
from .utils.query_enhancer import QueryEnhancer
from .utils.result_ranker import ResultRanker, RankedResult
from .utils.intelligent_cache import QueryCache

logger = logging.getLogger(__name__)


class EnhancedQueryProcessor(QueryProcessor):
    """
    Enhanced query processor with advanced capabilities:
    - Query expansion and reformulation (smarter)
    - Result ranking and relevance scoring (better)
    - Parallel search and intelligent caching (faster)
    """
    
    def __init__(
        self,
        search_engine: SearchEngine,
        web_scraper: WebScraper,
        context_manager: ContextManager,
        model: Optional[Any] = None,
        max_sources: int = 5,
        scrape_top_n: int = 3,
        enable_async_search: bool = True,
        enable_query_enhancement: bool = True,
        enable_result_ranking: bool = True,
        enable_caching: bool = True,
        cache_ttl: int = 3600,
    ):
        """
        Initialize enhanced query processor.
        
        Args:
            search_engine: Search engine instance
            web_scraper: Web scraper instance
            context_manager: Context manager instance
            model: AI model for response generation
            max_sources: Maximum search results
            scrape_top_n: Number of results to scrape
            enable_async_search: Enable parallel search
            enable_query_enhancement: Enable query expansion
            enable_result_ranking: Enable result ranking
            enable_caching: Enable intelligent caching
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(
            search_engine=search_engine,
            web_scraper=web_scraper,
            context_manager=context_manager,
            model=model,
            max_sources=max_sources,
            scrape_top_n=scrape_top_n,
        )
        
        # Enhanced features
        self.enable_async_search = enable_async_search
        self.enable_query_enhancement = enable_query_enhancement
        self.enable_result_ranking = enable_result_ranking
        self.enable_caching = enable_caching
        
        # Initialize enhancement components
        if enable_query_enhancement:
            self.query_enhancer = QueryEnhancer()
        
        if enable_result_ranking:
            self.result_ranker = ResultRanker()
        
        if enable_caching:
            self.query_cache = QueryCache(max_size=1000, default_ttl=cache_ttl)
        
        if enable_async_search:
            self.async_search_engine = AsyncSearchEngine(
                providers=search_engine.providers,
                max_results=max_sources,
            )
        
        logger.info(
            f"EnhancedQueryProcessor initialized "
            f"(async={enable_async_search}, enhance={enable_query_enhancement}, "
            f"rank={enable_result_ranking}, cache={enable_caching})"
        )
    
    def process(self, query: str, session_id: str = "default") -> ProcessedQuery:
        """
        Process query with enhanced capabilities.
        
        Args:
            query: User query
            session_id: Session identifier
            
        Returns:
            ProcessedQuery with results and response
        """
        logger.info(f"Enhanced processing: {query} (session: {session_id})")
        
        # Check cache first
        if self.enable_caching:
            cached_result = self.query_cache.get_query(query)
            if cached_result:
                logger.info("Returning cached result")
                return cached_result
        
        # Add query to context
        self.context_manager.add_user_message(session_id, query)
        
        # Step 1: Enhance query if enabled
        search_queries = [query]
        if self.enable_query_enhancement:
            enhanced = self._enhance_query(query, session_id)
            if enhanced:
                search_queries = enhanced
                logger.info(f"Enhanced to {len(search_queries)} query variants")
        
        # Step 2: Search with best available method
        if self.enable_async_search and len(self.search_engine.providers) > 1:
            search_results = self._search_parallel(search_queries[0])
        else:
            search_results = self._search_sequential(search_queries)
        
        if not search_results:
            logger.warning(f"No search results found for: {query}")
            response = "I couldn't find any relevant information for your query."
            result = ProcessedQuery(
                query=query,
                session_id=session_id,
                response=response,
            )
            self.context_manager.add_assistant_message(session_id, response)
            return result
        
        # Step 3: Rank results if enabled
        if self.enable_result_ranking:
            search_results = self._rank_results(search_results, query)
            logger.info(f"Ranked {len(search_results)} results")
        
        # Step 4: Scrape top results
        urls_to_scrape = [r.url for r in search_results[:self.scrape_top_n]]
        scraped_content = self.web_scraper.scrape_multiple(urls_to_scrape)
        successful_scrapes = [s for s in scraped_content if s.success]
        
        # Step 5: Generate response
        response, citations = self._generate_response(
            query=query,
            session_id=session_id,
            search_results=search_results,
            scraped_content=successful_scrapes,
        )
        
        # Add response to context
        self.context_manager.add_assistant_message(
            session_id,
            response,
            metadata={"citations": citations}
        )
        
        # Create result
        result = ProcessedQuery(
            query=query,
            session_id=session_id,
            search_results=search_results,
            scraped_content=scraped_content,
            response=response,
            citations=citations,
            metadata={
                "num_results": len(search_results),
                "num_scraped": len(successful_scrapes),
                "enhanced": self.enable_query_enhancement,
                "ranked": self.enable_result_ranking,
            }
        )
        
        # Cache result
        if self.enable_caching:
            self.query_cache.set_query(query, result, ttl=3600)
        
        logger.info(f"Enhanced query processed with {len(citations)} citations")
        return result
    
    def _enhance_query(self, query: str, session_id: str) -> List[str]:
        """
        Enhance query using query enhancer.
        
        Args:
            query: Original query
            session_id: Session ID for context
            
        Returns:
            List of enhanced query variants
        """
        # Get conversation context
        history = self.context_manager.get_history(session_id, limit=3)
        context = " ".join([msg.content for msg in history[:-1]]) if len(history) > 1 else None
        
        # Enhance query
        enhanced = self.query_enhancer.enhance_for_search(query, use_variations=True)
        
        return enhanced
    
    def _search_parallel(self, query: str) -> List[Any]:
        """
        Perform parallel search across providers.
        
        Args:
            query: Search query
            
        Returns:
            Combined search results
        """
        logger.info("Executing parallel search")
        
        # Execute parallel search
        async_results = search_parallel_sync(
            self.async_search_engine,
            query,
            num_results=self.max_sources
        )
        
        # Merge results
        merged = self.async_search_engine.merge_results(
            async_results,
            max_total=self.max_sources,
            deduplicate=True
        )
        
        # Log statistics
        stats = self.async_search_engine.get_statistics(async_results)
        logger.info(
            f"Parallel search: {stats['successful']}/{stats['total_providers']} "
            f"providers, {stats['total_results']} results, "
            f"avg {stats['avg_duration']:.2f}s"
        )
        
        return merged
    
    def _search_sequential(self, queries: List[str]) -> List[Any]:
        """
        Perform sequential search with query variants.
        
        Args:
            queries: List of query variants
            
        Returns:
            Combined search results
        """
        all_results = []
        seen_urls = set()
        
        for q in queries:
            results = self.search_engine.search(q, num_results=self.max_sources)
            
            # Deduplicate
            for result in results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    all_results.append(result)
            
            # Stop if we have enough results
            if len(all_results) >= self.max_sources:
                break
        
        return all_results[:self.max_sources]
    
    def _rank_results(self, results: List[Any], query: str) -> List[Any]:
        """
        Rank results by relevance.
        
        Args:
            results: Search results
            query: Original query
            
        Returns:
            Ranked results
        """
        # Extract keywords
        keywords = self.query_enhancer.extract_keywords(query) if self.enable_query_enhancement else None
        
        # Rank results
        ranked = self.result_ranker.rank_results(results, query, keywords)
        
        # Get top results
        top_results = self.result_ranker.get_top_results(
            ranked,
            top_n=self.max_sources,
            min_score=0.2
        )
        
        return top_results
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics dictionary
        """
        if self.enable_caching:
            return self.query_cache.get_statistics()
        return {}
    
    def clear_cache(self) -> None:
        """Clear query cache."""
        if self.enable_caching:
            self.query_cache.clear()
            logger.info("Query cache cleared")
