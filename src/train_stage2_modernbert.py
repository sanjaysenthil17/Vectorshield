"""
Vector-Shield: Stage 2 Neural Classifier Training (ModernBERT / DeBERTa)
AIDS Team 14 | Lead Architect: Vignesh V S (cb.ai.u4aid23057)

Fine-tunes a Transformer encoder (ModernBERT-base / DeBERTa-v3) for 
Stage 2 Deep Sequence Classification of stealthy & borderline prompt injections.
Compatible with NVIDIA GPUs (RTX 3050, A100, H100) and CPU.
"""

import os
import sys
import json
import argparse
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class PromptInjectionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long)
        }


def load_dataset(data_path):
    texts, labels = [], []
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}. Run dataset_scaler.py first.")

    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            texts.append(item["text"])
            labels.append(item["label"])

    return texts, labels


def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    print("=" * 60)
    print("🛡️ Vector-Shield: Stage 2 Neural Classifier Training")
    print(f"Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"Base Model: {args.model_name}")
    print(f"Batch Size: {args.batch_size} | Epochs: {args.epochs} | LR: {args.lr}")
    print("=" * 60)

    # 1. Load Data
    texts, labels = load_dataset(args.data_file)
    print(f"Loaded {len(texts)} samples (Clean: {labels.count(0)}, Injection: {labels.count(1)})")

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=args.val_split, random_state=42, stratify=labels
    )
    print(f"Split: {len(train_texts)} train, {len(val_texts)} validation")

    # 2. Tokenizer & Model
    print(f"Loading tokenizer & weights for {args.model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=2)
    model.to(device)

    # 3. DataLoaders
    train_dataset = PromptInjectionDataset(train_texts, train_labels, tokenizer, max_length=args.max_length)
    val_dataset = PromptInjectionDataset(val_texts, val_labels, tokenizer, max_length=args.max_length)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    # 4. Optimizer & Scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),
        num_training_steps=total_steps
    )

    use_amp = (device.type == "cuda") and args.fp16
    scaler = torch.cuda.amp.GradScaler() if use_amp else None

    # 5. Training Loop
    best_f1 = 0.0
    os.makedirs(args.output_dir, exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        total_train_loss = 0.0

        for step, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            b_labels = batch["labels"].to(device)

            optimizer.zero_grad()

            if use_amp:
                with torch.cuda.amp.autocast():
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=b_labels)
                    loss = outputs.loss
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=b_labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()

            scheduler.step()
            total_train_loss += loss.item()

        avg_train_loss = total_train_loss / len(train_loader)

        # Validation
        model.eval()
        all_preds, all_targets = [], []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                b_labels = batch["labels"].to(device)

                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
                all_preds.extend(preds)
                all_targets.extend(b_labels.cpu().numpy())

        acc = accuracy_score(all_targets, all_preds)
        prec, rec, f1, _ = precision_recall_fscore_support(all_targets, all_preds, average="binary", zero_division=0)

        print(f"Epoch {epoch+1}/{args.epochs} | Loss: {avg_train_loss:.4f} | "
              f"Val Acc: {acc*100:.2f}% | Prec: {prec*100:.2f}% | Rec: {rec*100:.2f}% | F1: {f1*100:.2f}%")

        if f1 > best_f1:
            best_f1 = f1
            print(f"  ⭐ New best F1 score ({best_f1*100:.2f}%). Saving checkpoint to {args.output_dir}...")
            model.save_pretrained(args.output_dir)
            tokenizer.save_pretrained(args.output_dir)

    print("\n" + "=" * 60)
    print("🎯 Training Complete! Final Classification Report on Validation Set:")
    print(classification_report(all_targets, all_preds, target_names=["Clean (0)", "Injection (1)"]))
    print(f"Model saved to: {args.output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Vector-Shield Stage 2 Neural Classifier")
    parser.add_argument("--data_file", type=str, default="data/vector_shield_scaled_corpus.jsonl",
                        help="Path to training jsonl dataset")
    parser.add_argument("--model_name", type=str, default="answerdotai/ModernBERT-base",
                        help="HuggingFace model ID (e.g. answerdotai/ModernBERT-base or microsoft/deberta-v3-small)")
    parser.add_argument("--output_dir", type=str, default="models/stage2_modernbert",
                        help="Output directory for saved weights")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size (16 for A100, 4 for RTX 3050)")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--max_length", type=int, default=256, help="Max sequence length")
    parser.add_argument("--val_split", type=float, default=0.2, help="Validation split fraction")
    parser.add_argument("--fp16", action="store_true", default=True, help="Use mixed precision fp16")
    parser.add_argument("--cpu", action="store_true", default=False, help="Force CPU training")

    args = parser.parse_args()
    train(args)
