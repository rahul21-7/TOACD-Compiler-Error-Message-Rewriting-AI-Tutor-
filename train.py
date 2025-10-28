import torch
import json
from torch.utils.data import Dataset, DataLoader
from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch.optim import AdamW

MODEL_NAME = 't5-small'
FILE_PATH = 'generated_dataset.json'
BATCH_SIZE = 4
EPOCHS = 30  # With a small dataset, we can train for more epochs.
LEARNING_RATE = 3e-4 # A common learning rate for fine-tuning.
MODEL_SAVE_PATH = './fine_tuned_t5_compiler_tutor'

# --- Phase 1: Custom PyTorch Dataset (Copied from our previous script) ---
# We include this class definition here to make the script self-contained.

class CompilerErrorDataset(Dataset):
    def __init__(self, data, tokenizer, max_input_len=512, max_target_len=256):
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

    def __getitem__(self, index):
        """
        This method is required by PyTorch. It fetches a single data sample at the given index.
        The DataLoader will call this method to create a batch.
        """
        source_ids = self.inputs[index]["input_ids"].squeeze()
        target_ids = self.targets[index]["input_ids"].squeeze()
        source_mask = self.inputs[index]["attention_mask"].squeeze()

        return {
            "input_ids":source_ids,
            "attention_mask":source_mask,
            "labels":target_ids
        }

    def _build(self):
        """
        A helper method to loop through the raw data and tokenize it.
        """
        print("Tokenizinng data...")
        for item in self.data:
            prefix = "explain C++ error: "
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

def  main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device {device}")

    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    model =  T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.to(device)

    with open(FILE_PATH, "r") as f:
        raw_data = json.load(f)

    dataset = CompilerErrorDataset(raw_data, tokenizer)
    data_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    optimizer = AdamW(model.parameters(), lr = LEARNING_RATE)

    print("###########Starting  training#########")

    model.train()


    for epoch in range(EPOCHS):
        total_loss = 0
        for batch in data_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            #Clear previous gradients
            optimizer.zero_grad

            #Forward Pass: Feed the data to the model

            outputs = model(
                input_ids = input_ids,
                attention_mask = attention_mask,
                labels = labels
            )

            #calculating/getting the loss(error)
            loss = outputs.loss

            #backwards pass
            loss.backward()

            #optimizer's step: update the model's weights and biases
            optimizer.step()

            total_loss += loss.item() #maintaing the total error for displaying avg error

        avg_loss = total_loss/len(data_loader)
        print(f"Epoch :{epoch+1}/{EPOCHS}| Average loss : {avg_loss:.4f}")

    print("-----------Completed with Training-----------")

    print(f"Saving model to {MODEL_SAVE_PATH}")
    model.save_pretrained(MODEL_SAVE_PATH)
    tokenizer.save_pretrained(MODEL_SAVE_PATH)
    print("Model saved succesfully!")


if __name__ == "__main__":
    main()