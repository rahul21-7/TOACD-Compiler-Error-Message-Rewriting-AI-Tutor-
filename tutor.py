import subprocess
import sys
import torch
from inference import explain_error, load_model

#config

MODEL_PATH = "./fine_tuned_t5_compiler_tutor"
COMPILER_TO_USE = "g++"

def main():
    args = sys.argv[1:]

    if not args:
        print(f"Usage: python tutor.py <arguments_for_compiler>")
        print(f"Example : python tutor.py main.cpp -o main")
        sys.exit(1)

    #build and run real compiler command

    command = [COMPILER_TO_USE] + args
    print(f"--- Running compiler : {' '.join(command)} ---")

    #subprocess for running executing the command
    result = subprocess.run(
        command,
        capture_output=True,
        text = True
    ) 

    compile_error_message = result.stderr

    if not compile_error_message:
        #Success
        print("--- Compile successful ---")
        if result.stdout:
            print(result.stdout)
    else:
        #Failure
        print("--- Original Compiler error ---")
        print(compile_error_message)

        #AI mode
        try:
            print("--- Friendly explanation ---")
            friendly_explanation = explain_error(compile_error_message)
            print(friendly_explanation)
        except Exception as e:
            print(f"Error calling the model : {e}")
    
if __name__ == "__main__":
    main()
