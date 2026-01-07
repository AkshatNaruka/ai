"""
Web scraper module for content extraction.
"""

from .scraper import WebScraper, ScrapedContent
from .content_extractor import ContentExtractor

__all__ = [
    "WebScraper",
    "ScrapedContent",
    "ContentExtractor",
]
