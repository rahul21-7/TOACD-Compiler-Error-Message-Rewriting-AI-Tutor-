import torch
from transformers import T5ForConditionalGeneration, AutoTokenizer

MODEL_PATH = "./fine_tuned_t5_compiler_tutor"

def explain_error(error_message):
    """
    Takes the raw error message from the command line and returns the model's output
    """

    #select the device to use
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using the device {device}")

    #load tokenizer and model
    print(f"loading model from {MODEL_PATH}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)

    #move model into current device
    model.to(device)

    model.eval() #set model to eval mode

    prefix = "explain C++ error: "
    input_text = prefix+error_message

    #Tokenize input

    inputs = tokenizer(
        input_text,
        max_length = 512,
        padding = "max_length",
        truncation = True,
        return_tensors = "pt"
    )

    input_ids = inputs.input_ids.to(device)
    attention_mask = inputs.attention_mask.to(device)

    print("Generating explanation...")

    #inference mode to reduce the computation and not keep track of grads, etc

    with torch.no_grad():
        output_sequences = model.generate(
            input_ids = input_ids,
            attention_mask = attention_mask,
            max_length = 512, #max 
            num_beams = 4,
            early_stopping = True #stop when ccomplete sentence is formed 
        )
    
    generated_text = tokenizer.decode(
        output_sequences[0],
        skip_special_tokens = True
    )

    return generated_text

def main():
    test_error = """ main.cpp: In function ‘int main()’: main.cpp:4:5: error: ‘cout’ was not declared in this scope 4 | cout << "Hello, World!"; | ^~~~ main.cpp:2:1: note: ‘std::cout’ is defined in header ‘<iostream>’; did you forget to ‘#include <iostream>’? or a ‘using namespace std;’? """

    explanation = explain_error(test_error)

    print("\n" + "="*30)
    print("Compiler error:")
    print("="*30)
    print(test_error)
    print("\n" + "="*30)
    print("AI Explanation:")
    print("="*30)
    print(explanation)
    print("="*30)

if __name__ == "__main__":
    main()

#right now the model has been trained for 10 epochs and with a toy dataset, as a result it is not able to make accurate predictions but to prove that the model is trying to prerdict something, we can turn off skip_special_tokens

#as of now, the dataset is very small, we are yet to find a dataset for this as a  result we cannot demonstrate its working

#we have set the epochs to 20 for now and learning rate to be 0.003, this is giving me a good balance of running in a reasonable amount of time and getting the loss value to not skip the global minima

#we'll train the model one more  time for more epochs and will try to get the loss vakue close to 0.5 if possiible, if not, unfortunately, the demonstration can only be ddone after we find our dataset, we'll do it next week

# <pad> is a special token which is  padding which is the safest prediction for the transformer to make a prediction about, for the final code i"m enabling skip _special_tokens

#we are using beam search for generating words which will always give the best output(prediction), but the output that is being given right now is not good enough due to lack of data, after getting a better dataset from programming platforms, we will be able to improve the accuracy of our model