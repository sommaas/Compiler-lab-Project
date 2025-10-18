## Mini Compiler
A complete compiler implementation with graphical user interface, featuring all major compilation phases from lexical analysis to assembly code generation.

<img width="1393" height="665" alt="Screenshot_1754" src="https://github.com/user-attachments/assets/f6ee4693-383a-4317-af23-d7ea6525c9a7" />

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PLY](https://img.shields.io/badge/PLY-3.11-orange.svg)

## ✨ Features

- **Complete Compilation Pipeline**: Lexical Analysis → Syntax Analysis → Semantic Analysis → Intermediate Code Generation → Assembly Code Generation
- **Interactive GUI**: User-friendly interface built with Tkinter
- **Real-time Compilation**: Instant feedback on code compilation
- **Multi-tab Output View**: Separate tabs for tokens, symbol table, IR code, assembly, and errors
- **Comprehensive Error Reporting**: Detailed lexical and syntax error messages
- **Symbol Table Management**: Track variable declarations and scopes
- **Three-Address Code Generation**: Clean intermediate representation
- **Assembly Code Output**: Generate pseudo-assembly code

## 🏗️ Architecture

```
┌─────────────────┐
│   Source Code   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Token Scanner   │ ◄─── Lexical Analysis
│  (Lexer/PLY)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Syntax Processor │ ◄─── Syntax Analysis
│   (Parser/PLY)  │      Semantic Analysis
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Variable Registry│ ◄─── Symbol Table
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IR Generator   │ ◄─── Intermediate Code
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Assembly Transl. │ ◄─── Code Generation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Assembly Output │
└─────────────────┘
```

## 📝 Supported Language Features

### Data Types
- `int` - Integer numbers
- `float` - Floating-point numbers

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Relational**: `<`, `<=`, `>`, `>=`, `==`, `!=`
- **Assignment**: `=`

### Control Structures
- `if` statements
- `if-else` statements
- `while` loops

### Other Features
- Variable declarations
- Variable assignments
- `print()` statements
- Code blocks with `{}`
- Comments (coming soon)

## 🔄 Compilation Phases

### 1. **Lexical Analysis (Token Scanner)**
   - Converts source code into tokens
   - Identifies keywords, identifiers, operators, and literals
   - Detects illegal characters

### 2. **Syntax Analysis (Syntax Processor)**
   - Parses tokens according to grammar rules
   - Builds abstract syntax tree (AST)
   - Detects syntax errors

### 3. **Semantic Analysis**
   - Checks variable declarations
   - Validates variable usage
   - Type checking (basic)
   - Detects undefined variables and redeclarations

### 4. **Intermediate Code Generation**
   - Generates three-address code
   - Creates temporary variables
   - Produces labels for control flow

### 5. **Code Generation (Assembly Translator)**
   - Converts IR to assembly code
   - Performs register allocation
   - Generates pseudo-assembly instructions

## 📄 Example Code

```c
int x;
int y;
x = 10;
y = 20;
int sum;
sum = x + y;
print(sum);

if (x < y) {
    int diff;
    diff = y - x;
    print(diff);
}

int counter;
counter = 0;
while (counter < 5) {
    counter = counter + 1;
}
```

### Expected Output

**Token Stream:**
```
IDENTIFIER       x                Line 1
IDENTIFIER       y                Line 2
INTEGER          10               Line 3
...
```

**Variable Registry:**
```
x               int             main
y               int             main
sum             int             main
...
```

**IR Code:**
```
1. x := 10
2. y := 20
3. temp1 := x + y
4. sum := temp1
5. print sum
...
```

**Assembly:**
```assembly
; Generated Assembly Code
section .data
section .text
global main
main:
    MOV AX, 10
    MOV BX, 20
    ADD CX, AX, BX
    ...
```

## Generated Files

When I run the compiler for the first time, PLY (Python Lex-Yacc) automatically generates two files:

### `parsetab.py`
- **Purpose**: Contains the compiled parser table
- **Size**: ~50-100 KB
- **Description**: Pre-computed LALR parsing tables for efficient parsing
- **Can be deleted?**: Yes, will be regenerated on next run
- **Should be in git?**: No, add to `.gitignore`

### `parser.out`
- **Purpose**: Debug information about the parser
- **Size**: ~10-30 KB
- **Description**: Contains grammar rules, states, and shift/reduce actions
- **Can be deleted?**: Yes, will be regenerated on next run

## 📚 Dependencies

- **Python 3.8+**: Core programming language
- **Tkinter**: GUI framework (usually comes with Python)
- **PLY (Python Lex-Yacc) 3.11**: Lexer and parser generator
  ```bash
  pip install ply
  ```

### requirements.txt
```
ply>=3.11
```

## 🛠️ Technical Details

### Lexer Tokens
```python
Keywords: if, else, while, for, int, float, return, print
Identifiers: [a-zA-Z_][a-zA-Z_0-9]*
Literals: integers, decimals
Operators: +, -, *, /, %, =, ==, !=, <, <=, >, >=
Delimiters: (, ), {, }, ;, ,
```

### Grammar
```bnf
program → statement_list
statement → declaration | assignment | print | if | while | block
declaration → type IDENTIFIER ;
assignment → IDENTIFIER = expression ;
expression → term ((+|-) term)*
term → factor ((*|/|%) factor)*
factor → NUMBER | IDENTIFIER | (expression)
```

## Author
- Course: CSE 430 - Compiler Design
- Soma Das - 21201111
