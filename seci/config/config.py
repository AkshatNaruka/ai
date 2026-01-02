"""
Configuration management for SECI.
Handles all hyperparameters and system settings.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import yaml
import os


@dataclass
class ModelConfig:
    """Configuration for the compact transformer model."""
    vocab_size: int = 32000
    hidden_size: int = 256
    num_layers: int = 4
    num_heads: int = 4
    intermediate_size: int = 1024
    max_seq_length: int = 512
    dropout: float = 0.1
    
    # Quantization settings
    use_quantization: bool = False
    quantization_bits: int = 8
    
    # LoRA settings
    use_lora: bool = False
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    lora_target_modules: list = field(default_factory=lambda: ["q_proj", "v_proj"])


@dataclass
class MemoryConfig:
    """Configuration for external memory system."""
    memory_size: int = 1000
    embedding_dim: int = 256
    num_memory_heads: int = 4
    memory_update_rate: float = 0.01
    retrieval_top_k: int = 5
    use_faiss: bool = False  # Use FAISS for large-scale retrieval


@dataclass
class DistillationConfig:
    """Configuration for knowledge distillation."""
    temperature: float = 2.0
    alpha: float = 0.5  # Weight for distillation loss vs task loss
    distill_loss_type: str = "kl_div"  # Options: kl_div, mse, cosine
    layer_wise_distillation: bool = True
    hidden_distillation: bool = True


@dataclass
class ReplayConfig:
    """Configuration for replay buffer."""
    buffer_size: int = 10000
    replay_batch_size: int = 32
    replay_frequency: int = 5  # Replay every N training steps
    sampling_strategy: str = "reservoir"  # Options: reservoir, priority, random
    priority_alpha: float = 0.6  # For priority sampling


@dataclass
class TrainingConfig:
    """Training hyperparameters."""
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    max_steps: int = 10000
    warmup_steps: int = 500
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    eval_steps: int = 500
    save_steps: int = 1000
    logging_steps: int = 100
    seed: int = 42


@dataclass
class SECIConfig:
    """Main configuration for SECI system."""
    model: ModelConfig = field(default_factory=ModelConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    distillation: DistillationConfig = field(default_factory=DistillationConfig)
    replay: ReplayConfig = field(default_factory=ReplayConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    
    # System settings
    device: str = "cuda"
    mixed_precision: bool = True
    output_dir: str = "./outputs"
    experiment_name: str = "seci_mvp"
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "SECIConfig":
        """Load configuration from YAML file."""
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(
            model=ModelConfig(**config_dict.get('model', {})),
            memory=MemoryConfig(**config_dict.get('memory', {})),
            distillation=DistillationConfig(**config_dict.get('distillation', {})),
            replay=ReplayConfig(**config_dict.get('replay', {})),
            training=TrainingConfig(**config_dict.get('training', {})),
            **{k: v for k, v in config_dict.items() 
               if k not in ['model', 'memory', 'distillation', 'replay', 'training']}
        )
    
    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to YAML file."""
        config_dict = {
            'model': self.model.__dict__,
            'memory': self.memory.__dict__,
            'distillation': self.distillation.__dict__,
            'replay': self.replay.__dict__,
            'training': self.training.__dict__,
            'device': self.device,
            'mixed_precision': self.mixed_precision,
            'output_dir': self.output_dir,
            'experiment_name': self.experiment_name,
        }
        
        os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
        with open(yaml_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'model': self.model.__dict__,
            'memory': self.memory.__dict__,
            'distillation': self.distillation.__dict__,
            'replay': self.replay.__dict__,
            'training': self.training.__dict__,
            'device': self.device,
            'mixed_precision': self.mixed_precision,
            'output_dir': self.output_dir,
            'experiment_name': self.experiment_name,
        }
