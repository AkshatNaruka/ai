"""
External Memory system for storing and retrieving learned representations.
Uses key-value memory with attention-based retrieval.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional, Dict
import math


class ExternalMemory(nn.Module):
    """
    External memory bank for storing and retrieving representations.
    Implements attention-based memory with write and read operations.
    """
    
    def __init__(self, memory_size: int, embedding_dim: int, 
                 num_memory_heads: int = 4, memory_update_rate: float = 0.01,
                 retrieval_top_k: int = 5):
        """
        Initialize external memory.
        
        Args:
            memory_size: Number of memory slots
            embedding_dim: Dimension of memory embeddings
            num_memory_heads: Number of attention heads for retrieval
            memory_update_rate: Learning rate for memory updates
            retrieval_top_k: Top-k memories to retrieve
        """
        super().__init__()
        
        self.memory_size = memory_size
        self.embedding_dim = embedding_dim
        self.num_memory_heads = num_memory_heads
        self.memory_update_rate = memory_update_rate
        self.retrieval_top_k = min(retrieval_top_k, memory_size)
        
        # Memory banks (key-value store)
        self.register_buffer('memory_keys', torch.randn(memory_size, embedding_dim))
        self.register_buffer('memory_values', torch.randn(memory_size, embedding_dim))
        self.register_buffer('memory_age', torch.zeros(memory_size))
        self.register_buffer('memory_usage', torch.zeros(memory_size))
        
        # Normalize initial memory
        self.memory_keys = F.normalize(self.memory_keys, dim=-1)
        self.memory_values = F.normalize(self.memory_values, dim=-1)
        
        # Query projection for retrieval
        self.query_proj = nn.Linear(embedding_dim, embedding_dim)
        
        # Output projection
        self.output_proj = nn.Linear(embedding_dim, embedding_dim)
        
        self.scale = (embedding_dim // num_memory_heads) ** -0.5
        self._step = 0
    
    def _compute_similarity(self, query: torch.Tensor) -> torch.Tensor:
        """
        Compute similarity between query and memory keys.
        
        Args:
            query: Query tensor of shape (batch_size, embedding_dim)
            
        Returns:
            Similarity scores of shape (batch_size, memory_size)
        """
        # Normalize query
        query = F.normalize(query, dim=-1)
        
        # Cosine similarity
        similarity = torch.matmul(query, self.memory_keys.T)
        
        return similarity
    
    def read(self, query: torch.Tensor, return_attention: bool = False) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Read from memory using attention mechanism.
        
        Args:
            query: Query tensor of shape (batch_size, seq_len, embedding_dim)
            return_attention: Whether to return attention weights
            
        Returns:
            Retrieved memory values and optionally attention weights
        """
        batch_size, seq_len, _ = query.shape
        
        # Project query
        query = self.query_proj(query)
        
        # Reshape for attention: (batch_size * seq_len, embedding_dim)
        query_flat = query.view(-1, self.embedding_dim)
        
        # Compute attention scores
        similarity = self._compute_similarity(query_flat)  # (batch_size * seq_len, memory_size)
        
        # Top-k selection for efficiency
        top_k_scores, top_k_indices = torch.topk(similarity, self.retrieval_top_k, dim=-1)
        
        # Softmax over top-k
        attention_weights = F.softmax(top_k_scores * self.scale, dim=-1)
        
        # Gather top-k values
        top_k_values = self.memory_values[top_k_indices]  # (batch_size * seq_len, top_k, embedding_dim)
        
        # Weighted sum
        retrieved = torch.einsum('bk,bkd->bd', attention_weights, top_k_values)
        
        # Reshape back
        retrieved = retrieved.view(batch_size, seq_len, self.embedding_dim)
        
        # Project output
        output = self.output_proj(retrieved)
        
        # Update usage statistics
        with torch.no_grad():
            for idx in top_k_indices.flatten().unique():
                self.memory_usage[idx] += 1
        
        if return_attention:
            # Reconstruct full attention weights
            full_attention = torch.zeros(batch_size * seq_len, self.memory_size, 
                                        device=query.device)
            full_attention.scatter_(1, top_k_indices, attention_weights)
            full_attention = full_attention.view(batch_size, seq_len, self.memory_size)
            return output, full_attention
        
        return output, None
    
    @torch.no_grad()
    def write(self, keys: torch.Tensor, values: torch.Tensor, 
              write_strength: float = 1.0):
        """
        Write new information to memory.
        Uses least-recently-used strategy for replacement.
        
        Args:
            keys: Key tensor of shape (batch_size, embedding_dim)
            values: Value tensor of shape (batch_size, embedding_dim)
            write_strength: Strength of write operation (0-1)
        """
        batch_size = keys.shape[0]
        
        # Normalize
        keys = F.normalize(keys, dim=-1)
        values = F.normalize(values, dim=-1)
        
        # Find least-used memory slots
        _, least_used_indices = torch.topk(self.memory_age, k=min(batch_size, self.memory_size), 
                                           largest=False)
        
        # Write to memory with momentum
        for i, idx in enumerate(least_used_indices[:batch_size]):
            self.memory_keys[idx] = (1 - write_strength) * self.memory_keys[idx] + \
                                   write_strength * keys[i]
            self.memory_values[idx] = (1 - write_strength) * self.memory_values[idx] + \
                                     write_strength * values[i]
            
            # Normalize after update
            self.memory_keys[idx] = F.normalize(self.memory_keys[idx], dim=-1)
            self.memory_values[idx] = F.normalize(self.memory_values[idx], dim=-1)
            
            # Reset age and usage
            self.memory_age[idx] = 0
        
        # Age all memories
        self.memory_age += 1
        self._step += 1
    
    def update_from_hidden_states(self, hidden_states: torch.Tensor, 
                                  labels: Optional[torch.Tensor] = None):
        """
        Update memory from model hidden states.
        
        Args:
            hidden_states: Hidden states of shape (batch_size, seq_len, embedding_dim)
            labels: Optional labels for selective memory
        """
        # Pool hidden states (mean pooling)
        keys = hidden_states.mean(dim=1)  # (batch_size, embedding_dim)
        values = keys.clone()  # For simplicity, use same for keys and values
        
        self.write(keys, values, write_strength=self.memory_update_rate)
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get statistics about memory usage."""
        return {
            'memory_utilization': (self.memory_usage > 0).float().mean().item(),
            'avg_memory_age': self.memory_age.mean().item(),
            'max_memory_age': self.memory_age.max().item(),
            'total_accesses': self.memory_usage.sum().item(),
            'step': self._step,
        }
    
    def reset_memory(self):
        """Reset memory to random initialization."""
        self.memory_keys = F.normalize(torch.randn_like(self.memory_keys), dim=-1)
        self.memory_values = F.normalize(torch.randn_like(self.memory_values), dim=-1)
        self.memory_age.zero_()
        self.memory_usage.zero_()
        self._step = 0
    
    def save_memory(self, path: str):
        """Save memory state to disk."""
        torch.save({
            'memory_keys': self.memory_keys,
            'memory_values': self.memory_values,
            'memory_age': self.memory_age,
            'memory_usage': self.memory_usage,
            'step': self._step,
        }, path)
    
    def load_memory(self, path: str):
        """Load memory state from disk."""
        checkpoint = torch.load(path)
        self.memory_keys = checkpoint['memory_keys']
        self.memory_values = checkpoint['memory_values']
        self.memory_age = checkpoint['memory_age']
        self.memory_usage = checkpoint['memory_usage']
        self._step = checkpoint.get('step', 0)
