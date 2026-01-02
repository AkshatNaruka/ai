"""
Basic SECI Training Example
Demonstrates minimal usage of the SECI framework.
"""

import torch
from torch.utils.data import DataLoader, TensorDataset

from seci import (
    SECIConfig,
    CompactTransformer,
    TeacherModel,
    ExternalMemory,
    KnowledgeDistiller,
    ReplayBuffer
)
from seci.config.config import ModelConfig


def create_dummy_dataset(num_samples=1000, seq_len=128, vocab_size=32000):
    """Create a simple dummy dataset for demonstration."""
    input_ids = torch.randint(0, vocab_size, (num_samples, seq_len))
    attention_mask = torch.ones_like(input_ids)
    labels = input_ids.clone()
    
    dataset = TensorDataset(input_ids, attention_mask, labels)
    return DataLoader(dataset, batch_size=32, shuffle=True)


def main():
    print("="*60)
    print("SECI Basic Training Example")
    print("="*60)
    
    # 1. Load configuration
    config = SECIConfig.from_yaml("config/default.yaml")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice: {device}")
    
    # 2. Initialize student model
    print("\n1. Initializing student model...")
    student = CompactTransformer(
        vocab_size=config.model.vocab_size,
        hidden_size=config.model.hidden_size,
        num_layers=config.model.num_layers,
        num_heads=config.model.num_heads,
        intermediate_size=config.model.intermediate_size,
        max_seq_length=config.model.max_seq_length,
        dropout=config.model.dropout,
        use_lora=config.model.use_lora,
        use_quantization=config.model.use_quantization
    ).to(device)
    
    print(f"   Parameters: {student.get_trainable_params():,}")
    
    # 3. Initialize teacher model
    print("\n2. Initializing teacher model...")
    teacher_config = ModelConfig(
        vocab_size=config.model.vocab_size,
        hidden_size=config.model.hidden_size * 2,
        num_layers=config.model.num_layers * 2,
        num_heads=config.model.num_heads * 2,
        intermediate_size=config.model.intermediate_size * 2,
        max_seq_length=config.model.max_seq_length
    )
    teacher_model = CompactTransformer(**teacher_config.__dict__).to(device)
    teacher = TeacherModel(model=teacher_model)
    
    # 4. Initialize memory
    print("\n3. Initializing external memory...")
    memory = ExternalMemory(
        memory_size=config.memory.memory_size,
        embedding_dim=config.model.hidden_size,
        num_memory_heads=config.memory.num_memory_heads,
        retrieval_top_k=config.memory.retrieval_top_k
    ).to(device)
    
    # 5. Initialize distiller
    print("\n4. Initializing knowledge distiller...")
    distiller = KnowledgeDistiller(
        temperature=config.distillation.temperature,
        alpha=config.distillation.alpha,
        distill_loss_type=config.distillation.distill_loss_type
    ).to(device)
    
    # 6. Initialize replay buffer
    print("\n5. Initializing replay buffer...")
    replay_buffer = ReplayBuffer(
        buffer_size=config.replay.buffer_size,
        replay_batch_size=config.replay.replay_batch_size,
        sampling_strategy=config.replay.sampling_strategy
    )
    
    # 7. Setup optimizer
    print("\n6. Setting up optimizer...")
    optimizer = torch.optim.AdamW(
        student.parameters(),
        lr=config.training.learning_rate,
        weight_decay=config.training.weight_decay
    )
    
    # 8. Create dataset
    print("\n7. Creating dummy dataset...")
    train_loader = create_dummy_dataset(
        num_samples=1000,
        seq_len=128,
        vocab_size=config.model.vocab_size
    )
    
    # 9. Training loop
    print("\n8. Starting training...")
    print("="*60)
    
    student.train()
    for step, (input_ids, attention_mask, labels) in enumerate(train_loader):
        if step >= 10:  # Just 10 steps for demo
            break
        
        input_ids = input_ids.to(device)
        attention_mask = attention_mask.to(device)
        labels = labels.to(device)
        
        # Forward pass - student
        student_outputs = student(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_hidden_states=True
        )
        
        # Read from memory
        memory_output, _ = memory.read(student_outputs['last_hidden_state'])
        
        # Forward pass - teacher
        with torch.no_grad():
            teacher_outputs = teacher(
                input_ids=input_ids,
                attention_mask=attention_mask,
                return_hidden_states=True
            )
        
        # Compute loss
        loss_dict = distiller(
            student_outputs=student_outputs,
            teacher_outputs=teacher_outputs,
            labels=labels
        )
        
        # Backward pass
        loss = loss_dict['loss']
        loss.backward()
        torch.nn.utils.clip_grad_norm_(student.parameters(), 1.0)
        optimizer.step()
        optimizer.zero_grad()
        
        # Update memory
        memory.update_from_hidden_states(
            student_outputs['last_hidden_state'].detach()
        )
        
        # Add to replay buffer
        replay_buffer.add(
            input_ids=input_ids.detach(),
            attention_mask=attention_mask.detach(),
            labels=labels.detach(),
            priority=loss.item()
        )
        
        # Log
        print(f"Step {step+1}/10:")
        print(f"  Loss: {loss.item():.4f}")
        print(f"  Distill: {loss_dict['distill_loss'].item():.4f}")
        print(f"  Task: {loss_dict['task_loss']:.4f if torch.is_tensor(loss_dict['task_loss']) else loss_dict['task_loss']}")
        
        # Memory stats
        if step % 5 == 0:
            mem_stats = memory.get_memory_stats()
            buf_stats = replay_buffer.get_stats()
            print(f"  Memory util: {mem_stats['memory_utilization']:.2%}")
            print(f"  Buffer: {buf_stats['current_size']}/{buf_stats['buffer_size']}")
    
    print("\n" + "="*60)
    print("Training completed!")
    print(f"Final memory utilization: {memory.get_memory_stats()['memory_utilization']:.2%}")
    print(f"Final buffer size: {len(replay_buffer)}/{replay_buffer.buffer_size}")
    print("="*60)


if __name__ == "__main__":
    main()
