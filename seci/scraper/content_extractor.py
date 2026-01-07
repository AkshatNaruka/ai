"""
Advanced content extraction using trafilatura.
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    Advanced content extractor using trafilatura library.
    Better at extracting main article content and filtering noise.
    """
    
    def __init__(self):
        """Initialize content extractor."""
        try:
            import trafilatura
            self.trafilatura = trafilatura
            logger.info("ContentExtractor initialized with trafilatura")
        except ImportError:
            logger.warning("trafilatura not installed, using basic extraction")
            self.trafilatura = None
    
    def extract(
        self,
        html: str,
        url: Optional[str] = None,
        output_format: str = "text",
    ) -> Optional[str]:
        """
        Extract main content from HTML.
        
        Args:
            html: HTML content
            url: Source URL (optional, helps with extraction)
            output_format: Output format ('text', 'markdown', 'xml')
        
        Returns:
            Extracted content or None if extraction fails
        """
        if not self.trafilatura:
            logger.warning("trafilatura not available")
            return None
        
        try:
            content = self.trafilatura.extract(
                html,
                url=url,
                output_format=output_format,
                include_comments=False,
                include_tables=True,
            )
            return content
        
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return None
    
    def extract_metadata(self, html: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract metadata from HTML.
        
        Args:
            html: HTML content
            url: Source URL
        
        Returns:
            Dictionary with metadata
        """
        if not self.trafilatura:
            return {}
        
        try:
            metadata = self.trafilatura.extract_metadata(html, url=url)
            if metadata:
                return {
                    "title": metadata.title,
                    "author": metadata.author,
                    "date": metadata.date,
                    "description": metadata.description,
                    "sitename": metadata.sitename,
                    "categories": metadata.categories,
                    "tags": metadata.tags,
                }
            return {}
        
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
