import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from lexer import TokenScanner
from parser import SyntaxProcessor
from code_generator import AssemblyTranslator


class CompilerInterface:
    """Main GUI for the compiler application"""
    
    def __init__(self, window):
        self.window = window
        self.window.title("Mini Compiler - By Soma Das")
        self.window.geometry("1400x850")
        self.window.configure(bg='#1e1e1e')
        
        # Initialize compiler components
        self.scanner = TokenScanner()
        self.scanner.initialize()
        self.processor = SyntaxProcessor()
        self.processor.initialize()
        self.translator = AssemblyTranslator()
        
        self.build_interface()
        
    def build_interface(self):
        """Build the GUI components"""
        container = ttk.Frame(self.window, padding="10")
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)
        
        # Input Section
        input_panel = ttk.LabelFrame(container, text="Input Code", padding="10")
        input_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.code_input = scrolledtext.ScrolledText(input_panel, width=50, height=30,
                                                    font=('Consolas', 10))
        self.code_input.pack(fill=tk.BOTH, expand=True)
        
        # Updated sample code with comprehensive scope testing
        example = """int x;
int y;
x = 10;
y = 20;
/* Calculate sum */
int sum;
sum = x + y;
print(sum);

// If block with local scope
if (x < y) {
    int diff;  // Local to if block
    diff = y - x;
    print(diff);
    int localVar;
    localVar = diff * 2;
}

// While loop with local scope
int counter;
counter = 0;
while (counter < 5) {
    int temp;  // Local to while block
    temp = counter * 2;
    print(temp);
    counter = counter + 1;
    
    if (temp > 6) {
        int nested;  // Nested scope variable
        nested = temp - 6;
    }
}

// Test arithmetic operations
int a;
int b;
int result;
a = 15;
b = 3;
result = a + b;  // Addition
print(result);
result = a - b;  // Subtraction
print(result);
result = a * b;  // Multiplication
print(result);
result = a / b;  // Division
print(result);
result = a % b;  // Modulo
print(result);

// Test comparison operations
if (a == b) {
    print(1);
}
if (a != b) {
    print(2);
}
if (a > b) {
    print(3);
}
if (a < b) {
    print(4);
}
if (a >= b) {
    print(5);
}
if (a <= b) {
    print(6);
}
"""
        self.code_input.insert('1.0', example)
        
        # Control Buttons
        controls = ttk.Frame(container)
        controls.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(controls, text="Compile", command=self.run_compilation).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Reset", command=self.reset_all).pack(side=tk.LEFT, padx=5)
        
        # Output Section
        output_panel = ttk.LabelFrame(container, text="Compilation Results", padding="10")
        output_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.tabs = ttk.Notebook(output_panel)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        
        # Create output tabs
        self.make_tab("Token Stream", "tok_view")
        self.make_tab("Symbol Table", "var_view")
        self.make_tab("IR Code", "ir_view")
        self.make_tab("Assembly", "asm_view")
        self.make_tab("Issues", "err_view")
        
    def make_tab(self, label, attr):
        """
        Create a new tab in the output notebook
        
        Args:
            label: Tab label
            attr: Attribute name for the text widget
        """
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text=label)
        
        view = scrolledtext.ScrolledText(frame, width=60, height=30, font=('Consolas', 9))
        view.pack(fill=tk.BOTH, expand=True)
        setattr(self, attr, view)  # FIXED: was setattr(self, view, view)
        
    def run_compilation(self):
        """Execute the compilation pipeline"""
        src = self.code_input.get('1.0', tk.END)
        
        # Clear all output views
        for view in ['tok_view', 'var_view', 'ir_view', 'asm_view', 'err_view']:
            getattr(self, view).delete('1.0', tk.END)
        
        # Clear symbol table before compilation
        self.processor.registry.clear()
        
        # Phase 1: Lexical Analysis
        tokens, lex_errs = self.scanner.scan(src)
        
        tok_display = "TOKEN STREAM\n" + "="*70 + "\n\n"
        tok_display += f"{'Type':<18} {'Value':<18} {'Line':<8}\n"
        tok_display += "-"*70 + "\n"
        for tok in tokens:
            tok_display += f"{tok['kind']:<18} {str(tok['val']):<18} {tok['ln']:<8}\n"
        
        self.tok_view.insert('1.0', tok_display)
        
        # Phase 2 & 3: Syntax Analysis & Semantic Analysis
        self.processor.process(src)

        # Symbol Table Display with scope information
        var_display = "SYMBOL TABLE\n" + "="*100 + "\n\n"
        var_display += f"{'Identifier':<18} {'Type':<12} {'Value':<12} {'Context':<15} {'Scope':<20} {'Level':<8}\n"
        var_display += "-"*100 + "\n"
        for entry in self.processor.registry.all_entries():
            val_str = str(entry['val']) if entry['val'] is not None else 'None'
            var_display += f"{entry['id']:<18} {entry['dtype']:<12} {val_str:<12} {entry['ctx']:<15} {entry['scope']:<20} {entry['scope_level']:<8}\n"
        
        self.var_view.insert('1.0', var_display)
        
        # Intermediate Representation Display
        ir_display = "INTERMEDIATE REPRESENTATION\n" + "="*70 + "\n\n"
        for idx, instr in enumerate(self.processor.ir_instructions):
            op = instr['op']
            s1 = instr['src1']
            s2 = instr['src2']
            d = instr['dst']
            
            if op == 'assign':
                ir_display += f"{idx+1}. {d} := {s1}\n"
            elif op in ['+', '-', '*', '/', '%']:
                ir_display += f"{idx+1}. {d} := {s1} {op} {s2}\n"
            elif op in ['<', '<=', '>', '>=', '==', '!=']:
                ir_display += f"{idx+1}. {d} := {s1} {op} {s2}\n"
            elif op == 'mark':
                ir_display += f"{idx+1}. {s1}:\n"
            elif op == 'jump':
                ir_display += f"{idx+1}. goto {s1}\n"
            elif op == 'jump_if_false':
                ir_display += f"{idx+1}. if_false {s1} goto {s2}\n"
            elif op == 'output':
                ir_display += f"{idx+1}. print {s1}\n"
            else:
                ir_display += f"{idx+1}. {op} {s1} {s2} {d}\n"
        
        self.ir_view.insert('1.0', ir_display)
        
        # Phase 4: Code Generation
        asm = self.translator.translate(self.processor.ir_instructions)
        asm_display = "ASSEMBLY OUTPUT\n" + "="*70 + "\n\n"
        asm_display += "\n".join(asm)
        
        self.asm_view.insert('1.0', asm_display)
        
        # Error/Issue Display
        all_errs = lex_errs + self.processor.issues
        if all_errs:
            err_display = "COMPILATION ISSUES\n" + "="*70 + "\n\n"
            for idx, err in enumerate(all_errs, 1):
                err_display += f"{idx}. {err}\n"
            self.err_view.insert('1.0', err_display)
            messagebox.showwarning("Issues Found", f"Detected {len(all_errs)} issue(s)")
        else:
            self.err_view.insert('1.0', "✓ Compilation completed successfully!")
            messagebox.showinfo("Success", "Code compiled without errors!")
        
    def reset_all(self):
        """Clear all input and output fields"""
        self.code_input.delete('1.0', tk.END)
        for view in ['tok_view', 'var_view', 'ir_view', 'asm_view', 'err_view']:
            getattr(self, view).delete('1.0', tk.END)
        
        # Clear symbol table
        self.processor.registry.clear()
