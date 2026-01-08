"""
SECI - Self-Evolving Compact Intelligence
A modular framework for efficient continual learning with compact transformers.
Now with Perplexity-like search capabilities!
Enhanced with smarter, better, and faster features!
"""

__version__ = "0.1.0"

from .core.model import CompactTransformer
from .core.teacher import TeacherModel
from .memory.external_memory import ExternalMemory
from .distillation.distiller import KnowledgeDistiller
from .replay.buffer import ReplayBuffer
from .config.config import SECIConfig

# Search and web capabilities
from .search import SearchEngine, SearchResult, AsyncSearchEngine, AsyncSearchResult, search_parallel_sync
from .scraper import WebScraper, ScrapedContent
from .context import ContextManager, ConversationContext
from .query_processor import QueryProcessor
from .enhanced_processor import EnhancedQueryProcessor

# Enhanced utilities
from .utils import QueryEnhancer, ResultRanker, IntelligentCache, QueryCache

__all__ = [
    "CompactTransformer",
    "TeacherModel",
    "ExternalMemory",
    "KnowledgeDistiller",
    "ReplayBuffer",
    "SECIConfig",
    "SearchEngine",
    "SearchResult",
    "AsyncSearchEngine",
    "AsyncSearchResult",
    "search_parallel_sync",
    "WebScraper",
    "ScrapedContent",
    "ContextManager",
    "ConversationContext",
    "QueryProcessor",
    "EnhancedQueryProcessor",
    "QueryEnhancer",
    "ResultRanker",
    "IntelligentCache",
    "QueryCache",
]
