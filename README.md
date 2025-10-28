Compiler Error Message Rewriting (AI Tutor)
• Task: Train a transformer-based model to rewrite compiler error messages into human-friendly explanations with suggested fixes.
• Assignment Deliverable: Take GCC/Clang error outputs and produce user-friendly diagnostic feedback (like IntelliJ or VSCode AI assistants).

Plan for the project
- For what model to use, we can maybe use `BERT`(transformer) for phase 1, understanding the error and then `GPT` for phase 2, generating the natural language like error, or any text to text converter that already exists(this is also a transformer but we are gonna have to fine tune this one to better work with errors)`T5` is an example given by google
- For giving natural language like response for the errors, we are gonna have to either manually write a dataset for errors(I couldn’t find any existing dataset as of now, but we can try searching a bit more first)
- or we can scrape data from stack overflow, not that hard, ig we can use beautiful soup(i only know this, there could be alternatives), look at the html and tell it to look for cpp/gcc/error in the header etc, and we can probably get the data that way
-  we should be storing the errors as a json file, this can help us maintain tensors, make dfs later if we wanna use dfs, anything, and one of the suggestions by google was to use json format for storing the errors, if we are  scraping the data, yeah probably a good idea


Tasks completed until now
* everyone has gone through what to do and has read up on what is necessary for the project(AI part)
* the work has been split among 4 of us 2 of us will work on each model and we'll choose the better one at the end during the integration of these 2 models
* decided on using YACC datasets for parse tree errors training
* using a toy dataset to make a model for now due to unavailability of datasets, after searching for a bit more, we'll try to use the found, existing datasets, which seems like will not be possible, so we are planning to scrape github for errors and fixes, in the worst case we will generate the errors ourselves, but we are trying to use github
* used T5 transformer for generating tokens from the dataset
* used the tokens and made a model
* trainedd the model on the dataset to finetune it and saved the fine tuned model

* currently the model is being trained on a dataset that was generated with the help of Chat GPT, I plan on scraping github/leetcode/cf/stack overflow or some coding website to make a  dataset that can be used to train the model that we have made until now 

after scraping and cleanning the data it will be preprocessed to be in the format 
`{
    "id": "gcc-undeclared-cout-01",
    "compiler": "gcc",
    "error_type": "Undeclared Identifier",
    "error_message": "main.cpp: In function ‘int main()’:\nmain.cpp:4:5: error: ‘cout’ was not declared in this scope\n    4 |     cout << \"Hello, World!\";\n      |     ^~~~\nmain.cpp:2:1: note: ‘std::cout’ is defined in header ‘<iostream>’; did you forget to ‘#include <iostream>’? or a ‘using namespace std;’?",
    "explanation": "The compiler does not recognize 'cout'. 'cout' is part of the C++ standard library used for printing to the console. To use it, you must first include the <iostream> header file, and then specify that 'cout' belongs to the standard namespace ('std').",
    "suggested_fix": {
      "type": "code_modification",
      "description": "Add '#include <iostream>' at the top and use 'std::cout' to specify the namespace.",
      "code": "#include <iostream>\n\nint main() {\n  std::cout << \"Hello, World!\";\n  return 0;\n}"
    }
  }`
