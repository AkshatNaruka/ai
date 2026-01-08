"""
Result ranking and relevance scoring utilities.
Implements intelligent ranking of search results and scraped content.
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class RankedResult:
    """Search result with relevance score."""
    result: Any
    score: float
    ranking_factors: Dict[str, float]


class ResultRanker:
    """
    Ranks search results based on multiple relevance factors.
    Improves result quality through intelligent scoring.
    """
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        source_credibility: Optional[Dict[str, float]] = None
    ):
        """
        Initialize result ranker.
        
        Args:
            weights: Custom weights for ranking factors
            source_credibility: Source credibility scores
        """
        # Default weights for ranking factors
        self.weights = weights or {
            'keyword_match': 0.3,
            'title_relevance': 0.25,
            'snippet_relevance': 0.2,
            'source_credibility': 0.15,
            'content_length': 0.1,
        }
        
        # Source credibility scores (higher is better)
        self.source_credibility = source_credibility or {
            'wikipedia': 0.9,
            'edu': 0.85,
            'gov': 0.9,
            'org': 0.7,
            'com': 0.6,
            'default': 0.5,
        }
        
        logger.info("ResultRanker initialized")
    
    def rank_results(
        self,
        results: List[Any],
        query: str,
        keywords: Optional[List[str]] = None
    ) -> List[RankedResult]:
        """
        Rank search results by relevance.
        
        Args:
            results: List of search results
            query: Original query
            keywords: Optional extracted keywords
            
        Returns:
            Sorted list of RankedResult objects
        """
        if not results:
            return []
        
        # Extract keywords if not provided
        if keywords is None:
            keywords = self._extract_keywords(query)
        
        # Score each result
        ranked = []
        for result in results:
            score, factors = self._score_result(result, query, keywords)
            ranked.append(RankedResult(
                result=result,
                score=score,
                ranking_factors=factors
            ))
        
        # Sort by score (descending)
        ranked.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Ranked {len(ranked)} results")
        return ranked
    
    def _score_result(
        self,
        result: Any,
        query: str,
        keywords: List[str]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate relevance score for a result.
        
        Args:
            result: Search result
            query: Query string
            keywords: Query keywords
            
        Returns:
            Tuple of (total_score, factor_scores)
        """
        factors = {}
        
        # Get result fields
        title = getattr(result, 'title', '').lower()
        snippet = getattr(result, 'snippet', '').lower()
        url = getattr(result, 'url', '').lower()
        
        # Factor 1: Keyword match score
        factors['keyword_match'] = self._keyword_match_score(
            title + ' ' + snippet, keywords
        )
        
        # Factor 2: Title relevance
        factors['title_relevance'] = self._text_relevance_score(title, query.lower())
        
        # Factor 3: Snippet relevance
        factors['snippet_relevance'] = self._text_relevance_score(snippet, query.lower())
        
        # Factor 4: Source credibility
        factors['source_credibility'] = self._source_credibility_score(url)
        
        # Factor 5: Content length indicator
        factors['content_length'] = self._content_length_score(snippet)
        
        # Calculate weighted total score
        total_score = sum(
            factors[factor] * self.weights.get(factor, 0.0)
            for factor in factors
        )
        
        return total_score, factors
    
    def _keyword_match_score(self, text: str, keywords: List[str]) -> float:
        """
        Calculate keyword match score.
        
        Args:
            text: Text to search
            keywords: Keywords to match
            
        Returns:
            Score between 0 and 1
        """
        if not keywords:
            return 0.5
        
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        
        return min(matches / len(keywords), 1.0)
    
    def _text_relevance_score(self, text: str, query: str) -> float:
        """
        Calculate text relevance to query.
        
        Args:
            text: Text to score
            query: Query string
            
        Returns:
            Score between 0 and 1
        """
        if not text or not query:
            return 0.0
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Exact match bonus
        if query_lower in text_lower:
            return 1.0
        
        # Count word overlaps
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        text_words = set(re.findall(r'\b\w+\b', text_lower))
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(text_words))
        return overlap / len(query_words)
    
    def _source_credibility_score(self, url: str) -> float:
        """
        Calculate source credibility score based on URL.
        
        Args:
            url: URL string
            
        Returns:
            Score between 0 and 1
        """
        url_lower = url.lower()
        
        # Check for special sources
        if 'wikipedia' in url_lower:
            return self.source_credibility['wikipedia']
        elif '.edu' in url_lower:
            return self.source_credibility['edu']
        elif '.gov' in url_lower:
            return self.source_credibility['gov']
        elif '.org' in url_lower:
            return self.source_credibility['org']
        elif '.com' in url_lower:
            return self.source_credibility['com']
        
        return self.source_credibility['default']
    
    def _content_length_score(self, text: str) -> float:
        """
        Calculate content length quality score.
        Prefer moderate length (not too short, not too long).
        
        Args:
            text: Text to score
            
        Returns:
            Score between 0 and 1
        """
        if not text:
            return 0.0
        
        length = len(text)
        
        # Optimal range: 100-500 characters
        if 100 <= length <= 500:
            return 1.0
        elif length < 100:
            return length / 100.0
        else:  # length > 500
            return max(0.5, 1.0 - (length - 500) / 1000.0)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from query.
        
        Args:
            query: Query string
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter common words
        stopwords = {'what', 'is', 'are', 'the', 'a', 'an', 'how', 'why', 'when', 'where'}
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        return keywords
    
    def get_top_results(
        self,
        ranked_results: List[RankedResult],
        top_n: int = 5,
        min_score: float = 0.3
    ) -> List[Any]:
        """
        Get top N results with minimum score threshold.
        
        Args:
            ranked_results: Ranked results
            top_n: Number of results to return
            min_score: Minimum score threshold
            
        Returns:
            List of top results
        """
        filtered = [r for r in ranked_results if r.score >= min_score]
        top = filtered[:top_n]
        
        logger.info(f"Returning {len(top)} top results (filtered from {len(ranked_results)})")
        return [r.result for r in top]
