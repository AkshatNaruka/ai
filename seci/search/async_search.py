"""
Async search engine for parallel search across multiple providers.
Dramatically improves search speed through concurrent requests.
"""

import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class AsyncSearchResult:
    """Result from async search with timing information."""
    results: List[Any]
    provider: str
    duration: float
    success: bool
    error: Optional[str] = None


class AsyncSearchEngine:
    """
    Async search engine that performs parallel searches across multiple providers.
    Provides significant speed improvements over sequential searching.
    """
    
    def __init__(
        self,
        providers: Optional[List[Any]] = None,
        max_results: int = 10,
        timeout: int = 10,
        max_concurrent: int = 5,
    ):
        """
        Initialize async search engine.
        
        Args:
            providers: List of search provider instances
            max_results: Maximum results per provider
            timeout: Timeout per provider in seconds
            max_concurrent: Maximum concurrent searches
        """
        self.providers = providers or []
        self.max_results = max_results
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        
        logger.info(f"AsyncSearchEngine initialized with {len(self.providers)} providers")
    
    def add_provider(self, provider: Any) -> None:
        """Add a search provider."""
        self.providers.append(provider)
        logger.info(f"Added provider: {provider.__class__.__name__}")
    
    async def search_parallel(
        self,
        query: str,
        num_results: Optional[int] = None,
        provider_names: Optional[List[str]] = None,
    ) -> List[AsyncSearchResult]:
        """
        Search across multiple providers in parallel.
        
        Args:
            query: Search query
            num_results: Number of results per provider
            provider_names: Specific providers to use (None = all)
            
        Returns:
            List of AsyncSearchResult from all providers
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        num_results = num_results or self.max_results
        
        # Select providers
        if provider_names:
            providers = [p for p in self.providers 
                        if p.__class__.__name__ in provider_names]
        else:
            providers = self.providers
        
        if not providers:
            logger.warning("No providers available for search")
            return []
        
        # Create search tasks
        tasks = []
        for provider in providers:
            task = self._search_provider_async(provider, query, num_results)
            tasks.append(task)
        
        # Execute all searches concurrently
        logger.info(f"Starting parallel search across {len(tasks)} providers")
        start_time = time.time()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        logger.info(f"Parallel search completed in {total_time:.2f}s")
        
        # Process results
        search_results = []
        for result in results:
            if isinstance(result, AsyncSearchResult):
                search_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Search task failed: {result}")
        
        return search_results
    
    async def _search_provider_async(
        self,
        provider: Any,
        query: str,
        num_results: int,
    ) -> AsyncSearchResult:
        """
        Execute search for a single provider asynchronously.
        
        Args:
            provider: Search provider instance
            query: Query string
            num_results: Number of results
            
        Returns:
            AsyncSearchResult
        """
        provider_name = provider.__class__.__name__
        start_time = time.time()
        
        try:
            # Run sync provider.search in executor to avoid blocking
            loop = asyncio.get_event_loop()
            results = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    provider.search,
                    query,
                    num_results
                ),
                timeout=self.timeout
            )
            
            duration = time.time() - start_time
            
            logger.info(f"{provider_name}: found {len(results)} results in {duration:.2f}s")
            
            return AsyncSearchResult(
                results=results,
                provider=provider_name,
                duration=duration,
                success=True
            )
        
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.warning(f"{provider_name}: timeout after {duration:.2f}s")
            return AsyncSearchResult(
                results=[],
                provider=provider_name,
                duration=duration,
                success=False,
                error="timeout"
            )
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{provider_name}: error - {e}")
            return AsyncSearchResult(
                results=[],
                provider=provider_name,
                duration=duration,
                success=False,
                error=str(e)
            )
    
    def merge_results(
        self,
        async_results: List[AsyncSearchResult],
        max_total: Optional[int] = None,
        deduplicate: bool = True,
    ) -> List[Any]:
        """
        Merge results from multiple providers.
        
        Args:
            async_results: Results from parallel searches
            max_total: Maximum total results to return
            deduplicate: Remove duplicate URLs
            
        Returns:
            Merged list of search results
        """
        max_total = max_total or self.max_results
        
        # Collect all successful results
        all_results = []
        for async_result in async_results:
            if async_result.success:
                all_results.extend(async_result.results)
        
        # Deduplicate by URL if requested
        if deduplicate:
            seen_urls = set()
            unique_results = []
            for result in all_results:
                url = getattr(result, 'url', None)
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
                elif not url:
                    unique_results.append(result)
            
            all_results = unique_results
        
        # Limit total results
        merged = all_results[:max_total]
        
        logger.info(f"Merged {len(merged)} results from {len(async_results)} providers")
        return merged
    
    def get_fastest_result(
        self,
        async_results: List[AsyncSearchResult]
    ) -> Optional[AsyncSearchResult]:
        """
        Get the fastest successful result.
        
        Args:
            async_results: Results from parallel searches
            
        Returns:
            Fastest successful result or None
        """
        successful = [r for r in async_results if r.success and r.results]
        if not successful:
            return None
        
        fastest = min(successful, key=lambda r: r.duration)
        logger.info(f"Fastest result: {fastest.provider} ({fastest.duration:.2f}s)")
        return fastest
    
    def get_statistics(
        self,
        async_results: List[AsyncSearchResult]
    ) -> Dict[str, Any]:
        """
        Get statistics about parallel search performance.
        
        Args:
            async_results: Results from parallel searches
            
        Returns:
            Statistics dictionary
        """
        successful = [r for r in async_results if r.success]
        failed = [r for r in async_results if not r.success]
        
        total_results = sum(len(r.results) for r in successful)
        avg_duration = sum(r.duration for r in async_results) / len(async_results) if async_results else 0
        
        stats = {
            'total_providers': len(async_results),
            'successful': len(successful),
            'failed': len(failed),
            'total_results': total_results,
            'avg_duration': avg_duration,
            'providers': {
                r.provider: {
                    'results': len(r.results),
                    'duration': r.duration,
                    'success': r.success,
                    'error': r.error,
                }
                for r in async_results
            }
        }
        
        return stats


# Sync wrapper for backward compatibility
def search_parallel_sync(
    engine: AsyncSearchEngine,
    query: str,
    num_results: Optional[int] = None,
    provider_names: Optional[List[str]] = None,
) -> List[AsyncSearchResult]:
    """
    Synchronous wrapper for parallel search.
    
    Args:
        engine: AsyncSearchEngine instance
        query: Search query
        num_results: Number of results
        provider_names: Provider names to use
        
    Returns:
        List of AsyncSearchResult
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            engine.search_parallel(query, num_results, provider_names)
        )
    finally:
        loop.close()
