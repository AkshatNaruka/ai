"""
Main search engine interface for querying multiple providers.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a single search result."""
    
    title: str
    url: str
    snippet: str
    source: str  # The search provider used
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class SearchEngine:
    """
    Main search engine that coordinates multiple search providers.
    Provides unified interface for web search across different providers.
    """
    
    def __init__(
        self,
        providers: Optional[List[Any]] = None,
        max_results: int = 10,
        timeout: int = 10,
        cache_ttl: int = 3600,
    ):
        """
        Initialize search engine.
        
        Args:
            providers: List of search provider instances
            max_results: Maximum number of results to return
            timeout: Timeout for search requests in seconds
            cache_ttl: Cache time-to-live in seconds
        """
        self.providers = providers or []
        self.max_results = max_results
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache = {}
        
        logger.info(f"Initialized SearchEngine with {len(self.providers)} providers")
    
    def add_provider(self, provider: Any) -> None:
        """Add a search provider."""
        self.providers.append(provider)
        logger.info(f"Added search provider: {provider.__class__.__name__}")
    
    def search(
        self,
        query: str,
        num_results: Optional[int] = None,
        provider_name: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Perform search across available providers.
        
        Args:
            query: Search query string
            num_results: Number of results to return (overrides max_results)
            provider_name: Specific provider to use (None = use first available)
        
        Returns:
            List of SearchResult objects
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        num_results = num_results or self.max_results
        
        # Check cache
        cache_key = f"{query}:{num_results}:{provider_name}"
        if cache_key in self._cache:
            logger.info(f"Cache hit for query: {query}")
            return self._cache[cache_key]
        
        # Select provider
        if provider_name:
            provider = self._get_provider_by_name(provider_name)
            if not provider:
                logger.error(f"Provider '{provider_name}' not found")
                return []
        else:
            if not self.providers:
                logger.error("No search providers available")
                return []
            provider = self.providers[0]
        
        # Perform search
        try:
            logger.info(f"Searching with {provider.__class__.__name__}: {query}")
            results = provider.search(query, num_results=num_results)
            
            # Cache results
            self._cache[cache_key] = results
            
            logger.info(f"Found {len(results)} results for: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _get_provider_by_name(self, name: str) -> Optional[Any]:
        """Get provider by name."""
        for provider in self.providers:
            if provider.__class__.__name__.lower().startswith(name.lower()):
                return provider
        return None
    
    def clear_cache(self) -> None:
        """Clear search cache."""
        self._cache.clear()
        logger.info("Search cache cleared")
