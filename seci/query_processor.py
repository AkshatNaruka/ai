"""
Query processor that integrates search, scraping, and AI response generation.
"""

from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass, field
from datetime import datetime

from ..search import SearchEngine, SearchResult
from ..scraper import WebScraper, ScrapedContent
from ..context import ContextManager

logger = logging.getLogger(__name__)


@dataclass
class ProcessedQuery:
    """Represents a processed query with search results and generated response."""
    
    query: str
    session_id: str
    search_results: List[SearchResult] = field(default_factory=list)
    scraped_content: List[ScrapedContent] = field(default_factory=list)
    response: str = ""
    citations: List[Dict[str, str]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "query": self.query,
            "session_id": self.session_id,
            "search_results": [r.to_dict() for r in self.search_results],
            "response": self.response,
            "citations": self.citations,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class QueryProcessor:
    """
    Main query processor that coordinates search, scraping, and response generation.
    This is the core component that makes the system behave like Perplexity.
    """
    
    def __init__(
        self,
        search_engine: SearchEngine,
        web_scraper: WebScraper,
        context_manager: ContextManager,
        model: Optional[Any] = None,
        max_sources: int = 5,
        scrape_top_n: int = 3,
    ):
        """
        Initialize query processor.
        
        Args:
            search_engine: Search engine instance
            web_scraper: Web scraper instance
            context_manager: Context manager instance
            model: AI model for response generation (optional)
            max_sources: Maximum search results to consider
            scrape_top_n: Number of top results to scrape
        """
        self.search_engine = search_engine
        self.web_scraper = web_scraper
        self.context_manager = context_manager
        self.model = model
        self.max_sources = max_sources
        self.scrape_top_n = scrape_top_n
        
        logger.info("QueryProcessor initialized")
    
    def process(self, query: str, session_id: str = "default") -> ProcessedQuery:
        """
        Process a query: search, scrape, and generate response.
        
        Args:
            query: User query
            session_id: Session identifier for context
        
        Returns:
            ProcessedQuery with results and response
        """
        logger.info(f"Processing query: {query} (session: {session_id})")
        
        # Add query to context
        self.context_manager.add_user_message(session_id, query)
        
        # Step 1: Search for relevant information
        search_results = self.search_engine.search(query, num_results=self.max_sources)
        
        if not search_results:
            logger.warning(f"No search results found for: {query}")
            response = "I couldn't find any relevant information for your query."
            self.context_manager.add_assistant_message(session_id, response)
            return ProcessedQuery(
                query=query,
                session_id=session_id,
                response=response,
            )
        
        # Step 2: Scrape top results for detailed content
        urls_to_scrape = [r.url for r in search_results[:self.scrape_top_n]]
        scraped_content = self.web_scraper.scrape_multiple(urls_to_scrape)
        
        # Filter successful scrapes
        successful_scrapes = [s for s in scraped_content if s.success]
        
        # Step 3: Generate response using search results and scraped content
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
        
        logger.info(f"Query processed with {len(citations)} citations")
        
        return ProcessedQuery(
            query=query,
            session_id=session_id,
            search_results=search_results,
            scraped_content=scraped_content,
            response=response,
            citations=citations,
            metadata={
                "num_results": len(search_results),
                "num_scraped": len(successful_scrapes),
            }
        )
    
    def _generate_response(
        self,
        query: str,
        session_id: str,
        search_results: List[SearchResult],
        scraped_content: List[ScrapedContent],
    ) -> tuple[str, List[Dict[str, str]]]:
        """
        Generate response based on search results and scraped content.
        
        Args:
            query: User query
            session_id: Session ID
            search_results: Search results
            scraped_content: Scraped content
        
        Returns:
            Tuple of (response, citations)
        """
        # Build context from search results and scraped content
        context_parts = []
        citations = []
        
        # Add search result snippets
        for i, result in enumerate(search_results[:self.max_sources]):
            context_parts.append(f"[{i+1}] {result.title}: {result.snippet}")
            citations.append({
                "number": i + 1,
                "title": result.title,
                "url": result.url,
                "source": result.source,
            })
        
        # Add scraped content (prioritize over snippets)
        for i, content in enumerate(scraped_content):
            if i < len(context_parts):
                # Replace snippet with full content
                context_parts[i] = f"[{i+1}] {content.title}: {content.content[:500]}"
        
        context_text = "\n\n".join(context_parts)
        
        # Get conversation history
        history = self.context_manager.get_history(session_id, limit=5)
        history_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in history[:-1]  # Exclude current query
        ])
        
        # Generate response
        if self.model:
            # Use AI model to generate response
            response = self._generate_with_model(query, context_text, history_text)
        else:
            # Fallback: simple summarization
            response = self._generate_fallback_response(query, search_results, scraped_content)
        
        return response, citations
    
    def _generate_with_model(
        self,
        query: str,
        context: str,
        history: str,
    ) -> str:
        """Generate response using AI model."""
        # This would integrate with the SECI model
        # For now, return a placeholder
        logger.info("Generating response with AI model")
        
        prompt = f"""Based on the following information, answer the user's question.

Previous conversation:
{history}

User question: {query}

Search results and sources:
{context}

Provide a comprehensive answer with references to the sources [1], [2], etc."""
        
        # TODO: Integrate with SECI model for actual generation
        # For now, return structured response
        return f"Based on the search results, here's what I found about '{query}':\n\n{context[:500]}...\n\nSources: [1], [2], [3]"
    
    def _generate_fallback_response(
        self,
        query: str,
        search_results: List[SearchResult],
        scraped_content: List[ScrapedContent],
    ) -> str:
        """Generate fallback response without model."""
        logger.info("Generating fallback response")
        
        # Build response from search results
        response_parts = [f"Based on the search results for '{query}':\n"]
        
        for i, result in enumerate(search_results[:3]):
            response_parts.append(f"\n[{i+1}] {result.title}")
            response_parts.append(f"{result.snippet}")
            if i < len(scraped_content) and scraped_content[i].success:
                # Add excerpt from scraped content
                excerpt = scraped_content[i].content[:200]
                response_parts.append(f"Additional context: {excerpt}...")
        
        response_parts.append("\n\nSources:")
        for i, result in enumerate(search_results[:3]):
            response_parts.append(f"[{i+1}] {result.url}")
        
        return "\n".join(response_parts)
