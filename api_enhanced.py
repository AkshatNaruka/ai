"""
Enhanced FastAPI server with advanced capabilities.
Demonstrates smarter, better, and faster features.
"""

from fastapi import FastAPI, HTTPException, Query as QueryParam
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
from seci.enhanced_processor import EnhancedQueryProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SECI Enhanced Search API",
    description="Enhanced Perplexity-like AI search with smarter, better, and faster features",
    version="0.2.0",
)

# Get allowed origins from environment variable
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
class EnhancedSearchRequest(BaseModel):
    """Request model for enhanced search queries."""
    query: str = Field(..., description="Search query", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for context")
    max_results: Optional[int] = Field(5, description="Maximum number of results", ge=1, le=20)
    scrape_content: Optional[bool] = Field(True, description="Whether to scrape full content")
    use_async: Optional[bool] = Field(True, description="Use async parallel search")
    enhance_query: Optional[bool] = Field(True, description="Enable query enhancement")
    rank_results: Optional[bool] = Field(True, description="Enable result ranking")


class EnhancedSearchResponse(BaseModel):
    """Response model for enhanced search results."""
    query: str
    session_id: str
    response: str
    citations: List[Dict[str, Any]]
    search_results: List[Dict[str, Any]]
    timestamp: str
    metadata: Dict[str, Any]
    performance: Dict[str, Any]


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""
    cache_stats: Dict[str, Any]
    timestamp: str


class StatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    version: str
    features: Dict[str, bool]
    components: Dict[str, bool]
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize enhanced components on startup."""
    global search_engine, web_scraper, context_manager, query_processor
    
    logger.info("Initializing Enhanced SECI Search API...")
    
    # Initialize search engine with multiple providers
    search_engine = SearchEngine(max_results=10)
    search_engine.add_provider(DuckDuckGoProvider())
    
    # Try to add Google search as backup
    try:
        search_engine.add_provider(GoogleSearchProvider())
        logger.info("Google search provider added")
    except Exception as e:
        logger.warning(f"Google search not available: {e}")
    
    # Initialize web scraper
    web_scraper = WebScraper(timeout=10, max_content_length=50000)
    
    # Initialize context manager
    context_manager = ContextManager(max_history=20)
    
    # Initialize ENHANCED query processor
    query_processor = EnhancedQueryProcessor(
        search_engine=search_engine,
        web_scraper=web_scraper,
        context_manager=context_manager,
        max_sources=5,
        scrape_top_n=3,
        enable_async_search=True,
        enable_query_enhancement=True,
        enable_result_ranking=True,
        enable_caching=True,
        cache_ttl=3600,
    )
    
    logger.info("Enhanced SECI Search API initialized with advanced features")


@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint with enhanced system status."""
    return {
        "status": "online",
        "version": "0.2.0",
        "features": {
            "async_search": True,
            "query_enhancement": True,
            "result_ranking": True,
            "intelligent_caching": True,
            "parallel_providers": len(search_engine.providers) > 1 if search_engine else False,
        },
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


@app.post("/search", response_model=EnhancedSearchResponse)
async def search(request: EnhancedSearchRequest):
    """
    Enhanced search endpoint with advanced features.
    
    Supports:
    - Async parallel search across multiple providers
    - Query enhancement and expansion
    - Intelligent result ranking
    - Smart caching
    """
    if not query_processor:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    logger.info(f"Enhanced search request: {request.query} (session: {session_id})")
    
    start_time = datetime.now()
    
    try:
        # Process query with enhanced features
        result = query_processor.process(
            query=request.query,
            session_id=session_id,
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "query": result.query,
            "session_id": result.session_id,
            "response": result.response,
            "citations": result.citations,
            "search_results": [r.to_dict() for r in result.search_results],
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata,
            "performance": {
                "processing_time_seconds": processing_time,
                "num_results": len(result.search_results),
                "num_citations": len(result.citations),
                "features_used": {
                    "async_search": request.use_async,
                    "query_enhancement": request.enhance_query,
                    "result_ranking": request.rank_results,
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/cache/stats", response_model=CacheStatsResponse)
async def cache_stats():
    """Get cache statistics."""
    if not query_processor:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    stats = query_processor.get_cache_statistics()
    
    return {
        "cache_stats": stats,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/cache/clear")
async def clear_cache():
    """Clear query cache."""
    if not query_processor:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    query_processor.clear_cache()
    
    return {
        "status": "success",
        "message": "Cache cleared",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    history = context_manager.get_history(session_id)
    
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in history
        ],
        "message_count": len(history),
    }


@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session."""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context_manager.clear_history(session_id)
    
    return {
        "status": "success",
        "message": f"Conversation {session_id} cleared",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    sessions = context_manager.list_sessions()
    
    return {
        "sessions": sessions,
        "count": len(sessions),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/features")
async def list_features():
    """List all enhanced features."""
    return {
        "features": {
            "async_parallel_search": {
                "description": "Search multiple providers simultaneously for faster results",
                "status": "enabled",
            },
            "query_enhancement": {
                "description": "Expand and reformulate queries for better results",
                "status": "enabled",
            },
            "result_ranking": {
                "description": "Intelligent ranking based on relevance and credibility",
                "status": "enabled",
            },
            "intelligent_caching": {
                "description": "Multi-level caching with semantic similarity",
                "status": "enabled",
            },
            "conversation_context": {
                "description": "Maintain conversation history across queries",
                "status": "enabled",
            },
        },
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
