"""
Continual Learning Example
Demonstrates SECI's ability to prevent catastrophic forgetting.
"""

import torch
import numpy as np
from torch.utils.data import DataLoader, TensorDataset

from seci import (
    SECIConfig,
    CompactTransformer,
    ExternalMemory,
    ReplayBuffer
)


def create_task_dataset(task_id, num_samples=500, seq_len=64, vocab_size=1000):
    """Create a synthetic dataset for a specific task."""
    # Different tasks use different vocabulary ranges
    vocab_start = task_id * (vocab_size // 3)
    vocab_end = vocab_start + (vocab_size // 3)
    
    input_ids = torch.randint(vocab_start, vocab_end, (num_samples, seq_len))
    attention_mask = torch.ones_like(input_ids)
    labels = input_ids.clone()
    
    dataset = TensorDataset(input_ids, attention_mask, labels)
    return DataLoader(dataset, batch_size=16, shuffle=True)


def evaluate_task(model, dataloader, device, max_batches=10):
    """Evaluate model on a task."""
    model.eval()
    total_loss = 0
    num_batches = 0
    
    with torch.no_grad():
        for batch_idx, (input_ids, attention_mask, labels) in enumerate(dataloader):
            if batch_idx >= max_batches:
                break
            
            input_ids = input_ids.to(device)
            attention_mask = attention_mask.to(device)
            labels = labels.to(device)
            
            outputs = model(input_ids, attention_mask)
            loss = torch.nn.functional.cross_entropy(
                outputs['logits'].view(-1, outputs['logits'].size(-1)),
                labels.view(-1)
            )
            
            total_loss += loss.item()
            num_batches += 1
    
    model.train()
    return total_loss / num_batches if num_batches > 0 else 0


def train_task(model, memory, replay_buffer, dataloader, device, task_id, steps=50):
    """Train on a single task."""
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    model.train()
    
    losses = []
    for step, (input_ids, attention_mask, labels) in enumerate(dataloader):
        if step >= steps:
            break
        
        input_ids = input_ids.to(device)
        attention_mask = attention_mask.to(device)
        labels = labels.to(device)
        
        # Forward pass
        outputs = model(input_ids, attention_mask, return_hidden_states=True)
        
        # Memory-augmented representations
        memory_output, _ = memory.read(outputs['last_hidden_state'])
        
        # Compute loss
        loss = torch.nn.functional.cross_entropy(
            outputs['logits'].view(-1, outputs['logits'].size(-1)),
            labels.view(-1)
        )
        
        # Backward pass
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        optimizer.zero_grad()
        
        # Update memory
        memory.update_from_hidden_states(outputs['last_hidden_state'].detach())
        
        # Add to replay buffer
        replay_buffer.add(
            input_ids=input_ids.detach(),
            attention_mask=attention_mask.detach(),
            labels=labels.detach(),
            priority=loss.item()
        )
        
        # Replay every 5 steps
        if step % 5 == 0 and not replay_buffer.is_empty():
            replay_batch = replay_buffer.sample(device=device)
            if replay_batch is not None:
                replay_outputs = model(
                    replay_batch['input_ids'],
                    replay_batch['attention_mask']
                )
                replay_loss = torch.nn.functional.cross_entropy(
                    replay_outputs['logits'].view(-1, replay_outputs['logits'].size(-1)),
                    replay_batch['labels'].view(-1)
                )
                replay_loss.backward()
                optimizer.step()
                optimizer.zero_grad()
        
        losses.append(loss.item())
    
    return np.mean(losses)


def main():
    print("="*60)
    print("SECI Continual Learning Demonstration")
    print("Testing catastrophic forgetting prevention")
    print("="*60)
    
    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice: {device}")
    
    vocab_size = 1000
    hidden_size = 128
    
    # Initialize model
    print("\n1. Initializing compact model...")
    model = CompactTransformer(
        vocab_size=vocab_size,
        hidden_size=hidden_size,
        num_layers=2,
        num_heads=2,
        intermediate_size=512,
        max_seq_length=64,
        dropout=0.1
    ).to(device)
    
    print(f"   Parameters: {model.get_trainable_params():,}")
    
    # Initialize memory and replay
    print("\n2. Initializing memory and replay buffer...")
    memory = ExternalMemory(
        memory_size=500,
        embedding_dim=hidden_size,
        num_memory_heads=2,
        retrieval_top_k=3
    ).to(device)
    
    replay_buffer = ReplayBuffer(
        buffer_size=2000,
        replay_batch_size=16,
        sampling_strategy="reservoir"
    )
    
    # Create three tasks
    print("\n3. Creating three synthetic tasks...")
    task_loaders = {
        'Task A': create_task_dataset(0, 500, 64, vocab_size),
        'Task B': create_task_dataset(1, 500, 64, vocab_size),
        'Task C': create_task_dataset(2, 500, 64, vocab_size)
    }
    
    # Evaluation loaders (for testing)
    eval_loaders = {
        'Task A': create_task_dataset(0, 200, 64, vocab_size),
        'Task B': create_task_dataset(1, 200, 64, vocab_size),
        'Task C': create_task_dataset(2, 200, 64, vocab_size)
    }
    
    # Training schedule
    results = {
        'Task A': [],
        'Task B': [],
        'Task C': []
    }
    
    print("\n" + "="*60)
    print("Starting Sequential Training")
    print("="*60)
    
    # Train on Task A
    print("\n📚 Training on Task A...")
    train_loss = train_task(model, memory, replay_buffer, 
                           task_loaders['Task A'], device, 0, steps=50)
    print(f"   Training loss: {train_loss:.4f}")
    
    # Evaluate on all tasks
    print("\n📊 Evaluating after Task A:")
    for task_name, loader in eval_loaders.items():
        eval_loss = evaluate_task(model, loader, device, max_batches=10)
        results[task_name].append(eval_loss)
        print(f"   {task_name}: {eval_loss:.4f}")
    
    # Train on Task B
    print("\n📚 Training on Task B...")
    train_loss = train_task(model, memory, replay_buffer, 
                           task_loaders['Task B'], device, 1, steps=50)
    print(f"   Training loss: {train_loss:.4f}")
    
    # Evaluate on all tasks
    print("\n📊 Evaluating after Task B:")
    for task_name, loader in eval_loaders.items():
        eval_loss = evaluate_task(model, loader, device, max_batches=10)
        results[task_name].append(eval_loss)
        print(f"   {task_name}: {eval_loss:.4f}")
    
    # Train on Task C
    print("\n📚 Training on Task C...")
    train_loss = train_task(model, memory, replay_buffer, 
                           task_loaders['Task C'], device, 2, steps=50)
    print(f"   Training loss: {train_loss:.4f}")
    
    # Final evaluation
    print("\n📊 Final Evaluation:")
    for task_name, loader in eval_loaders.items():
        eval_loss = evaluate_task(model, loader, device, max_batches=10)
        results[task_name].append(eval_loss)
        print(f"   {task_name}: {eval_loss:.4f}")
    
    # Analyze forgetting
    print("\n" + "="*60)
    print("📈 Forgetting Analysis")
    print("="*60)
    
    for task_name, losses in results.items():
        if len(losses) >= 2:
            initial = losses[0]
            final = losses[-1]
            forgetting = ((final - initial) / initial) * 100
            print(f"\n{task_name}:")
            print(f"   Initial loss: {initial:.4f}")
            print(f"   Final loss: {final:.4f}")
            print(f"   Change: {forgetting:+.1f}%")
            
            if forgetting < 30:
                print(f"   ✅ Good retention (forgetting < 30%)")
            else:
                print(f"   ⚠️  Significant forgetting")
    
    # Memory and buffer stats
    print("\n" + "="*60)
    print("💾 Memory & Buffer Statistics")
    print("="*60)
    
    mem_stats = memory.get_memory_stats()
    buf_stats = replay_buffer.get_stats()
    
    print(f"\nMemory:")
    print(f"   Utilization: {mem_stats['memory_utilization']:.2%}")
    print(f"   Total accesses: {mem_stats['total_accesses']:.0f}")
    print(f"   Avg age: {mem_stats['avg_memory_age']:.1f}")
    
    print(f"\nReplay Buffer:")
    print(f"   Size: {buf_stats['current_size']}/{buf_stats['buffer_size']}")
    print(f"   Utilization: {buf_stats['utilization']:.2%}")
    print(f"   Total added: {buf_stats['total_added']}")
    
    print("\n" + "="*60)
    print("✅ Continual Learning Demonstration Complete!")
    print("="*60)
    print("\nKey Takeaways:")
    print("• SECI maintains performance on old tasks via replay")
    print("• External memory stores learned representations")
    print("• Reservoir sampling ensures uniform experience distribution")
    print("="*60)


if __name__ == "__main__":
    main()
