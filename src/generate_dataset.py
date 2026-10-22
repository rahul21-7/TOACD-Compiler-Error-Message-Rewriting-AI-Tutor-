import subprocess
import json
import os
import shlex

# --- Configuration ---
# Change this to 'clang++' if you prefer
COMPILER_TO_USE = 'g++' 
OUTPUT_FILENAME = 'generated_dataset.json'
TEMP_CPP_FILE = '_temp.cpp'

#this will make a dataset(still prototype) which has 25 entries, this can be used to train the model to a level where it atleast gives some output, not just padding tags(<padding>), also increased the no of epochs in the model to make sure the error is minimized further and global minima is reached by the model thus the predictions are better


ERROR_JOBS = [
    {
        "id": "gen-semicolon-01",
        "error_type": "Missing Semicolon",
        "broken_code": "int main() { int x = 5 return 0; }",
        "explanation": "In C++, statements must end with a semicolon (;). This symbol tells the compiler where one instruction ends and the next begins. You are missing one at the end of the line where you declare 'x'.",
        "suggested_fix": { "type": "code_modification", "description": "Add a semicolon to the end of the line.", "code": "int x = 5;" }
    },
    {
        "id": "gen-cout-no-include-01",
        "error_type": "Undeclared Identifier (cout)",
        "broken_code": "int main() { cout << \"Hello\"; return 0; }",
        "explanation": "The compiler does not recognize 'cout'. 'cout' is part of the C++ standard library. To use it, you must first include the <iostream> header file and specify that 'cout' belongs to the standard namespace ('std').",
        "suggested_fix": { "type": "code_addition", "description": "Add '#include <iostream>' and 'using namespace std;'.", "code": "#include <iostream>\n\nint main() {\n    std::cout << \"Hello\";\n    return 0;\n}" }
    },
    {
        "id": "gen-vector-no-include-01",
        "error_type": "Undeclared Type (vector)",
        "broken_code": "int main() { std::vector<int> numbers; return 0; }",
        "explanation": "The compiler does not recognize 'vector'. 'vector' is a template defined in the standard library. To use it, you must first include the <vector> header file.",
        "suggested_fix": { "type": "code_addition", "description": "Add '#include <vector>' at the top of your file.", "code": "#include <vector>\n" }
    },
    {
        "id": "gen-string-no-include-01",
        "error_type": "Undeclared Type (string)",
        "broken_code": "int main() { std::string s = \"hello\"; return 0; }",
        "explanation": "The compiler does not recognize 'string'. 'string' is a type defined in the standard library. To use it, you must first include the <string> header file.",
        "suggested_fix": { "type": "code_addition", "description": "Add '#include <string>' at the top of your file.", "code": "#include <string>\n" }
    },
    {
        "id": "gen-undeclared-var-01",
        "error_type": "Undeclared Identifier",
        "broken_code": "int main() { int x = 5; y = x + 2; return 0; }",
        "explanation": "You are trying to use a variable 'y' that has not been declared. In C++, you must declare a variable (e.g., 'int y;') before you can assign a value to it or use it in an expression.",
        "suggested_fix": { "type": "code_modification", "description": "Declare 'y' as an integer before using it.", "code": "int x = 5;\nint y;\ny = x + 2;" }
    },
    {
        "id": "gen-missing-brace-01",
        "error_type": "Missing Brace",
        "broken_code": "int main() { int x = 5; return 0;",
        "explanation": "The compiler reached the end of the file while expecting a closing curly brace '}'. This usually means you have an opening brace '{' for a function (like 'main') that was never closed.",
        "suggested_fix": { "type": "code_addition", "description": "Add a closing brace '}' at the end of the main function.", "code": "}\n" }
    },
    {
        "id": "gen-type-mismatch-01",
        "error_type": "Type Mismatch",
        "broken_code": "int main() { int x = \"hello\"; return 0; }",
        "explanation": "You are trying to assign a text string literal (\"hello\") to a variable 'x' that is declared to hold an integer (int). C++ is a strongly-typed language and will not allow this implicit conversion.",
        "suggested_fix": { "type": "code_modification", "description": "Change the type of 'x' to 'const char*' or 'std::string'.", "code": "#include <string>\nstd::string x = \"hello\";" }
    },
    {
        "id": "gen-too-few-args-01",
        "error_type": "Incorrect Function Call",
        "broken_code": "void myFunction(int a, int b) { }\nint main() { myFunction(5); return 0; }",
        "explanation": "You are calling the function 'myFunction' with only one argument, but it was defined to accept exactly two arguments. You must provide a value for each parameter.",
        "suggested_fix": { "type": "code_modification", "description": "Pass the required number of arguments to the function.", "code": "myFunction(5, 10);" }
    },
    {
        "id": "gen-too-many-args-01",
        "error_type": "Incorrect Function Call",
        "broken_code": "void myFunction(int a) { }\nint main() { myFunction(5, 10); return 0; }",
        "explanation": "You are calling the function 'myFunction' with two arguments, but it was defined to accept only one. You must provide the exact number of arguments the function expects.",
        "suggested_fix": { "type": "code_modification", "description": "Pass only one argument to the function.", "code": "myFunction(5);" }
    },
    {
        "id": "gen-const-assign-01",
        "error_type": "Assignment to Read-Only Variable",
        "broken_code": "int main() { const int x = 10; x = 20; return 0; }",
        "explanation": "You declared 'x' as a 'const' (constant), which means its value cannot be changed after it is initialized. The compiler is correctly stopping you from assigning a new value to this read-only variable.",
        "suggested_fix": { "type": "code_modification", "description": "If the variable needs to be changed, remove the 'const' keyword from its declaration.", "code": "int x = 10;\nx = 20;" }
    },
    {
        "id": "gen-dot-on-pointer-01",
        "error_type": "Member Access Error",
        "broken_code": "struct MyStruct { int val; };\nint main() { MyStruct* s = new MyStruct(); s.val = 10; return 0; }",
        "explanation": "You are using the dot operator (.) to access a member of 's', but 's' is a pointer. In C++, you must use the arrow operator (->) to access members of an object through a pointer.",
        "suggested_fix": { "type": "code_modification", "description": "Change the dot operator (.) to an arrow operator (->).", "code": "s->val = 10;" }
    },
    {
        "id": "gen-arrow-on-object-01",
        "error_type": "Member Access Error",
        "broken_code": "struct MyStruct { int val; };\nint main() { MyStruct s; s->val = 10; return 0; }",
        "explanation": "You are using the arrow operator (->) to access a member of 's', but 's' is a direct object, not a pointer. In C++, you must use the dot operator (.) to access members of an object directly.",
        "suggested_fix": { "type": "code_modification", "description": "Change the arrow operator (->) to a dot operator (.).", "code": "s.val = 10;" }
    },
    {
        "id": "gen-cout-no-namespace-01",
        "error_type": "Undeclared Identifier (cout)",
        "broken_code": "#include <iostream>\nint main() { cout << \"Hello\"; return 0; }",
        "explanation": "You included <iostream>, but 'cout' is still undeclared. This is because 'cout' is in the 'std' (standard) namespace. You must either prefix it with 'std::' (as in 'std::cout') or add 'using namespace std;' to your code.",
        "suggested_fix": { "type": "code_modification", "description": "Use 'std::cout' to specify the namespace.", "code": "std::cout << \"Hello\";" }
    },
    {
        "id": "gen-cin-no-include-01",
        "error_type": "Undeclared Identifier (cin)",
        "broken_code": "int main() { int x; cin >> x; return 0; }",
        "explanation": "The compiler does not recognize 'cin'. 'cin' is the standard input stream and is defined in the <iostream> header file. You must include <iostream> and specify the 'std' namespace.",
        "suggested_fix": { "type": "code_addition", "description": "Add '#include <iostream>' and use 'std::cin'.", "code": "#include <iostream>\n\nint main() {\n    int x;\n    std::cin >> x;\n    return 0;\n}" }
    },
    {
        "id": "gen-redeclaration-01",
        "error_type": "Redeclaration",
        "broken_code": "int main() { int x = 5; int x = 10; return 0; }",
        "explanation": "You are trying to declare a variable named 'x' twice in the same scope. C++ does not allow you to redefine a variable that already exists in that block of code.",
        "suggested_fix": { "type": "code_modification", "description": "Use a different name for the second variable or re-assign the first one without 'int'.", "code": "int x = 5;\nx = 10;" }
    },
    {
        "id": "gen-const-to-non-const-ref-01",
        "error_type": "Const Correctness",
        "broken_code": "void func(int &x) { x = 10; }\nint main() { const int y = 5; func(y); return 0; }",
        "explanation": "You are passing a 'const' variable 'y' to a function 'func' that takes a non-const reference ('int &x'). This is not allowed because the function 'func' promises to modify 'x', which would break the 'const' promise of 'y'.",
        "suggested_fix": { "type": "code_modification", "description": "Change the function parameter to 'const int &x' if it doesn't need to modify 'x', or pass a non-const variable.", "code": "void func(const int &x) { /* can't modify x */ }" }
    },
    {
        "id": "gen-private-access-01",
        "error_type": "Access Control",
        "broken_code": "class MyClass { private: int x; };\nint main() { MyClass m; m.x = 10; return 0; }",
        "explanation": "You are trying to access the member variable 'x' from outside the 'MyClass' class. However, 'x' is declared as 'private', meaning it can only be accessed by other members of 'MyClass'.",
        "suggested_fix": { "type": "code_modification", "description": "Make 'x' public, or create a public member function (a 'setter') to modify 'x'.", "code": "class MyClass { public: int x; };" }
    },
    {
        "id": "gen-static-this-01",
        "error_type": "Static Member Error",
        "broken_code": "class MyClass { int x; static void func() { this->x = 10; } };\nint main() { return 0; }",
        "explanation": "You are trying to use the 'this' keyword inside a 'static' member function. Static functions belong to the class itself, not to any specific object instance. Therefore, there is no 'this' (no object) to refer to.",
        "suggested_fix": { "type": "code_modification", "description": "Make the function non-static if it needs to access member variables, or remove the use of 'this'.", "code": "class MyClass { int x; void func() { this->x = 10; } };" }
    },
    {
        "id": "gen-no-constructor-01",
        "error_type": "No Matching Constructor",
        "broken_code": "class MyClass { public: MyClass(int a) {} };\nint main() { MyClass m; return 0; }",
        "explanation": "You are trying to create an object 'm' using the default constructor ('MyClass m;'), but you have defined a custom constructor 'MyClass(int a)'. Once you define *any* constructor, the compiler no longer provides a default one automatically.",
        "suggested_fix": { "type": "code_modification", "description": "Either provide an argument (e.g., 'MyClass m(10);') or explicitly define a default constructor 'MyClass() {}').", "code": "class MyClass { public: MyClass(int a) {} MyClass() {} };\nint main() { MyClass m; return 0; }" }
    },
    {
        "id": "gen-void-assignment-01",
        "error_type": "Invalid Assignment",
        "broken_code": "void func() {}\nint main() { int x = func(); return 0; }",
        "explanation": "You are trying to assign the result of the function 'func' to an integer variable 'x'. However, 'func' is declared as 'void', meaning it does not return any value. You cannot assign 'void' to a variable.",
        "suggested_fix": { "type": "code_modification", "description": "Either make 'func' return an 'int', or call 'func' without assigning its result.", "code": "void func() {}\nint main() { func(); return 0; }" }
    },
    {
        "id": "gen-division-by-zero-01",
        "error_type": "Division by Zero",
        "broken_code": "int main() { int x = 10 / 0; return 0; }",
        "explanation": "The compiler has detected that you are attempting to divide an integer by the constant value zero. This is an undefined operation in mathematics and is not allowed. This is a compile-time error because the compiler can see the '0' directly.",
        "suggested_fix": { "type": "code_modification", "description": "Change the divisor to a non-zero value.", "code": "int x = 10 / 1;" }
    },
    {
        "id": "gen-non-bool-if-01",
        "error_type": "Type Mismatch (if statement)",
        "broken_code": "#include <string>\nint main() { std::string s = \"hello\"; if (s) {} return 0; }",
        "explanation": "You are using a 'std::string' object 's' as the condition in an 'if' statement. The 'if' statement expects a boolean value (true or false), or something that can be converted to one. 'std::string' does not automatically convert to 'bool'.",
        "suggested_fix": { "type": "code_modification", "description": "Check a property of the string instead, like 'if (!s.empty())'.", "code": "#include <string>\nint main() { std::string s = \"hello\"; if (!s.empty()) {} return 0; }" }
    },
    {
        "id": "gen-missing-template-type-01",
        "error_type": "Syntax Error (Template)",
        "broken_code": "template <T> class MyClass { T data; };\nint main() { return 0; }",
        "explanation": "When declaring a template, you must use the 'typename' or 'class' keyword to tell the compiler that 'T' is a type parameter. You have written 'template <T>' instead of 'template <typename T>'.",
        "suggested_fix": { "type": "code_modification", "description": "Add the 'typename' keyword before 'T'.", "code": "template <typename T> class MyClass { T data; };" }
    },
    {
        "id": "gen-no-semicolon-class-01",
        "error_type": "Missing Semicolon (Class)",
        "broken_code": "class MyClass { public: int x; }\nint main() { return 0; }",
        "explanation": "You are missing a semicolon (;) at the end of your class definition. In C++, class and struct definitions must be followed by a semicolon.",
        "suggested_fix": { "type": "code_addition", "description": "Add a semicolon after the closing brace '}' of the class.", "code": "class MyClass { public: int x; };\n" }
    },
    {
        "id": "gen-map-no-include-01",
        "error_type": "Undeclared Type (map)",
        "broken_code": "#include <string>\nint main() { std::map<std::string, int> myMap; return 0; }",
        "explanation": "The compiler does not recognize 'map'. 'map' is a template defined in the standard library. To use it, you must first include the <map> header file.",
        "suggested_fix": { "type": "code_addition", "description": "Add '#include <map>' at the top of your file.", "code": "#include <map>\n" }
    },
    {
        "id": "gen-mismatched-return-01",
        "error_type": "Type Mismatch (Return)",
        "broken_code": "int func() { return \"hello\"; }",
        "explanation": "Your function 'func' is declared to return an 'int', but you are trying to return a string literal (\"hello\"). The return type must match the function's declaration.",
        "suggested_fix": { "type": "code_modification", "description": "Either change the function's return type to 'std::string' (and include <string>) or return an integer.", "code": "int func() { return 0; }" }
    },
    {
        "id": "gen-break-no-loop-01",
        "error_type": "Syntax Error (break)",
        "broken_code": "int main() { break; return 0; }",
        "explanation": "The 'break' statement can only be used inside a loop (like 'for' or 'while') or a 'switch' statement. You are using it in the main body of a function.",
        "suggested_fix": { "type": "code_removal", "description": "Remove the 'break' statement, as it is not inside a loop or switch.", "code": "int main() { return 0; }" }
    },
    {
        "id": "gen-else-no-if-01",
        "error_type": "Syntax Error ('else' without 'if')",
        "broken_code": "int main() { else { } return 0; }",
        "explanation": "The 'else' keyword is used to provide an alternative block of code if an 'if' statement is false. You have an 'else' block without a preceding 'if' block.",
        "suggested_fix": { "type": "code_modification", "description": "Add an 'if' statement before the 'else' block or remove the 'else' block.", "code": "int main() { if (false) { } else { } return 0; }" }
    },
    {
        "id": "gen-array-negative-size-01",
        "error_type": "Array Size Error",
        "broken_code": "int main() { int arr[-5]; return 0; }",
        "explanation": "You are trying to declare an array with a negative size (-5). An array's size must be a positive integer.",
        "suggested_fix": { "type": "code_modification", "description": "Change the array size to a positive number.", "code": "int arr[5];" }
    },
    {
        "id": "gen-switch-non-int-01",
        "error_type": "Syntax Error (switch)",
        "broken_code": "#include <string>\nint main() { std::string s = \"hi\"; switch(s) { case \"hi\": break; } return 0; }",
        "explanation": "The 'switch' statement in C++ can only evaluate integral types (like 'int', 'char', 'enum') and cannot be used with types like 'std::string'.",
        "suggested_fix": { "type": "code_modification", "description": "Use a series of 'if' and 'else if' statements to compare strings.", "code": "#include <string>\nint main() { std::string s = \"hi\"; if (s == \"hi\") { } return 0; }" }
    },
    {
        "id": "gen-abstract-class-01",
        "error_type": "Abstract Class Instantiation",
        "broken_code": "class Base { virtual void func() = 0; };\nint main() { Base b; return 0; }",
        "explanation": "You are trying to create an instance of the class 'Base'. However, 'Base' is an 'abstract class' because it contains a 'pure virtual function' ('func() = 0'). You cannot create objects of an abstract class.",
        "suggested_fix": { "type": "code_modification", "description": "Create a new class that inherits from 'Base', implements the 'func' function, and then create an instance of that new class.", "code": "class Base { virtual void func() = 0; };\nclass Derived : public Base { public: void func() override {} };\nint main() { Derived d; return 0; }" }
    },
    {
        "id": "gen-set-no-include-01",
        "error_type": "Undeclared Type (set)",
        "broken_code": "int main() { std::set<int> mySet; return 0; }",
        "explanation": "The compiler does not recognize 'set'. 'set' is a template defined in the standard library. To use it, you must first include the <set> header file.",
        "suggested_fix": { "type": "code_addition", "description": "Add '#include <set>' at the top of your file.", "code": "#include <set>\n" }
    },
    {
        "id": "gen-const-member-no-init-01",
        "error_type": "Missing Initialization (const)",
        "broken_code": "class MyClass { const int x; };\nint main() { MyClass m; return 0; }",
        "explanation": "You have a 'const' member variable 'x' that is not initialized. 'const' members *must* be initialized in the constructor's member initializer list.",
        "suggested_fix": { "type": "code_modification", "description": "Add a constructor and initialize 'x' in the initializer list.", "code": "class MyClass { const int x; public: MyClass() : x(10) {} };" }
    },
    {
        "id": "gen-ref-member-no-init-01",
        "error_type": "Missing Initialization (reference)",
        "broken_code": "class MyClass { int& ref; };\nint main() { int a = 5; MyClass m; return 0; }",
        "explanation": "You have a reference member variable 'ref' that is not initialized. Reference members *must* be initialized in the constructor's member initializer list to refer to an object.",
        "suggested_fix": { "type": "code_modification", "description": "Add a constructor that initializes the reference 'ref'.", "code": "class MyClass { int& ref; public: MyClass(int& r) : ref(r) {} };\nint main() { int a = 5; MyClass m(a); return 0; }" }
    },
    {
        "id": "gen-typo-namespace-01",
        "error_type": "Undeclared Identifier (Typo)",
        "broken_code": "#include <iostream>\nint main() { std::coutt << \"hi\"; return 0; }",
        "explanation": "The compiler does not recognize 'coutt'. It looks like this is a typo for 'cout', which is the standard output stream. Check your spelling.",
        "suggested_fix": { "type": "code_modification", "description": "Correct the typo from 'coutt' to 'cout'.", "code": "std::cout << \"hi\";" }
    },
    {
        "id": "gen-typo-keyword-01",
        "error_type": "Syntax Error",
        "broken_code": "int main() { retun 0; }",
        "explanation": "The compiler does not recognize 'retun'. It looks like this is a typo for the 'return' keyword. Check your spelling.",
        "suggested_fix": { "type": "code_modification", "description": "Correct the typo from 'retun' to 'return'.", "code": "return 0;" }
    },
    {
        "id": "gen-template-no-type-01",
        "error_type": "Syntax Error (Template)",
        "broken_code": "#include <vector>\nint main() { std::vector<> v; return 0; }",
        "explanation": "You are using the 'std::vector' template, but you have not specified what type of elements the vector should hold. You must provide a type inside the angle brackets.",
        "suggested_fix": { "type": "code_modification", "description": "Provide a type inside the <...>, for example '<int>'.", "code": "#include <vector>\nint main() { std::vector<int> v; return 0; }" }
    },
    {
        "id": "gen-call-non-function-01",
        "error_type": "Syntax Error",
        "broken_code": "int main() { int x = 10; x(5); return 0; }",
        "explanation": "You are trying to 'call' the variable 'x' as if it were a function, using parentheses 'x(5)'. However, 'x' is an 'int' variable, not a function.",
        "suggested_fix": { "type": "code_removal", "description": "Remove the 'x(5)' call. If you meant to assign, use 'x = 5;'.", "code": "int x = 10; x = 5;" }
    },
    {
        "id": "gen-main-wrong-return-01",
        "error_type": "Syntax Error (main return)",
        "broken_code": "void main() { }",
        "explanation": "You have declared 'main' with a 'void' return type. In standard C++, the 'main' function must be declared to return an 'int' (integer).",
        "suggested_fix": { "type": "code_modification", "description": "Change the return type of 'main' from 'void' to 'int'.", "code": "int main() { return 0; }" }
    },
    {
        "id": "gen-bad-alloc-01",
        "error_type": "Array Size Error",
        "broken_code": "int main() { int *arr = new int[-100]; return 0; }",
        "explanation": "You are trying to allocate an array on the heap using 'new' with a negative size. Array sizes must be positive, non-zero values.",
        "suggested_fix": { "type": "code_modification", "description": "Use a positive size for the array allocation.", "code": "int *arr = new int[100];" }
    },
    {
        "id": "gen-delete-non-pointer-01",
        "error_type": "Syntax Error (delete)",
        "broken_code": "int main() { int x = 5; delete x; return 0; }",
        "explanation": "The 'delete' operator is used to free memory that was allocated with 'new'. You are trying to use 'delete' on a stack variable 'x'. This is not allowed.",
        "suggested_fix": { "type": "code_removal", "description": "Remove the 'delete x;' line. Stack variables are automatically destroyed.", "code": "int main() { int x = 5; return 0; }" }
    },
    
    # --- HERE ARE THE FIXED VERSIONS OF ALL YOUR FAILING JOBS ---
    
    {
        "id": "gen-for-loop-syntax-01", # Replaces gen-for-loop-semicolon-01
        "error_type": "Syntax Error (for loop)",
        "broken_code": "int main() { for(int i = 0; i < 5 i++) { } return 0; }",
        "explanation": "You have a syntax error inside your 'for' loop's header. You are missing a semicolon (;) between the condition 'i < 5' and the increment 'i++'.",
        "suggested_fix": { "type": "code_modification", "description": "Add the missing semicolon.", "code": "for(int i = 0; i < 5; i++) { }" }
    },
    {
        "id": "gen-use-before-declaration-01", # Replaces gen-missing-return-01
        "error_type": "Undeclared Identifier (Function)",
        "broken_code": "int main() { int x = getValue(); return 0; }\nint getValue() { return 10; }",
        "explanation": "You are calling the function 'getValue' before it has been declared. In C++, the compiler reads from top to bottom, and it doesn't know what 'getValue' is. You must provide a declaration (a 'prototype') before 'main'.",
        "suggested_fix": { "type": "code_addition", "description": "Add a function prototype 'int getValue();' before your main function.", "code": "int getValue();\nint main() { int x = getValue(); return 0; }\nint getValue() { return 10; }" }
    },
    {
        "id": "gen-linker-no-main-01", # Fixed version
        "error_type": "Linker Error (no main)",
        "command_flags": [COMPILER_TO_USE], # No '-c', forces linker
        "broken_code": "#include <iostream>\nvoid foo() { std::cout << \"hi\"; }",
        "explanation": "This is a linker error. The code compiled successfully, but the linker could not find a 'main' function. The 'main' function is the required entry point for all C++ programs.",
        "suggested_fix": { "type": "code_addition", "description": "Add a 'main' function to your program.", "code": "int main() { foo(); return 0; }" }
    },
    {
        "id": "gen-linker-undefined-func-01", # Fixed version
        "error_type": "Linker Error (undefined reference)",
        "command_flags": [COMPILER_TO_USE], # No '-c', forces linker
        "broken_code": "void foo();\nint main() { foo(); return 0; }",
        "explanation": "This is a linker error. You declared a function 'void foo()' (a prototype), but you never provided its definition (the actual function body). The compiler trusted you, but the linker couldn't find the function's code.",
        "suggested_fix": { "type": "code_addition", "description": "Provide a definition for the 'foo' function.", "code": "void foo() { /* do nothing */ }\nint main() { foo(); return 0; }" }
    },
    {
        "id": "gen-ambiguous-call-01", # Fixed version
        "error_type": "Ambiguous Function Call",
        "broken_code": "void func(long i) {}\nvoid func(float f) {}\nint main() { func(0); return 0; }",
        "explanation": "You are calling 'func' with an integer literal (0). The compiler is confused because an 'int' can be promoted to either a 'long' or a 'float', and both 'func(long)' and 'func(float)' are equally valid matches. The call is ambiguous.",
        "suggested_fix": { "type": "code_modification", "description": "Explicitly cast '0' to the type you intend to call, e.g., 'func(0L);' for long or 'func(0.0f);' for float.", "code": "func(0.0f);" }
    },
    {
        "id": "gen-array-bad-size-01", # Fixed version
        "error_type": "Array Size Error (VLA)",
        "command_flags": [COMPILER_TO_USE, '-c', '-pedantic-errors'],
        "broken_code": "int main() { int n = 5; int arr[n]; return 0; }",
        "explanation": "You are using a variable 'n' to set the size of a C-style array. This is a non-standard C++ extension called a 'Variable Length Array' (VLA). We are forcing the compiler to be strict, which is why this is an error.",
        "suggested_fix": { "type": "code_modification", "description": "Use 'std::vector' for dynamic-sized arrays or make 'n' a 'const'.", "code": "#include <vector>\nint main() { int n = 5; std::vector<int> arr(n); return 0; }" }
    },
    {
        "id": "gen-static-member-no-def-01", # Fixed version
        "error_type": "Linker Error (Undefined Reference)",
        "command_flags": [COMPILER_TO_USE], # No '-c', forces linker
        "broken_code": "#include <iostream>\nstruct S { static int x; };\nint main() { std::cout << S::x; return 0; }",
        "explanation": "This is a linker error. You declared a 'static' member variable 'x' inside your struct 'S', but you never defined it. Static members must be defined outside the class, exactly once.",
        "suggested_fix": { "type": "code_addition", "description": "Add the definition of the static member 'x' in the global scope.", "code": "struct S { static int x; };\nint S::x = 5; // Add this definition\nint main() { std::cout << S::x; return 0; }" }
    },
    {
        "id": "gen-missing-if-parens-01", # Replaces gen-double-semicolon-01
        "error_type": "Syntax Error (if)",
        "broken_code": "int main() { int x = 5; if x > 0 {} return 0; }",
        "explanation": "You are missing the parentheses '(...)' around the condition in your 'if' statement. In C++, all 'if' conditions must be wrapped in parentheses.",
        "suggested_fix": { "type": "code_modification", "description": "Add parentheses around the condition 'x > 0'.", "code": "if (x > 0) {}" }
    },
    {
        "id": "gen-if-assignment-01", # Fixed version
        "error_type": "Syntax Error (if)",
        "command_flags": [COMPILER_TO_USE, '-c', '-Werror=parentheses'], # Force this specific warning to be an error
        "broken_code": "int main() { int x = 0; if (x = 5) { } return 0; }",
        "explanation": "You are using a single equals sign '=' in your 'if' statement's condition. This is an assignment ('x = 5'), not a comparison ('x == 5'). The compiler is treating this as an error because it's almost always a mistake.",
        "suggested_fix": { "type": "code_modification", "description": "Use the double equals '==' operator to check for equality.", "code": "if (x == 5)" }
    }
]

def main():
    """
    Main function to generate the dataset.
    """
    print(f"Starting dataset generation with '{COMPILER_TO_USE}'...")
    
    # Check if compiler is available
    try:
        subprocess.run([COMPILER_TO_USE, '-v'], capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"Error: Compiler '{COMPILER_TO_USE}' not found.")
        print("Please install it or change the 'COMPILER_TO_USE' variable in this script.")
        return

    dataset = []

    for job in ERROR_JOBS:
        # 1. Write the broken code to the temp file
        try:
            with open(TEMP_CPP_FILE, 'w') as f:
                f.write(job['broken_code'])
        except IOError as e:
            print(f"Error writing temp file: {e}")
            continue

        # 2. Run the compiler and capture output
        #    Use '-c' as default, but allow jobs to override flags
        default_command_flags = [COMPILER_TO_USE, '-c']
        
        # Get custom command flags from the job, or use the default
        command_flags = job.get("command_flags", default_command_flags)
        
        # Add the temp file to the command
        command = command_flags + [TEMP_CPP_FILE]
            
        result = subprocess.run(command, capture_output=True, text=True)
        
        # 3. The error message is in stderr
        error_message = result.stderr.strip()
        
        # 4. Clean up error message paths for consistency
        #    Replaces the temp file's name with a generic 'source.cpp'
        error_message = error_message.replace(TEMP_CPP_FILE, 'source.cpp')

        if not error_message:
            print(f"Warning: Job '{job['id']}' produced no error. Skipping.")
            continue
            
        # 5. Build the final JSON object
        full_data_point = {
            "id": job['id'],
            "compiler": COMPILER_TO_USE,
            "error_type": job['error_type'],
            "error_message": error_message,
            "explanation": job['explanation'],
            "suggested_fix": job['suggested_fix']
        }
        dataset.append(full_data_point)

    # 6. Clean up the temp file
    try:
        if os.path.exists(TEMP_CPP_FILE):
            os.remove(TEMP_CPP_FILE)
    except OSError as e:
        print(f"Warning: Could not remove temp file: {e}")

    # 7. Save the final dataset
    try:
        with open(OUTPUT_FILENAME, 'w') as f:
            json.dump(dataset, f, indent=2)
    except IOError as e:
        print(f"Error writing dataset file: {e}")
        return

    print(f"\nSuccessfully generated {len(dataset)} data points.")
    print(f"Dataset saved to '{OUTPUT_FILENAME}'")

if __name__ == "__main__":
    main()