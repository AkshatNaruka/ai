"""
SECI Training Script - End-to-End Execution Flow
Demonstrates the complete training loop with all SECI components.
"""

import torch
import torch.nn.functional as F
from torch.optim import AdamW
from tqdm import tqdm
import os
import argparse

from seci.config.config import SECIConfig, ModelConfig
from seci.core.model import CompactTransformer
from seci.core.teacher import TeacherModel
from seci.memory.external_memory import ExternalMemory
from seci.distillation.distiller import KnowledgeDistiller
from seci.replay.buffer import ReplayBuffer
from seci.utils.helpers import (
    set_seed, count_parameters, get_device, 
    save_checkpoint, load_checkpoint, format_metrics,
    AverageMeter, get_linear_schedule_with_warmup
)


class SECITrainer:
    """
    Main trainer for SECI system.
    Orchestrates all components for self-evolving continual learning.
    """
    
    def __init__(self, config: SECIConfig):
        """
        Initialize SECI trainer.
        
        Args:
            config: SECI configuration
        """
        self.config = config
        self.device = get_device(prefer_cuda=(config.device == "cuda"))
        
        # Set seed for reproducibility
        set_seed(config.training.seed)
        
        # Initialize student model (compact transformer)
        self.student = CompactTransformer(
            vocab_size=config.model.vocab_size,
            hidden_size=config.model.hidden_size,
            num_layers=config.model.num_layers,
            num_heads=config.model.num_heads,
            intermediate_size=config.model.intermediate_size,
            max_seq_length=config.model.max_seq_length,
            dropout=config.model.dropout,
            use_quantization=config.model.use_quantization,
            quantization_bits=config.model.quantization_bits,
            use_lora=config.model.use_lora,
            lora_r=config.model.lora_r,
            lora_alpha=config.model.lora_alpha,
            lora_dropout=config.model.lora_dropout
        ).to(self.device)
        
        # Initialize teacher model (larger version for MVP)
        teacher_config = ModelConfig(
            vocab_size=config.model.vocab_size,
            hidden_size=config.model.hidden_size * 2,  # Larger
            num_layers=config.model.num_layers * 2,    # Deeper
            num_heads=config.model.num_heads * 2,
            intermediate_size=config.model.intermediate_size * 2,
            max_seq_length=config.model.max_seq_length,
            dropout=config.model.dropout,
            use_quantization=False,
            use_lora=False
        )
        
        teacher_model = CompactTransformer(**teacher_config.__dict__).to(self.device)
        self.teacher = TeacherModel(model=teacher_model)
        
        # Initialize external memory
        self.memory = ExternalMemory(
            memory_size=config.memory.memory_size,
            embedding_dim=config.model.hidden_size,
            num_memory_heads=config.memory.num_memory_heads,
            memory_update_rate=config.memory.memory_update_rate,
            retrieval_top_k=config.memory.retrieval_top_k
        ).to(self.device)
        
        # Initialize knowledge distiller
        self.distiller = KnowledgeDistiller(
            temperature=config.distillation.temperature,
            alpha=config.distillation.alpha,
            distill_loss_type=config.distillation.distill_loss_type,
            layer_wise_distillation=config.distillation.layer_wise_distillation,
            hidden_distillation=config.distillation.hidden_distillation
        ).to(self.device)
        
        # Initialize replay buffer
        self.replay_buffer = ReplayBuffer(
            buffer_size=config.replay.buffer_size,
            replay_batch_size=config.replay.replay_batch_size,
            sampling_strategy=config.replay.sampling_strategy,
            priority_alpha=config.replay.priority_alpha
        )
        
        # Optimizer and scheduler
        self.optimizer = AdamW(
            self.student.parameters(),
            lr=config.training.learning_rate,
            weight_decay=config.training.weight_decay
        )
        
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=config.training.warmup_steps,
            num_training_steps=config.training.max_steps
        )
        
        # Training state
        self.global_step = 0
        self.best_loss = float('inf')
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
        
        # Print model info
        print(f"\n{'='*60}")
        print(f"SECI Training Configuration")
        print(f"{'='*60}")
        print(f"Student parameters: {count_parameters(self.student):,}")
        print(f"Teacher parameters: {count_parameters(self.teacher):,}")
        print(f"Trainable parameters: {count_parameters(self.student, trainable_only=True):,}")
        print(f"Memory slots: {config.memory.memory_size}")
        print(f"Replay buffer size: {config.replay.buffer_size}")
        print(f"Device: {self.device}")
        print(f"{'='*60}\n")
    
    def train_step(self, batch: dict, use_replay: bool = True) -> dict:
        """
        Execute single training step.
        
        Args:
            batch: Training batch
            use_replay: Whether to use replay buffer
            
        Returns:
            Dictionary with loss and metrics
        """
        self.student.train()
        
        input_ids = batch['input_ids'].to(self.device)
        attention_mask = batch['attention_mask'].to(self.device)
        labels = batch.get('labels', input_ids).to(self.device)
        
        # Forward pass through student
        student_outputs = self.student(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_hidden_states=True
        )
        
        # Get memory-augmented representations
        memory_output, _ = self.memory.read(student_outputs['last_hidden_state'])
        
        # Forward pass through teacher
        with torch.no_grad():
            teacher_outputs = self.teacher(
                input_ids=input_ids,
                attention_mask=attention_mask,
                return_hidden_states=True
            )
        
        # Compute distillation loss
        loss_dict = self.distiller(
            student_outputs=student_outputs,
            teacher_outputs=teacher_outputs,
            labels=labels
        )
        
        loss = loss_dict['loss']
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(
            self.student.parameters(),
            self.config.training.max_grad_norm
        )
        
        # Optimizer step
        self.optimizer.step()
        self.scheduler.step()
        self.optimizer.zero_grad()
        
        # Update memory with current hidden states
        self.memory.update_from_hidden_states(
            student_outputs['last_hidden_state'].detach()
        )
        
        # Add to replay buffer
        self.replay_buffer.add(
            input_ids=input_ids.detach(),
            attention_mask=attention_mask.detach(),
            labels=labels.detach(),
            priority=loss.item()
        )
        
        # Replay step (if enabled and buffer has enough samples)
        replay_loss = 0.0
        if use_replay and not self.replay_buffer.is_empty():
            if self.global_step % self.config.replay.replay_frequency == 0:
                replay_loss = self._replay_step()
        
        self.global_step += 1
        
        return {
            'loss': loss.item(),
            'distill_loss': loss_dict['distill_loss'].item(),
            'task_loss': loss_dict['task_loss'].item() if torch.is_tensor(loss_dict['task_loss']) else loss_dict['task_loss'],
            'hidden_loss': loss_dict['hidden_loss'].item() if torch.is_tensor(loss_dict['hidden_loss']) else loss_dict['hidden_loss'],
            'replay_loss': replay_loss,
            'lr': self.scheduler.get_last_lr()[0]
        }
    
    def _replay_step(self) -> float:
        """
        Execute replay training step.
        
        Returns:
            Replay loss
        """
        # Sample from replay buffer
        replay_batch = self.replay_buffer.sample(device=self.device)
        
        if replay_batch is None:
            return 0.0
        
        # Forward pass
        student_outputs = self.student(
            input_ids=replay_batch['input_ids'],
            attention_mask=replay_batch['attention_mask'],
            return_hidden_states=False
        )
        
        # Compute loss
        replay_loss = F.cross_entropy(
            student_outputs['logits'].view(-1, student_outputs['logits'].size(-1)),
            replay_batch['labels'].view(-1),
            ignore_index=-100
        )
        
        # Backward pass
        replay_loss.backward()
        torch.nn.utils.clip_grad_norm_(
            self.student.parameters(),
            self.config.training.max_grad_norm
        )
        self.optimizer.step()
        self.optimizer.zero_grad()
        
        return replay_loss.item()
    
    def train(self, train_dataloader, num_epochs: int = 1):
        """
        Main training loop.
        
        Args:
            train_dataloader: Training data loader
            num_epochs: Number of epochs to train
        """
        print(f"Starting training for {num_epochs} epochs...")
        
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch + 1}/{num_epochs}")
            
            # Metrics
            loss_meter = AverageMeter()
            distill_loss_meter = AverageMeter()
            task_loss_meter = AverageMeter()
            
            progress_bar = tqdm(train_dataloader, desc=f"Training")
            
            for batch_idx, batch in enumerate(progress_bar):
                # Training step
                metrics = self.train_step(batch)
                
                # Update meters
                loss_meter.update(metrics['loss'])
                distill_loss_meter.update(metrics['distill_loss'])
                task_loss_meter.update(metrics['task_loss'])
                
                # Update progress bar
                progress_bar.set_postfix({
                    'loss': f"{loss_meter.avg:.4f}",
                    'distill': f"{distill_loss_meter.avg:.4f}",
                    'lr': f"{metrics['lr']:.2e}"
                })
                
                # Logging
                if self.global_step % self.config.training.logging_steps == 0:
                    memory_stats = self.memory.get_memory_stats()
                    buffer_stats = self.replay_buffer.get_stats()
                    
                    print(f"\nStep {self.global_step}:")
                    print(format_metrics(metrics))
                    print(f"Memory utilization: {memory_stats['memory_utilization']:.2%}")
                    print(f"Buffer utilization: {buffer_stats['utilization']:.2%}")
                
                # Save checkpoint
                if self.global_step % self.config.training.save_steps == 0:
                    self.save_checkpoint()
                
                # Check if reached max steps
                if self.global_step >= self.config.training.max_steps:
                    print(f"\nReached max steps ({self.config.training.max_steps})")
                    return
    
    def save_checkpoint(self):
        """Save training checkpoint."""
        checkpoint_path = os.path.join(
            self.config.output_dir,
            f"checkpoint_step_{self.global_step}.pt"
        )
        
        save_checkpoint(
            model=self.student,
            optimizer=self.optimizer,
            step=self.global_step,
            path=checkpoint_path,
            config=self.config.to_dict()
        )
        
        # Save memory and replay buffer
        memory_path = os.path.join(self.config.output_dir, f"memory_step_{self.global_step}.pt")
        buffer_path = os.path.join(self.config.output_dir, f"buffer_step_{self.global_step}.pt")
        
        self.memory.save_memory(memory_path)
        self.replay_buffer.save(buffer_path)
        
        print(f"Checkpoint saved at step {self.global_step}")


def create_dummy_dataloader(config: SECIConfig, num_batches: int = 100):
    """
    Create a dummy dataloader for testing.
    Replace with real data loading logic.
    """
    from torch.utils.data import DataLoader, TensorDataset
    
    # Create random data
    input_ids = torch.randint(0, config.model.vocab_size, 
                             (num_batches * config.training.batch_size, 128))
    attention_mask = torch.ones_like(input_ids)
    
    dataset = TensorDataset(input_ids, attention_mask)
    dataloader = DataLoader(dataset, batch_size=config.training.batch_size, shuffle=True)
    
    # Format batches
    formatted_batches = []
    for input_ids_batch, attention_mask_batch in dataloader:
        formatted_batches.append({
            'input_ids': input_ids_batch,
            'attention_mask': attention_mask_batch,
            'labels': input_ids_batch.clone()
        })
    
    return formatted_batches


def main():
    parser = argparse.ArgumentParser(description="Train SECI model")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML")
    parser.add_argument("--output_dir", type=str, default="./outputs", help="Output directory")
    parser.add_argument("--num_epochs", type=int, default=1, help="Number of epochs")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config and os.path.exists(args.config):
        config = SECIConfig.from_yaml(args.config)
    else:
        config = SECIConfig()
    
    config.output_dir = args.output_dir
    
    # Create trainer
    trainer = SECITrainer(config)
    
    # Create dummy dataloader (replace with real data)
    train_dataloader = create_dummy_dataloader(config, num_batches=100)
    
    # Train
    trainer.train(train_dataloader, num_epochs=args.num_epochs)
    
    print("\nTraining completed!")
    print(f"Results saved to: {config.output_dir}")


if __name__ == "__main__":
    main()
