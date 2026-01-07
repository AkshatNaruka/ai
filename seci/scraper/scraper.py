"""
Web scraper for extracting content from URLs.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# CSS selectors for elements to remove during content extraction
ELEMENTS_TO_REMOVE = ["script", "style", "nav", "footer", "header"]

# CSS selectors for finding main content
MAIN_CONTENT_SELECTORS = ["article", "main", '[role="main"]', ".content", "#content"]


@dataclass
class ScrapedContent:
    """Represents scraped web content."""
    
    url: str
    title: str
    content: str
    markdown: str
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content[:1000],  # Truncate for dict
            "markdown": self.markdown[:1000],
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error,
        }


class WebScraper:
    """
    Web scraper for extracting content from web pages.
    Uses multiple extraction strategies for best results.
    """
    
    def __init__(
        self,
        timeout: int = 10,
        max_content_length: int = 50000,
        user_agent: Optional[str] = None,
    ):
        """
        Initialize web scraper.
        
        Args:
            timeout: Request timeout in seconds
            max_content_length: Maximum content length to extract
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.html_to_text = html2text.HTML2Text()
        self.html_to_text.ignore_links = False
        self.html_to_text.ignore_images = True
        self.html_to_text.body_width = 0
        
        logger.info("WebScraper initialized")
    
    def scrape(self, url: str) -> ScrapedContent:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
        
        Returns:
            ScrapedContent object with extracted data
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Fetch the page
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "lxml")
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup)
            
            # Convert to markdown
            markdown = self.html_to_text.handle(str(soup))
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            # Truncate if too long
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length] + "..."
            if len(markdown) > self.max_content_length:
                markdown = markdown[:self.max_content_length] + "..."
            
            logger.info(f"Successfully scraped: {url} ({len(content)} chars)")
            
            return ScrapedContent(
                url=url,
                title=title,
                content=content,
                markdown=markdown,
                metadata=metadata,
                success=True,
            )
        
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return ScrapedContent(
                url=url,
                title="",
                content="",
                markdown="",
                metadata={},
                success=False,
                error=str(e),
            )
    
    def scrape_multiple(self, urls: List[str]) -> List[ScrapedContent]:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape
        
        Returns:
            List of ScrapedContent objects
        """
        results = []
        for url in urls:
            try:
                result = self.scrape(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                results.append(ScrapedContent(
                    url=url,
                    title="",
                    content="",
                    markdown="",
                    metadata={},
                    success=False,
                    error=str(e),
                ))
        return results
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try title tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()
        
        # Try og:title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        
        return "Untitled"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page."""
        # Remove script and style elements
        for script in soup(ELEMENTS_TO_REMOVE):
            script.decompose()
        
        # Try to find main content areas
        main_content = None
        for selector in MAIN_CONTENT_SELECTORS:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # Fall back to body
        if not main_content:
            main_content = soup.find("body")
        
        if not main_content:
            return ""
        
        # Extract text
        text = main_content.get_text(separator="\n", strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from page."""
        metadata = {
            "domain": urlparse(url).netloc,
        }
        
        # Extract description
        description = soup.find("meta", attrs={"name": "description"})
        if description and description.get("content"):
            metadata["description"] = description["content"]
        
        # Extract og metadata
        for prop in ["og:description", "og:image", "og:type"]:
            tag = soup.find("meta", property=prop)
            if tag and tag.get("content"):
                metadata[prop] = tag["content"]
        
        # Extract author
        author = soup.find("meta", attrs={"name": "author"})
        if author and author.get("content"):
            metadata["author"] = author["content"]
        
        return metadata
