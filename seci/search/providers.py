"""
Search provider implementations for different search engines.
"""

from typing import List, Optional
import logging
from abc import ABC, abstractmethod

from .search_engine import SearchResult

logger = logging.getLogger(__name__)


class SearchProvider(ABC):
    """Abstract base class for search providers."""
    
    @abstractmethod
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform search and return results."""
        pass


class DuckDuckGoProvider(SearchProvider):
    """DuckDuckGo search provider."""
    
    def __init__(self, region: str = "wt-wt", safesearch: str = "moderate"):
        """
        Initialize DuckDuckGo provider.
        
        Args:
            region: Region code (e.g., 'us-en', 'wt-wt' for worldwide)
            safesearch: Safe search setting ('on', 'moderate', 'off')
        """
        self.region = region
        self.safesearch = safesearch
        
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS()
            logger.info("DuckDuckGo provider initialized")
        except ImportError:
            logger.error("duckduckgo_search not installed")
            self.ddgs = None
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using DuckDuckGo."""
        if not self.ddgs:
            logger.error("DuckDuckGo not available")
            return []
        
        try:
            results = []
            # Use text search
            search_results = self.ddgs.text(
                query,
                region=self.region,
                safesearch=self.safesearch,
                max_results=num_results
            )
            
            for item in search_results:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("href", item.get("link", "")),
                    snippet=item.get("body", item.get("description", "")),
                    source="duckduckgo",
                    metadata={"raw": item}
                )
                results.append(result)
            
            return results[:num_results]
        
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []


class GoogleSearchProvider(SearchProvider):
    """Google search provider using googlesearch-python."""
    
    def __init__(self, lang: str = "en", tld: str = "com"):
        """
        Initialize Google search provider.
        
        Args:
            lang: Language code
            tld: Top-level domain
        """
        self.lang = lang
        self.tld = tld
        
        try:
            from googlesearch import search as google_search
            self.google_search = google_search
            logger.info("Google provider initialized")
        except ImportError:
            logger.error("googlesearch-python not installed")
            self.google_search = None
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Google."""
        if not self.google_search:
            logger.error("Google search not available")
            return []
        
        try:
            results = []
            search_results = self.google_search(
                query,
                num_results=num_results,
                lang=self.lang,
                advanced=True
            )
            
            for item in search_results:
                result = SearchResult(
                    title=item.title if hasattr(item, 'title') else item.url,
                    url=item.url if hasattr(item, 'url') else str(item),
                    snippet=item.description if hasattr(item, 'description') else "",
                    source="google",
                    metadata={"raw": str(item)}
                )
                results.append(result)
            
            return results[:num_results]
        
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []


class BingSearchProvider(SearchProvider):
    """Bing search provider using requests."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Bing search provider.
        
        Args:
            api_key: Bing Search API key (optional)
        """
        self.api_key = api_key
        logger.info("Bing provider initialized")
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Bing."""
        if not self.api_key:
            logger.warning("Bing API key not provided, using fallback")
            return self._fallback_search(query, num_results)
        
        try:
            import requests
            
            endpoint = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            params = {"q": query, "count": num_results, "textDecorations": True}
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("webPages", {}).get("value", []):
                result = SearchResult(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", ""),
                    source="bing",
                    metadata={"raw": item}
                )
                results.append(result)
            
            return results[:num_results]
        
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            return []
    
    def _fallback_search(self, query: str, num_results: int) -> List[SearchResult]:
        """Fallback search without API key."""
        logger.warning("Bing fallback not implemented, returning empty results")
        return []
