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


    load_model()

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
        #clean the error first
        filename = None

        for arg in args:
            if arg.endswith(".cpp") or arg.endswith(".c"):
                filename = arg.split('/')[-1].split('\\')[-1]

        clean_error = ""
        if filename:
            essential_lines = []
            for line in compile_error_message.splitlines():
                if filename in line:
                    essential_lines.append(line)
                
            clean_error = "\n".join(essential_lines)
        else:
            clean_error = compile_error_message
        try:
            
            print("--- Friendly explanation ---")
            friendly_explanation = explain_error(clean_error)
            print(friendly_explanation)
        except Exception as e:
            print(f"Error calling the model : {e}")
    
if __name__ == "__main__":
    main()
