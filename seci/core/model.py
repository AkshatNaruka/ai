"""
Compact Transformer Model with Quantization and LoRA support.
Core student model for SECI.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict
import math


class LoRALayer(nn.Module):
    """Low-Rank Adaptation layer for efficient fine-tuning."""
    
    def __init__(self, in_features: int, out_features: int, r: int = 8, 
                 alpha: int = 16, dropout: float = 0.1):
        super().__init__()
        self.r = r
        self.alpha = alpha
        self.scaling = alpha / r
        
        # LoRA matrices
        self.lora_A = nn.Parameter(torch.zeros(in_features, r))
        self.lora_B = nn.Parameter(torch.zeros(r, out_features))
        self.dropout = nn.Dropout(dropout)
        
        # Initialize
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply LoRA transformation."""
        return self.dropout(x @ self.lora_A @ self.lora_B) * self.scaling


class MultiHeadAttention(nn.Module):
    """Multi-head attention with optional LoRA."""
    
    def __init__(self, hidden_size: int, num_heads: int, dropout: float = 0.1,
                 use_lora: bool = False, lora_r: int = 8, lora_alpha: int = 16):
        super().__init__()
        assert hidden_size % num_heads == 0
        
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        self.scale = self.head_dim ** -0.5
        
        # Linear projections
        self.q_proj = nn.Linear(hidden_size, hidden_size)
        self.k_proj = nn.Linear(hidden_size, hidden_size)
        self.v_proj = nn.Linear(hidden_size, hidden_size)
        self.out_proj = nn.Linear(hidden_size, hidden_size)
        
        # LoRA adapters
        self.use_lora = use_lora
        if use_lora:
            self.q_lora = LoRALayer(hidden_size, hidden_size, lora_r, lora_alpha, dropout)
            self.v_lora = LoRALayer(hidden_size, hidden_size, lora_r, lora_alpha, dropout)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape
        
        # Project and split heads
        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)
        
        # Apply LoRA if enabled
        if self.use_lora:
            q = q + self.q_lora(x)
            v = v + self.v_lora(x)
        
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Attention scores
        attn_scores = (q @ k.transpose(-2, -1)) * self.scale
        
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))
        
        attn_probs = F.softmax(attn_scores, dim=-1)
        attn_probs = self.dropout(attn_probs)
        
        # Apply attention to values
        attn_output = attn_probs @ v
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_size)
        
        return self.out_proj(attn_output)


class FeedForward(nn.Module):
    """Feed-forward network with GELU activation."""
    
    def __init__(self, hidden_size: int, intermediate_size: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(hidden_size, intermediate_size)
        self.fc2 = nn.Linear(intermediate_size, hidden_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(self.dropout(F.gelu(self.fc1(x))))


class TransformerBlock(nn.Module):
    """Single transformer block with pre-norm architecture."""
    
    def __init__(self, hidden_size: int, num_heads: int, intermediate_size: int,
                 dropout: float = 0.1, use_lora: bool = False, lora_r: int = 8, 
                 lora_alpha: int = 16):
        super().__init__()
        self.ln1 = nn.LayerNorm(hidden_size)
        self.attn = MultiHeadAttention(hidden_size, num_heads, dropout, use_lora, lora_r, lora_alpha)
        self.ln2 = nn.LayerNorm(hidden_size)
        self.ffn = FeedForward(hidden_size, intermediate_size, dropout)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # Self-attention with residual
        attn_output = self.attn(self.ln1(x), mask)
        x = x + self.dropout(attn_output)
        
        # Feed-forward with residual
        ffn_output = self.ffn(self.ln2(x))
        x = x + self.dropout(ffn_output)
        
        return x, attn_output


class CompactTransformer(nn.Module):
    """
    Compact Transformer model for SECI.
    Supports quantization and LoRA for efficient training.
    """
    
    def __init__(self, vocab_size: int, hidden_size: int, num_layers: int, 
                 num_heads: int, intermediate_size: int, max_seq_length: int,
                 dropout: float = 0.1, use_quantization: bool = False,
                 quantization_bits: int = 8, use_lora: bool = False,
                 lora_r: int = 8, lora_alpha: int = 16, lora_dropout: float = 0.1):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.use_quantization = use_quantization
        self.use_lora = use_lora
        
        # Embeddings
        self.token_embedding = nn.Embedding(vocab_size, hidden_size)
        self.position_embedding = nn.Embedding(max_seq_length, hidden_size)
        self.embedding_dropout = nn.Dropout(dropout)
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(hidden_size, num_heads, intermediate_size, dropout,
                           use_lora, lora_r, lora_alpha)
            for _ in range(num_layers)
        ])
        
        # Final layer norm
        self.ln_f = nn.LayerNorm(hidden_size)
        
        # Output head
        self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)
        
        # Tie weights
        self.lm_head.weight = self.token_embedding.weight
        
        # Initialize weights
        self.apply(self._init_weights)
        
        # Apply quantization if requested
        if use_quantization:
            self._quantize_model(quantization_bits)
    
    def _init_weights(self, module):
        """Initialize weights."""
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)
    
    def _quantize_model(self, bits: int = 8):
        """Apply dynamic quantization to the model."""
        # This is a placeholder for quantization
        # In practice, use torch.quantization or bitsandbytes
        pass
    
    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None,
                return_hidden_states: bool = False) -> Dict[str, torch.Tensor]:
        """
        Forward pass of the model.
        
        Args:
            input_ids: Token IDs of shape (batch_size, seq_len)
            attention_mask: Attention mask of shape (batch_size, seq_len)
            return_hidden_states: Whether to return intermediate hidden states
            
        Returns:
            Dictionary containing logits and optionally hidden states
        """
        batch_size, seq_len = input_ids.shape
        device = input_ids.device
        
        # Create position IDs
        position_ids = torch.arange(seq_len, dtype=torch.long, device=device)
        position_ids = position_ids.unsqueeze(0).expand(batch_size, -1)
        
        # Embeddings
        token_embeds = self.token_embedding(input_ids)
        position_embeds = self.position_embedding(position_ids)
        hidden_states = self.embedding_dropout(token_embeds + position_embeds)
        
        # Prepare attention mask
        if attention_mask is not None:
            attention_mask = attention_mask.unsqueeze(1).unsqueeze(2)
            attention_mask = attention_mask.to(dtype=hidden_states.dtype)
        
        # Store hidden states for distillation
        all_hidden_states = [] if return_hidden_states else None
        
        # Pass through transformer blocks
        for block in self.blocks:
            if return_hidden_states:
                all_hidden_states.append(hidden_states)
            hidden_states, _ = block(hidden_states, attention_mask)
        
        # Final layer norm
        hidden_states = self.ln_f(hidden_states)
        
        if return_hidden_states:
            all_hidden_states.append(hidden_states)
        
        # Language modeling head
        logits = self.lm_head(hidden_states)
        
        output = {'logits': logits, 'last_hidden_state': hidden_states}
        if return_hidden_states:
            output['hidden_states'] = all_hidden_states
        
        return output
    
    def get_trainable_params(self) -> int:
        """Count trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def enable_lora(self):
        """Enable LoRA adapters for fine-tuning."""
        if not self.use_lora:
            return
        
        # Freeze base model
        for param in self.parameters():
            param.requires_grad = False
        
        # Unfreeze LoRA parameters
        for block in self.blocks:
            if hasattr(block.attn, 'q_lora'):
                for param in block.attn.q_lora.parameters():
                    param.requires_grad = True
                for param in block.attn.v_lora.parameters():
                    param.requires_grad = True
    
    def disable_lora(self):
        """Disable LoRA adapters."""
        for param in self.parameters():
            param.requires_grad = True
