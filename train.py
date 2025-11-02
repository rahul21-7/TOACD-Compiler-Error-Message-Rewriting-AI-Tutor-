import torch
import json
from torch.utils.data import Dataset, DataLoader
from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch.optim import AdamW
from prepare_data import CompilerErrorDataset

MODEL_NAME = 't5-small'
FILE_PATH = 'generated_dataset.json'
BATCH_SIZE = 4
EPOCHS = 30  # With a small dataset, we can train for more epochs.
LEARNING_RATE = 3e-4 # A common learning rate for fine-tuning.
MODEL_SAVE_PATH = './fine_tuned_t5_compiler_tutor'

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