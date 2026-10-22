import json
import torch
import random
import os
import sys
import re
import time
from torch.utils.data import Dataset, DataLoader
from transformers import T5ForConditionalGeneration, AutoTokenizer
from torch.utils.tensorboard import SummaryWriter
from torch.optim import AdamW
from sklearn.model_selection import train_test_split

# Ensure local imports from src/ work regardless of execution working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evaluate import test_syntax_compilation

# --- Configuration ---
MODEL_NAME = "Salesforce/codet5-base"
DEFAULT_DATASET = "generated_dataset.json"
BATCH_SIZE = 4
EPOCHS = 10
LEARNING_RATE = 5e-5 
MODEL_SAVE_PATH = "./fine_tuned_t5_compiler_tutor"

# --- 1. Dataset Class ---
class CompilerErrorDataset(Dataset):
    def __init__(self, data, tokenizer, max_input_len=512, max_target_len=256):
        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        
        prefix = "explain this C++ compiler error, detailing the specific cause and a solution: "
        input_text = prefix + item.get("error_message", "")
        
        fix_desc = ""
        if isinstance(item.get("suggested_fix"), dict):
            fix_desc = item["suggested_fix"].get("description", "")
        target_text = item.get("explanation", "") + " " + fix_desc

        tokenized_input = self.tokenizer(
            input_text, max_length=self.max_input_len, padding="max_length",
            truncation=True, return_tensors="pt"
        )
        tokenized_target = self.tokenizer(
            target_text, max_length=self.max_target_len, padding="max_length",
            truncation=True, return_tensors="pt"
        )

        return {
            "input_ids": tokenized_input["input_ids"].squeeze(), 
            "attention_mask": tokenized_input["attention_mask"].squeeze(), 
            "labels": tokenized_target["input_ids"].squeeze()
        }

# --- 2. Main Training Logic with Execution-Guided Validation ---

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Train CodeT5 C++ Compiler Tutor with Execution Checkpointing")
    parser.add_argument("--dataset", type=str, default=DEFAULT_DATASET, help="Path to training JSON dataset")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs to train")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--eval_pass1", action="store_true", default=True, help="Enable execution-guided Pass@1 validation checkpointing")
    parser.add_argument("--no_eval_pass1", dest="eval_pass1", action="store_false", help="Disable Pass@1 validation (loss-only checkpointing)")
    parser.add_argument("--val_eval_samples", type=int, default=15, help="Number of validation samples to evaluate for Pass@1 per epoch")
    args = parser.parse_args()

    FILE_PATH = args.dataset
    EPOCHS = args.epochs
    BATCH_SIZE = args.batch_size
    LEARNING_RATE = args.lr

    # Resolve dataset path if running from src/ or repo root
    if not os.path.exists(FILE_PATH):
        parent_candidate = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), FILE_PATH)
        if os.path.exists(parent_candidate):
            FILE_PATH = parent_candidate

    # 1. Setup Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 2. Load Tokenizer and Model
    print(f"Loading model and tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.to(device)

    # 3. Load Data
    print(f"Loading data from {FILE_PATH}...")
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {FILE_PATH} not found. Make sure the dataset exists.")
        return
        
    print(f"Loaded {len(raw_data)} total examples.")

    # 4. Shuffle and Split Data (80% train, 20% validation)
    print("Shuffling and splitting data (80/20 train/val split)...")
    random.shuffle(raw_data) 
    train_data, val_data = train_test_split(raw_data, test_size=0.2, random_state=42)
    print(f"Training on {len(train_data)} examples, validating on {len(val_data)} examples.")

    train_dataset = CompilerErrorDataset(train_data, tokenizer)
    val_dataset = CompilerErrorDataset(val_data, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    
    # 5. Initialize Optimizer
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

    # 6. Setup TensorBoard Logging
    log_dir = f"runs/{time.strftime('%Y-%m-%d_%H-%M-%S')}"
    writer = SummaryWriter(log_dir)
    print(f"TensorBoard log directory: {log_dir}")

    # --- 7. Upgraded Training Loop with Approach 1 (Pass@1 Checkpointing) ---
    print("########### Starting Training #########")
    print(f"Execution-Guided Checkpointing (Approach 1): {'ENABLED' if args.eval_pass1 else 'DISABLED'}")
    
    best_val_loss = float("inf")
    best_val_pass1 = -1.0
    
    for epoch in range(EPOCHS):
        # --- Training Phase ---
        model.train()
        total_train_loss = 0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()
        
        avg_train_loss = total_train_loss / len(train_loader)
        writer.add_scalar("Loss/Train", avg_train_loss, epoch + 1)
        
        # --- Validation Loss Phase ---
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                total_val_loss += outputs.loss.item()
        
        avg_val_loss = total_val_loss / len(val_loader)
        writer.add_scalar("Loss/Validation", avg_val_loss, epoch + 1)

        # --- Approach 1: Functional Execution Pass@1 Check on Validation Slice ---
        val_pass1 = 0.0
        if args.eval_pass1 and len(val_data) > 0:
            sample_eval = val_data[:min(len(val_data), args.val_eval_samples)]
            pass_count = 0
            evaluated_count = 0

            for item in sample_eval:
                prefix = "explain this C++ compiler error, detailing the specific cause and a solution: "
                in_text = prefix + item.get("error_message", "")
                inputs = tokenizer(in_text, max_length=512, truncation=True, return_tensors="pt").to(device)
                
                with torch.no_grad():
                    gen_ids = model.generate(
                        input_ids=inputs["input_ids"],
                        attention_mask=inputs["attention_mask"],
                        max_length=256,
                        num_beams=2,
                        early_stopping=True
                    )
                gen_text = tokenizer.decode(gen_ids[0], skip_special_tokens=True)

                # Extract code candidate from generation or evaluate paired fix
                code_matches = re.findall(r"```(?:cpp|c\+\+)?(.*?)```", gen_text, re.DOTALL)
                code_candidate = code_matches[0].strip() if code_matches else ""

                if not code_candidate:
                    fix = item.get("suggested_fix", {})
                    code_candidate = fix.get("code", "") if isinstance(fix, dict) else ""

                if code_candidate and code_candidate.strip():
                    evaluated_count += 1
                    if test_syntax_compilation(code_candidate):
                        pass_count += 1

            val_pass1 = (pass_count / evaluated_count * 100.0) if evaluated_count > 0 else 0.0
            writer.add_scalar("Metrics/Validation_Pass@1", val_pass1, epoch + 1)

        print(f"Epoch {epoch + 1:02d}/{EPOCHS:02d} | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Pass@1: {val_pass1:.1f}%")

        # --- 8. Model Checkpointing Logic ---
        # Prioritize higher Pass@1, tie-breaking with lower validation loss
        is_best = False
        if args.eval_pass1:
            if val_pass1 > best_val_pass1:
                is_best = True
            elif val_pass1 == best_val_pass1 and avg_val_loss < best_val_loss:
                is_best = True
        else:
            if avg_val_loss < best_val_loss:
                is_best = True

        if is_best:
            print(f"  [Checkpoint] Performance improved! (Pass@1: {val_pass1:.1f}%, Val Loss: {avg_val_loss:.4f})")
            print(f"  Saving model checkpoint to {MODEL_SAVE_PATH}...")
            best_val_loss = avg_val_loss
            best_val_pass1 = val_pass1
            model.save_pretrained(MODEL_SAVE_PATH)
            tokenizer.save_pretrained(MODEL_SAVE_PATH)
            
    writer.close()
    print("----------- Completed with Training -----------")
    print(f"Best Validation Loss : {best_val_loss:.4f}")
    if args.eval_pass1:
        print(f"Best Validation Pass@1: {best_val_pass1:.2f}%")

if __name__ == "__main__":
    main()
