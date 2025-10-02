Compiler Error Message Rewriting (AI Tutor)
• Task: Train a transformer-based model to rewrite compiler error messages into human-friendly explanations with suggested fixes.
• Assignment Deliverable: Take GCC/Clang error outputs and produce user-friendly diagnostic feedback (like IntelliJ or VSCode AI assistants).

Plan for the project
- For what model to use, we can maybe use `BERT`(transformer) for phase 1, understanding the error and then `GPT` for phase 2, generating the natural language like error, or any text to text converter that already exists(this is also a transformer but we are gonna have to fine tune this one to better work with errors)`T5` is an example given by google
- For giving natural language like response for the errors, we are gonna have to either manually write a dataset for errors(I couldn’t find any existing dataset as of now, but we can try searching a bit more first)
- or we can scrape data from stack overflow, not that hard, ig we can use beautiful soup(i only know this, there could be alternatives), look at the html and tell it to look for cpp/gcc/error in the header etc, and we can probably get the data that way
- in my opinion, we should be storing the errors as `(error, text_message)` format, this can help us maintain tensors, make dfs later if we wanna use dfs, anything, and one of the suggestions by google was to use json format for storing the errors, if we are  scraping the data, yeah probably a good idea