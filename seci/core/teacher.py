"""
Teacher Model interface for knowledge distillation.
Can wrap any pre-trained model for distillation.
"""

import torch
import torch.nn as nn
from typing import Dict, Optional
from .model import CompactTransformer


class TeacherModel(nn.Module):
    """
    Teacher model wrapper for knowledge distillation.
    Can use a larger frozen model or an ensemble.
    """
    
    def __init__(self, model: Optional[nn.Module] = None, 
                 use_compact_as_teacher: bool = False,
                 teacher_config: Optional[Dict] = None):
        """
        Initialize teacher model.
        
        Args:
            model: Pre-trained model to use as teacher
            use_compact_as_teacher: If True, uses CompactTransformer as teacher
            teacher_config: Configuration for creating a teacher model
        """
        super().__init__()
        
        if model is not None:
            self.model = model
        elif use_compact_as_teacher and teacher_config is not None:
            # Create a larger CompactTransformer as teacher
            self.model = CompactTransformer(**teacher_config)
        else:
            raise ValueError("Must provide either a model or teacher_config")
        
        # Freeze teacher
        self.freeze()
    
    def freeze(self):
        """Freeze all teacher parameters."""
        for param in self.model.parameters():
            param.requires_grad = False
        self.model.eval()
    
    def forward(self, input_ids: torch.Tensor, 
                attention_mask: Optional[torch.Tensor] = None,
                return_hidden_states: bool = True) -> Dict[str, torch.Tensor]:
        """
        Forward pass through teacher model.
        
        Args:
            input_ids: Token IDs
            attention_mask: Attention mask
            return_hidden_states: Whether to return intermediate hidden states
            
        Returns:
            Dictionary with logits and optionally hidden states
        """
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                return_hidden_states=return_hidden_states
            )
        return outputs
    
    @torch.no_grad()
    def get_soft_targets(self, input_ids: torch.Tensor,
                        attention_mask: Optional[torch.Tensor] = None,
                        temperature: float = 1.0) -> torch.Tensor:
        """
        Get soft targets (probabilities) from teacher.
        
        Args:
            input_ids: Token IDs
            attention_mask: Attention mask
            temperature: Temperature for softening logits
            
        Returns:
            Soft probability distribution
        """
        outputs = self.forward(input_ids, attention_mask, return_hidden_states=False)
        logits = outputs['logits']
        soft_targets = torch.softmax(logits / temperature, dim=-1)
        return soft_targets
    
    @torch.no_grad()
    def get_hidden_states(self, input_ids: torch.Tensor,
                         attention_mask: Optional[torch.Tensor] = None) -> list:
        """
        Extract hidden states from all layers.
        
        Args:
            input_ids: Token IDs
            attention_mask: Attention mask
            
        Returns:
            List of hidden states from each layer
        """
        outputs = self.forward(input_ids, attention_mask, return_hidden_states=True)
        return outputs.get('hidden_states', [])
    
    def save(self, path: str):
        """Save teacher model."""
        torch.save(self.model.state_dict(), path)
    
    @classmethod
    def load(cls, path: str, model_class, model_config: Dict):
        """Load teacher model from checkpoint."""
        model = model_class(**model_config)
        model.load_state_dict(torch.load(path))
        return cls(model=model)
