"""
Knowledge Distillation module for transferring knowledge from teacher to student.
Supports multiple distillation strategies and loss functions.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, List, Tuple


class KnowledgeDistiller(nn.Module):
    """
    Knowledge distillation manager.
    Handles distillation loss computation between teacher and student models.
    """
    
    def __init__(self, temperature: float = 2.0, alpha: float = 0.5,
                 distill_loss_type: str = "kl_div", 
                 layer_wise_distillation: bool = True,
                 hidden_distillation: bool = True):
        """
        Initialize knowledge distiller.
        
        Args:
            temperature: Temperature for softening logits
            alpha: Weight balancing distillation loss and task loss (0-1)
            distill_loss_type: Type of distillation loss (kl_div, mse, cosine)
            layer_wise_distillation: Whether to match intermediate layers
            hidden_distillation: Whether to distill hidden states
        """
        super().__init__()
        
        self.temperature = temperature
        self.alpha = alpha
        self.distill_loss_type = distill_loss_type
        self.layer_wise_distillation = layer_wise_distillation
        self.hidden_distillation = hidden_distillation
        
        # Hidden state projection layers (created dynamically)
        self.hidden_projections = nn.ModuleList()
    
    def compute_distillation_loss(self, student_logits: torch.Tensor,
                                 teacher_logits: torch.Tensor) -> torch.Tensor:
        """
        Compute distillation loss between student and teacher logits.
        
        Args:
            student_logits: Logits from student model
            teacher_logits: Logits from teacher model
            
        Returns:
            Distillation loss
        """
        if self.distill_loss_type == "kl_div":
            # KL divergence between soft targets
            student_log_probs = F.log_softmax(student_logits / self.temperature, dim=-1)
            teacher_probs = F.softmax(teacher_logits / self.temperature, dim=-1)
            
            loss = F.kl_div(student_log_probs, teacher_probs, reduction='batchmean')
            loss = loss * (self.temperature ** 2)  # Scale back
            
        elif self.distill_loss_type == "mse":
            # MSE between logits
            loss = F.mse_loss(student_logits, teacher_logits)
            
        elif self.distill_loss_type == "cosine":
            # Cosine similarity loss
            loss = 1 - F.cosine_similarity(
                student_logits.view(-1, student_logits.size(-1)),
                teacher_logits.view(-1, teacher_logits.size(-1)),
                dim=-1
            ).mean()
            
        else:
            raise ValueError(f"Unknown distillation loss type: {self.distill_loss_type}")
        
        return loss
    
    def compute_hidden_distillation_loss(self, student_hidden_states: List[torch.Tensor],
                                        teacher_hidden_states: List[torch.Tensor]) -> torch.Tensor:
        """
        Compute distillation loss for hidden states.
        
        Args:
            student_hidden_states: List of hidden states from student
            teacher_hidden_states: List of hidden states from teacher
            
        Returns:
            Hidden state distillation loss
        """
        if not self.hidden_distillation:
            return torch.tensor(0.0, device=student_hidden_states[0].device)
        
        total_loss = 0.0
        num_layers = min(len(student_hidden_states), len(teacher_hidden_states))
        
        # Create projection layers if needed
        if len(self.hidden_projections) == 0 and num_layers > 0:
            student_dim = student_hidden_states[0].size(-1)
            teacher_dim = teacher_hidden_states[0].size(-1)
            
            if student_dim != teacher_dim:
                for _ in range(num_layers):
                    self.hidden_projections.append(
                        nn.Linear(student_dim, teacher_dim).to(student_hidden_states[0].device)
                    )
        
        # Compute loss for each layer
        for i in range(num_layers):
            student_hidden = student_hidden_states[i]
            teacher_hidden = teacher_hidden_states[i]
            
            # Project if dimensions don't match
            if student_hidden.size(-1) != teacher_hidden.size(-1):
                if i < len(self.hidden_projections):
                    student_hidden = self.hidden_projections[i](student_hidden)
            
            # MSE loss for hidden states
            layer_loss = F.mse_loss(student_hidden, teacher_hidden)
            total_loss += layer_loss
        
        return total_loss / num_layers if num_layers > 0 else torch.tensor(0.0)
    
    def forward(self, student_outputs: Dict[str, torch.Tensor],
                teacher_outputs: Dict[str, torch.Tensor],
                labels: Optional[torch.Tensor] = None,
                task_loss_fn: Optional[callable] = None) -> Dict[str, torch.Tensor]:
        """
        Compute combined distillation and task loss.
        
        Args:
            student_outputs: Dictionary with student model outputs
            teacher_outputs: Dictionary with teacher model outputs
            labels: Ground truth labels for task loss
            task_loss_fn: Function to compute task loss
            
        Returns:
            Dictionary with total loss and individual loss components
        """
        # Extract logits
        student_logits = student_outputs['logits']
        teacher_logits = teacher_outputs['logits']
        
        # Compute distillation loss
        distill_loss = self.compute_distillation_loss(student_logits, teacher_logits)
        
        # Compute hidden state distillation loss
        hidden_loss = torch.tensor(0.0, device=student_logits.device)
        if self.hidden_distillation and 'hidden_states' in student_outputs and 'hidden_states' in teacher_outputs:
            hidden_loss = self.compute_hidden_distillation_loss(
                student_outputs['hidden_states'],
                teacher_outputs['hidden_states']
            )
        
        # Compute task loss if labels provided
        task_loss = torch.tensor(0.0, device=student_logits.device)
        if labels is not None:
            if task_loss_fn is not None:
                task_loss = task_loss_fn(student_logits, labels)
            else:
                # Default: cross-entropy loss
                task_loss = F.cross_entropy(
                    student_logits.view(-1, student_logits.size(-1)),
                    labels.view(-1),
                    ignore_index=-100
                )
        
        # Combine losses
        total_loss = self.alpha * distill_loss + (1 - self.alpha) * task_loss
        
        # Add hidden loss if enabled
        if self.hidden_distillation:
            total_loss = total_loss + 0.1 * hidden_loss  # Weight for hidden loss
        
        return {
            'loss': total_loss,
            'distill_loss': distill_loss.detach(),
            'task_loss': task_loss.detach() if isinstance(task_loss, torch.Tensor) else task_loss,
            'hidden_loss': hidden_loss.detach() if isinstance(hidden_loss, torch.Tensor) else hidden_loss,
        }
    
    def set_temperature(self, temperature: float):
        """Update distillation temperature."""
        self.temperature = temperature
    
    def set_alpha(self, alpha: float):
        """Update alpha (distillation vs task loss weight)."""
        assert 0 <= alpha <= 1, "Alpha must be between 0 and 1"
        self.alpha = alpha
    
    def get_soft_targets(self, teacher_logits: torch.Tensor) -> torch.Tensor:
        """
        Get soft probability distribution from teacher logits.
        
        Args:
            teacher_logits: Logits from teacher
            
        Returns:
            Soft probability distribution
        """
        return F.softmax(teacher_logits / self.temperature, dim=-1)
    
    @staticmethod
    def compute_attention_transfer_loss(student_attentions: List[torch.Tensor],
                                       teacher_attentions: List[torch.Tensor]) -> torch.Tensor:
        """
        Compute attention transfer loss (optional advanced technique).
        
        Args:
            student_attentions: List of attention matrices from student
            teacher_attentions: List of attention matrices from teacher
            
        Returns:
            Attention transfer loss
        """
        total_loss = 0.0
        num_layers = min(len(student_attentions), len(teacher_attentions))
        
        for i in range(num_layers):
            # Normalize attention matrices
            student_attn = F.normalize(student_attentions[i].view(-1), p=2, dim=0)
            teacher_attn = F.normalize(teacher_attentions[i].view(-1), p=2, dim=0)
            
            # MSE loss
            layer_loss = F.mse_loss(student_attn, teacher_attn)
            total_loss += layer_loss
        
        return total_loss / num_layers if num_layers > 0 else torch.tensor(0.0)
