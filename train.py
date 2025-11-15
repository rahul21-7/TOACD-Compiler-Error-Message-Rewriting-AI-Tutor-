import json
import torch
import random
from torch.utils.data import Dataset, DataLoader
from transformers import T5ForConditionalGeneration, AutoTokenizer
from torch.utils.tensorboard import SummaryWriter
from torch.optim import AdamW
import time
from sklearn.model_selection import train_test_split

# --- Configuration ---
MODEL_NAME = "Salesforce/codet5-base"
FILE_PATH = 'generated_dataset.json' # Your 4,000-item dataset
BATCH_SIZE = 4
EPOCHS = 10 # We can run for more epochs, we will only save the best
LEARNING_RATE = 5e-5 
MODEL_SAVE_PATH = './fine_tuned_t5_compiler_tutor'

# --- 1. Your new, improved Dataset Class ---
# We put it directly inside train.py
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
        
        # Your new, specific prompt
        prefix = "explain this C++ compiler error, detailing the specific cause and a solution: "
        input_text = prefix + item['error_message']
        
        # Your new, enriched target text
        target_text = item["explanation"] + " " + item["suggested_fix"]["description"]

        tokenized_input = self.tokenizer(
            input_text, max_length=self.max_input_len, padding='max_length',
            truncation=True, return_tensors="pt"
        )
        tokenized_target = self.tokenizer(
            target_text, max_length=self.max_target_len, padding='max_length',
            truncation=True, return_tensors="pt"
        )

        return {
            "input_ids": tokenized_input["input_ids"].squeeze(), 
            "attention_mask": tokenized_input["attention_mask"].squeeze(), 
            "labels": tokenized_target["input_ids"].squeeze()
        }

# --- 2. The Main Training Logic ---

def main():
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
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {FILE_PATH} not found. Did you run generate_dataset.py?")
        return
        
    print(f"Loaded {len(raw_data)} total examples.")

    # --- 4. CRITICAL FIX: Shuffle and Split the Data ---
    print("Shuffling and splitting data...")
    
    # First, shuffle the entire dataset to break lazy patterns
    random.shuffle(raw_data) 
    
    # Split: 80% for training, 20% for validation (the "quiz")
    train_data, val_data = train_test_split(raw_data, test_size=0.2, random_state=42)
    print(f"Training on {len(train_data)} examples, validating on {len(val_data)} examples.")

    train_dataset = CompilerErrorDataset(train_data, tokenizer)
    val_dataset = CompilerErrorDataset(val_data, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    
    # 5. Initialize Optimizer
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

    # 6. Setup TensorBoard
    log_dir = f"runs/{time.strftime('%Y-%m-%d_%H-%M-%S')}"
    writer = SummaryWriter(log_dir)
    print(f"TensorBoard log directory: {log_dir}")

    # --- 7. The Upgraded Training Loop ---
    print("########### Starting Training #########")
    
    best_val_loss = float('inf') # Track the best "quiz score"
    
    for epoch in range(EPOCHS):
        # --- Training Phase ---
        model.train()
        total_train_loss = 0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()
        
        avg_train_loss = total_train_loss / len(train_loader)
        writer.add_scalar("Training Loss", avg_train_loss, epoch + 1)
        
        # --- Validation Phase (The "Quiz") ---
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                
                loss = outputs.loss
                total_val_loss += loss.item()
        
        avg_val_loss = total_val_loss / len(val_loader)
        writer.add_scalar("Validation Loss", avg_val_loss, epoch + 1)
        
        print(f"Epoch: {epoch + 1}/{EPOCHS} | Avg Train Loss: {avg_train_loss:.4f} | Avg Val Loss: {avg_val_loss:.4f}")

        # --- 8. Save Only the Best Model ---
        if avg_val_loss < best_val_loss:
            print(f"Validation loss improved! Saving model to {MODEL_SAVE_PATH}")
            best_val_loss = avg_val_loss
            model.save_pretrained(MODEL_SAVE_PATH)
            tokenizer.save_pretrained(MODEL_SAVE_PATH)
            
    writer.close()
    print("----------- Completed with Training -----------")
    print(f"Best validation loss: {best_val_loss:.4f}")

if __name__ == '__main__':
    main()