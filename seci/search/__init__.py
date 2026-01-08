"""
Search module for web search integration.
Supports multiple search providers: Google, Bing, DuckDuckGo.
"""

from .search_engine import SearchEngine, SearchResult
from .providers import GoogleSearchProvider, DuckDuckGoProvider, BingSearchProvider
from .async_search import AsyncSearchEngine, AsyncSearchResult, search_parallel_sync

__all__ = [
    "SearchEngine",
    "SearchResult",
    "GoogleSearchProvider",
    "DuckDuckGoProvider",
    "BingSearchProvider",
    "AsyncSearchEngine",
    "AsyncSearchResult",
    "search_parallel_sync",
]
