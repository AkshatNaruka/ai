"""
FastAPI server for Perplexity-like AI search system.
Provides REST API endpoints for search queries and conversation management.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import uuid
import os
from datetime import datetime

from seci.search import SearchEngine, DuckDuckGoProvider, GoogleSearchProvider
from seci.scraper import WebScraper
from seci.context import ContextManager
from seci.query_processor import QueryProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SECI Search API",
    description="Perplexity-like AI search system with web scraping and context",
    version="0.1.0",
)

# Get allowed origins from environment variable or use default for development
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if ALLOWED_ORIGINS == ["*"]:
    logger.warning("CORS configured with allow_origins=['*']. Configure ALLOWED_ORIGINS env var for production!")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
search_engine = None
web_scraper = None
context_manager = None
query_processor = None


# Pydantic models for API
class SearchRequest(BaseModel):
    """Request model for search queries."""
    query: str = Field(..., description="Search query", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for context")
    max_results: Optional[int] = Field(5, description="Maximum number of results", ge=1, le=20)
    scrape_content: Optional[bool] = Field(True, description="Whether to scrape full content")


class SearchResponse(BaseModel):
    """Response model for search results."""
    query: str
    session_id: str
    response: str
    citations: List[Dict[str, Any]]
    search_results: List[Dict[str, Any]]
    timestamp: str
    metadata: Dict[str, Any]


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: str
    updated_at: str


class StatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    version: str
    components: Dict[str, bool]
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global search_engine, web_scraper, context_manager, query_processor
    
    logger.info("Initializing SECI Search API...")
    
    # Initialize search engine with DuckDuckGo (no API key needed)
    search_engine = SearchEngine(max_results=10)
    search_engine.add_provider(DuckDuckGoProvider())
    
    # Try to add Google search as backup
    try:
        search_engine.add_provider(GoogleSearchProvider())
    except Exception as e:
        logger.warning(f"Google search not available: {e}")
    
    # Initialize web scraper
    web_scraper = WebScraper(timeout=10, max_content_length=50000)
    
    # Initialize context manager
    context_manager = ContextManager(max_history=20)
    
    # Initialize query processor
    query_processor = QueryProcessor(
        search_engine=search_engine,
        web_scraper=web_scraper,
        context_manager=context_manager,
        max_sources=5,
        scrape_top_n=3,
    )
    
    logger.info("SECI Search API initialized successfully")


@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint with system status."""
    return {
        "status": "online",
        "version": "0.1.0",
        "components": {
            "search_engine": search_engine is not None,
            "web_scraper": web_scraper is not None,
            "context_manager": context_manager is not None,
            "query_processor": query_processor is not None,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    if not all([search_engine, web_scraper, context_manager, query_processor]):
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Main search endpoint.
    Processes queries, searches the web, scrapes content, and generates responses.
    """
    if not query_processor:
        raise HTTPException(status_code=503, detail="Query processor not initialized")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing search request: {request.query}")
        
        # Process query
        result = query_processor.process(
            query=request.query,
            session_id=session_id,
        )
        
        return SearchResponse(
            query=result.query,
            session_id=result.session_id,
            response=result.response,
            citations=result.citations,
            search_results=[r.to_dict() for r in result.search_results[:request.max_results]],
            timestamp=result.timestamp.isoformat(),
            metadata=result.metadata,
        )
    
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/conversation/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not initialized")
    
    context = context_manager.get_context(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return ConversationHistoryResponse(
        session_id=context.session_id,
        messages=[msg.to_dict() for msg in context.messages],
        created_at=context.created_at.isoformat(),
        updated_at=context.updated_at.isoformat(),
    )


@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session."""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not initialized")
    
    context_manager.clear_context(session_id)
    return {"message": f"Conversation {session_id} cleared"}


@app.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not initialized")
    
    sessions = context_manager.get_all_sessions()
    return {
        "sessions": sessions,
        "count": len(sessions),
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
