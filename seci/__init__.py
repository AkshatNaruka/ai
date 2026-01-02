"""
SECI - Self-Evolving Compact Intelligence
A modular framework for efficient continual learning with compact transformers.
"""

__version__ = "0.1.0"

from .core.model import CompactTransformer
from .core.teacher import TeacherModel
from .memory.external_memory import ExternalMemory
from .distillation.distiller import KnowledgeDistiller
from .replay.buffer import ReplayBuffer
from .config.config import SECIConfig

__all__ = [
    "CompactTransformer",
    "TeacherModel",
    "ExternalMemory",
    "KnowledgeDistiller",
    "ReplayBuffer",
    "SECIConfig",
]
