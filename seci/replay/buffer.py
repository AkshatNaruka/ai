"""
Replay Buffer for experience replay in continual learning.
Stores past experiences and provides efficient sampling strategies.
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque
import random


class ReplayBuffer:
    """
    Experience replay buffer for continual learning.
    Supports multiple sampling strategies: reservoir, priority, and random.
    """
    
    def __init__(self, buffer_size: int, replay_batch_size: int = 32,
                 sampling_strategy: str = "reservoir", priority_alpha: float = 0.6):
        """
        Initialize replay buffer.
        
        Args:
            buffer_size: Maximum number of samples to store
            replay_batch_size: Batch size for replay sampling
            sampling_strategy: Sampling strategy (reservoir, priority, random)
            priority_alpha: Priority exponent for priority sampling (0-1)
        """
        self.buffer_size = buffer_size
        self.replay_batch_size = replay_batch_size
        self.sampling_strategy = sampling_strategy
        self.priority_alpha = priority_alpha
        
        # Storage for experiences
        self.input_ids = []
        self.attention_masks = []
        self.labels = []
        self.priorities = []  # For priority-based sampling
        self.metadata = []  # Additional info (timestamp, task_id, etc.)
        
        self.current_size = 0
        self.total_added = 0
    
    def add(self, input_ids: torch.Tensor, attention_mask: torch.Tensor,
            labels: torch.Tensor, priority: Optional[float] = None,
            metadata: Optional[Dict] = None):
        """
        Add a batch of experiences to the buffer.
        
        Args:
            input_ids: Input token IDs
            attention_mask: Attention mask
            labels: Target labels
            priority: Priority score for priority sampling
            metadata: Additional metadata dictionary
        """
        batch_size = input_ids.size(0)
        
        for i in range(batch_size):
            if self.sampling_strategy == "reservoir":
                self._add_reservoir(
                    input_ids[i].cpu(),
                    attention_mask[i].cpu(),
                    labels[i].cpu(),
                    priority if priority is not None else 1.0,
                    metadata
                )
            else:
                self._add_regular(
                    input_ids[i].cpu(),
                    attention_mask[i].cpu(),
                    labels[i].cpu(),
                    priority if priority is not None else 1.0,
                    metadata
                )
            
            self.total_added += 1
    
    def _add_regular(self, input_ids: torch.Tensor, attention_mask: torch.Tensor,
                    labels: torch.Tensor, priority: float, metadata: Optional[Dict]):
        """Add experience using regular FIFO strategy."""
        if self.current_size < self.buffer_size:
            # Buffer not full, append
            self.input_ids.append(input_ids)
            self.attention_masks.append(attention_mask)
            self.labels.append(labels)
            self.priorities.append(priority)
            self.metadata.append(metadata or {})
            self.current_size += 1
        else:
            # Buffer full, replace oldest
            idx = self.total_added % self.buffer_size
            self.input_ids[idx] = input_ids
            self.attention_masks[idx] = attention_mask
            self.labels[idx] = labels
            self.priorities[idx] = priority
            self.metadata[idx] = metadata or {}
    
    def _add_reservoir(self, input_ids: torch.Tensor, attention_mask: torch.Tensor,
                      labels: torch.Tensor, priority: float, metadata: Optional[Dict]):
        """Add experience using reservoir sampling."""
        if self.current_size < self.buffer_size:
            # Buffer not full, append
            self.input_ids.append(input_ids)
            self.attention_masks.append(attention_mask)
            self.labels.append(labels)
            self.priorities.append(priority)
            self.metadata.append(metadata or {})
            self.current_size += 1
        else:
            # Reservoir sampling: replace with probability buffer_size / total_added
            idx = random.randint(0, self.total_added)
            if idx < self.buffer_size:
                self.input_ids[idx] = input_ids
                self.attention_masks[idx] = attention_mask
                self.labels[idx] = labels
                self.priorities[idx] = priority
                self.metadata[idx] = metadata or {}
    
    def sample(self, batch_size: Optional[int] = None, device: str = "cpu") -> Dict[str, torch.Tensor]:
        """
        Sample a batch from the replay buffer.
        
        Args:
            batch_size: Number of samples to draw (defaults to replay_batch_size)
            device: Device to place tensors on
            
        Returns:
            Dictionary with sampled batch
        """
        if self.current_size == 0:
            return None
        
        batch_size = batch_size or self.replay_batch_size
        batch_size = min(batch_size, self.current_size)
        
        # Sample indices based on strategy
        if self.sampling_strategy == "priority":
            indices = self._sample_priority(batch_size)
        else:
            indices = self._sample_random(batch_size)
        
        # Gather samples
        sampled_input_ids = torch.stack([self.input_ids[i] for i in indices]).to(device)
        sampled_attention_masks = torch.stack([self.attention_masks[i] for i in indices]).to(device)
        sampled_labels = torch.stack([self.labels[i] for i in indices]).to(device)
        
        return {
            'input_ids': sampled_input_ids,
            'attention_mask': sampled_attention_masks,
            'labels': sampled_labels,
            'indices': indices,
        }
    
    def _sample_random(self, batch_size: int) -> List[int]:
        """Sample indices uniformly at random."""
        return random.sample(range(self.current_size), batch_size)
    
    def _sample_priority(self, batch_size: int) -> List[int]:
        """Sample indices based on priority scores."""
        # Convert priorities to probabilities
        priorities = np.array([self.priorities[i] for i in range(self.current_size)])
        priorities = priorities ** self.priority_alpha
        probabilities = priorities / priorities.sum()
        
        # Sample without replacement
        indices = np.random.choice(
            self.current_size,
            size=batch_size,
            replace=False,
            p=probabilities
        )
        
        return indices.tolist()
    
    def update_priorities(self, indices: List[int], priorities: List[float]):
        """
        Update priorities for specific samples.
        Useful for prioritized experience replay.
        
        Args:
            indices: Indices of samples to update
            priorities: New priority values
        """
        for idx, priority in zip(indices, priorities):
            if 0 <= idx < self.current_size:
                self.priorities[idx] = priority
    
    def get_stats(self) -> Dict[str, any]:
        """Get buffer statistics."""
        return {
            'current_size': self.current_size,
            'buffer_size': self.buffer_size,
            'total_added': self.total_added,
            'utilization': self.current_size / self.buffer_size if self.buffer_size > 0 else 0,
            'avg_priority': np.mean(self.priorities) if self.priorities else 0,
        }
    
    def clear(self):
        """Clear all experiences from buffer."""
        self.input_ids.clear()
        self.attention_masks.clear()
        self.labels.clear()
        self.priorities.clear()
        self.metadata.clear()
        self.current_size = 0
        self.total_added = 0
    
    def save(self, path: str):
        """Save buffer to disk."""
        torch.save({
            'input_ids': self.input_ids,
            'attention_masks': self.attention_masks,
            'labels': self.labels,
            'priorities': self.priorities,
            'metadata': self.metadata,
            'current_size': self.current_size,
            'total_added': self.total_added,
            'config': {
                'buffer_size': self.buffer_size,
                'replay_batch_size': self.replay_batch_size,
                'sampling_strategy': self.sampling_strategy,
                'priority_alpha': self.priority_alpha,
            }
        }, path)
    
    @classmethod
    def load(cls, path: str) -> 'ReplayBuffer':
        """Load buffer from disk."""
        checkpoint = torch.load(path)
        config = checkpoint['config']
        
        buffer = cls(
            buffer_size=config['buffer_size'],
            replay_batch_size=config['replay_batch_size'],
            sampling_strategy=config['sampling_strategy'],
            priority_alpha=config['priority_alpha']
        )
        
        buffer.input_ids = checkpoint['input_ids']
        buffer.attention_masks = checkpoint['attention_masks']
        buffer.labels = checkpoint['labels']
        buffer.priorities = checkpoint['priorities']
        buffer.metadata = checkpoint['metadata']
        buffer.current_size = checkpoint['current_size']
        buffer.total_added = checkpoint['total_added']
        
        return buffer
    
    def __len__(self) -> int:
        """Return current buffer size."""
        return self.current_size
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self.current_size == 0
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        return self.current_size >= self.buffer_size
