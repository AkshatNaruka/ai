"""
SECI - Self-Evolving Compact Intelligence
A modular framework for efficient continual learning with compact transformers.
Now with Perplexity-like search capabilities!
"""

__version__ = "0.1.0"

from .core.model import CompactTransformer
from .core.teacher import TeacherModel
from .memory.external_memory import ExternalMemory
from .distillation.distiller import KnowledgeDistiller
from .replay.buffer import ReplayBuffer
from .config.config import SECIConfig

# Search and web capabilities
from .search import SearchEngine, SearchResult
from .scraper import WebScraper, ScrapedContent
from .context import ContextManager, ConversationContext
from .query_processor import QueryProcessor

__all__ = [
    "CompactTransformer",
    "TeacherModel",
    "ExternalMemory",
    "KnowledgeDistiller",
    "ReplayBuffer",
    "SECIConfig",
    "SearchEngine",
    "SearchResult",
    "WebScraper",
    "ScrapedContent",
    "ContextManager",
    "ConversationContext",
    "QueryProcessor",
]
