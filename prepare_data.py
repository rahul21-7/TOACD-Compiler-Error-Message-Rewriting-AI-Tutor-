import torch
from transformers import T5ForConditionalGeneration, AutoTokenizer
from torch.utils.data import DataLoader, Dataset

MODEL_NAME = 'Salesforce/codet5-base'
DATASET_PATH = '.'
FILE_NAME = 'error_dataset.json'
BATCH_SIZE = 4
MAX_INPUT_LEN = 512
MAX_TARGET_LEN = 256

#this module is later called in the train.py file for tokenizing the data before training

class CompilerErrorDataset(Dataset):
    def __init__(self, data, tokenizer, max_input_len=512, max_target_len=256):
        """
        The constructor for our dataset. This is where we do the one-time setup,
        like loading data into memory and tokenizing it.
        
        Args:
            data (list of dicts): The loaded data from our JSON file.
            tokenizer: The T5 tokenizer instance.
            max_input_len (int): Maximum sequence length for the input.
            max_target_len (int): Maximum sequence length for the output.
        """

        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len
        self.data = data

        self.inputs = []
        self.targets = []

        self._build()

    def __len__(self):
        """
        This method is required by PyTorch. It returns the total number of samples.
        """
        return len(self.inputs)

    def _build(self):
        """
        A helper method to loop through the raw data and tokenize it.
        """
        print("Tokenizinng data...")
        for item in self.data:
            prefix = "explain this C++ compiler error, detailing the specific cause and a solution:"
            input_text = prefix+item["error_message"]
            target_text = item["explanation"]

            #tokenize the input
            tokenized_input = self.tokenizer(
                input_text,
                max_length=self.max_input_len,
                padding='max_length',
                truncation=True,
                return_tensors="pt" # Return PyTorch tensors
            )

            #tokenize the output
            tokenized_target = self.tokenizer(
                target_text,
                max_length=self.max_target_len,
                padding='max_length',
                truncation=True,
                return_tensors="pt" # Return PyTorch tensors
            )

            self.inputs.append(tokenized_input)
            self.targets.append(tokenized_target)

    def __getitem__(self, index):
        """
        This method is required by PyTorch. It fetches a single data sample at the given index.
        The DataLoader will call this method to create a batch.
        """
        source_ids = self.inputs[index]["input_ids"].squeeze()
        target_ids = self.targets[index]["input_ids"].squeeze()
        
        source_mask = self.inputs[index]["attention_mask"].squeeze()
        
        return {
            "input_ids": source_ids, 
            "attention_mask": source_mask, 
            "labels": target_ids
        }

import json

def load_data():
    try:
        with open(FILE_NAME, "r") as f:
            raw_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Coudn't open the file due to the error : {e}")
        return

    print("Successfully imported the dataset")
    print(f"Number of examples: {len(raw_data)}")
    print("First example (raw):")
    print(raw_data[0])
    print("-" * 30)
    return raw_data

def main():
    raw_data = load_data()
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("\n--- Building Custom Dataset and DataLoader ---")

    custom_dataset = CompilerErrorDataset(
        raw_data,
        tokenizer,
        MAX_INPUT_LEN,
        MAX_TARGET_LEN
    )

    data_loader = DataLoader(
        custom_dataset,
        batch_size = BATCH_SIZE,
        shuffle = True
    )

    print("\nCustom Dataset and DataLoader created successfully!")
    print(f"Number of batches: {len(data_loader)}")

    first_batch = next(iter(data_loader))
    print("Shape of 'input_ids' in one batch:", first_batch['input_ids'].shape)
    print("Shape of 'attention_mask' in one batch:", first_batch['attention_mask'].shape)
    print("Shape of 'labels' in one batch:", first_batch['labels'].shape)
    print("This batch is ready to be fed into a model for training.")
    print("-" * 30)

if __name__ == '__main__':
    main()