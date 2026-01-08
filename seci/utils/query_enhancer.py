"""
Query enhancement utilities for smarter search capabilities.
Includes query expansion, reformulation, and semantic analysis.
"""

import re
from typing import List, Dict, Set, Optional
import logging

logger = logging.getLogger(__name__)


class QueryEnhancer:
    """
    Enhances queries for better search results through expansion,
    reformulation, and semantic analysis.
    """
    
    def __init__(self):
        """Initialize query enhancer."""
        # Common question words for query analysis
        self.question_words = {'what', 'when', 'where', 'who', 'why', 'how', 'which'}
        
        # Stopwords to filter (minimal set)
        self.stopwords = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        
        logger.info("QueryEnhancer initialized")
    
    def expand_query(self, query: str, max_variations: int = 3) -> List[str]:
        """
        Generate query variations for broader search coverage.
        
        Args:
            query: Original query
            max_variations: Maximum number of variations to generate
            
        Returns:
            List of query variations including original
        """
        variations = [query]
        
        # Extract question type and keywords
        query_lower = query.lower().strip()
        
        # Generate variations based on query type
        if any(word in query_lower for word in ['what is', 'what are']):
            # Definition query
            base = re.sub(r'what (is|are)\s+', '', query_lower, flags=re.IGNORECASE)
            variations.extend([
                f"{base} definition",
                f"{base} explanation",
                f"define {base}"
            ][:max_variations])
        
        elif any(word in query_lower for word in ['how to', 'how do']):
            # How-to query
            base = re.sub(r'how (to|do|does)\s+', '', query_lower, flags=re.IGNORECASE)
            variations.extend([
                f"{base} tutorial",
                f"{base} guide",
                f"steps to {base}"
            ][:max_variations])
        
        elif query_lower.startswith('why'):
            # Reason query
            base = re.sub(r'why\s+', '', query_lower, flags=re.IGNORECASE)
            variations.extend([
                f"{base} reason",
                f"{base} explanation",
                f"cause of {base}"
            ][:max_variations])
        
        else:
            # General query - add context keywords
            variations.extend([
                f"{query} overview",
                f"{query} information",
                f"{query} facts"
            ][:max_variations])
        
        # Return unique variations
        unique_variations = list(dict.fromkeys(variations))
        logger.info(f"Generated {len(unique_variations)} query variations")
        return unique_variations[:max_variations + 1]
    
    def extract_keywords(self, query: str, max_keywords: int = 5) -> List[str]:
        """
        Extract important keywords from query.
        
        Args:
            query: Query string
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Clean and tokenize
        query_lower = query.lower()
        words = re.findall(r'\b\w+\b', query_lower)
        
        # Filter stopwords and short words
        keywords = [
            word for word in words 
            if word not in self.stopwords 
            and word not in self.question_words
            and len(word) > 2
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for word in keywords:
            if word not in seen:
                seen.add(word)
                unique_keywords.append(word)
        
        return unique_keywords[:max_keywords]
    
    def reformulate_query(self, query: str, context: Optional[str] = None) -> str:
        """
        Reformulate query for better search results.
        
        Args:
            query: Original query
            context: Optional context from conversation
            
        Returns:
            Reformulated query
        """
        query = query.strip()
        
        # If query is very short, try to expand it
        if len(query.split()) <= 2:
            keywords = self.extract_keywords(query)
            if keywords:
                return ' '.join(keywords)
        
        # If query has context, incorporate it
        if context:
            context_keywords = self.extract_keywords(context, max_keywords=2)
            query_keywords = self.extract_keywords(query)
            
            # Combine context and query keywords
            combined = context_keywords + query_keywords
            return ' '.join(dict.fromkeys(combined))  # Remove duplicates
        
        return query
    
    def analyze_query_intent(self, query: str) -> Dict[str, any]:
        """
        Analyze query to determine intent and characteristics.
        
        Args:
            query: Query string
            
        Returns:
            Dictionary with intent analysis
        """
        query_lower = query.lower().strip()
        
        # Determine query type
        query_type = 'general'
        if any(word in query_lower for word in ['what is', 'what are', 'define']):
            query_type = 'definition'
        elif any(word in query_lower for word in ['how to', 'how do', 'how does']):
            query_type = 'howto'
        elif query_lower.startswith('why'):
            query_type = 'explanation'
        elif query_lower.startswith('when'):
            query_type = 'temporal'
        elif query_lower.startswith('where'):
            query_type = 'location'
        
        # Extract keywords
        keywords = self.extract_keywords(query)
        
        # Determine if query is conversational
        is_conversational = len(query.split()) > 10 or '?' in query
        
        # Determine complexity
        complexity = 'simple' if len(keywords) <= 2 else 'moderate' if len(keywords) <= 4 else 'complex'
        
        return {
            'type': query_type,
            'keywords': keywords,
            'is_conversational': is_conversational,
            'complexity': complexity,
            'word_count': len(query.split()),
        }
    
    def enhance_for_search(self, query: str, use_variations: bool = False) -> List[str]:
        """
        Enhance query for optimal search results.
        
        Args:
            query: Original query
            use_variations: Whether to generate multiple variations
            
        Returns:
            List of enhanced queries
        """
        # Analyze query
        analysis = self.analyze_query_intent(query)
        
        # Start with reformulated query
        enhanced = [self.reformulate_query(query)]
        
        # Add variations if requested
        if use_variations:
            variations = self.expand_query(query, max_variations=2)
            enhanced.extend([v for v in variations if v not in enhanced])
        
        logger.info(f"Enhanced query: {len(enhanced)} variants generated")
        return enhanced
