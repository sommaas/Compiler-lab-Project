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
        
        # Default sample code
        example = """int num1;
int num2;
num1 = 15;
num2 = 25;
int result;
result = num1 + num2;
print(result);

if (num1 < num2) {
    int delta;
    delta = num2 - num1;
    print(delta);
}

int idx;
idx = 0;
while (idx < 3) {
    idx = idx + 1;
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
        setattr(self, attr, view)
        
    def run_compilation(self):
        """Execute the compilation pipeline"""
        src = self.code_input.get('1.0', tk.END)
        
        # Clear all output views
        for view in ['tok_view', 'var_view', 'ir_view', 'asm_view', 'err_view']:
            getattr(self, view).delete('1.0', tk.END)
        
        # Phase 1: Lexical Analysis
        tokens, lex_errs = self.scanner.scan(src)
        
        tok_display = "TOKEN STREAM\n" + "="*50 + "\n\n"
        tok_display += f"{'Type':<18} {'Value':<18} {'Line':<8}\n"
        tok_display += "-"*50 + "\n"
        for tok in tokens:
            tok_display += f"{tok['kind']:<18} {str(tok['val']):<18} {tok['ln']:<8}\n"
        
        self.tok_view.insert('1.0', tok_display)
        
        # Phase 2 & 3: Syntax Analysis & Semantic Analysis
        self.processor.process(src)

        # Symbol Table Display
        var_display = "SYMBOL TABLE\n" + "="*50 + "\n\n"
        var_display += f"{'Identifier':<18} {'Type':<12} {'Context':<15}\n"
        var_display += "-"*50 + "\n"
        for entry in self.processor.registry.all_entries():
            var_display += f"{entry['id']:<18} {entry['dtype']:<12} {entry['ctx']:<15}\n"
        
        self.var_view.insert('1.0', var_display)
        
        # Intermediate Representation Display
        ir_display = "INTERMEDIATE REPRESENTATION\n" + "="*50 + "\n\n"
        for idx, instr in enumerate(self.processor.ir_instructions):
            op = instr['op']
            s1 = instr['src1']
            s2 = instr['src2']
            d = instr['dst']
            
            if op == 'assign':
                ir_display += f"{idx+1}. {d} := {s1}\n"
            elif op in ['+', '-', '*', '/', '%']:
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
                ir_display += f"{idx+1}. {d} := {s1} {op} {s2}\n"
        
        self.ir_view.insert('1.0', ir_display)
        
        # Phase 4: Code Generation
        asm = self.translator.translate(self.processor.ir_instructions)
        asm_display = "ASSEMBLY OUTPUT\n" + "="*50 + "\n\n"
        asm_display += "\n".join(asm)
        
        self.asm_view.insert('1.0', asm_display)
        
        # Error/Issue Display
        all_errs = lex_errs + self.processor.issues
        if all_errs:
            err_display = "COMPILATION ISSUES\n" + "="*50 + "\n\n"
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