import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ply.lex as lex
import ply.yacc as yacc


class TokenScanner:
    keywords = {
        'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'for': 'FOR',
        'int': 'INT', 'float': 'FLOAT', 'return': 'RETURN', 'print': 'PRINT'
    }

    tokens = [
        'IDENTIFIER', 'INTEGER', 'DECIMAL',
        'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MOD',
        'EQUALS', 'EQUAL_TO', 'NOT_EQUAL', 'LESS', 'LESS_EQ', 'GREATER', 'GREATER_EQ',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA',
    ] + list(keywords.values())

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_EQUALS = r'='
    t_EQUAL_TO = r'=='
    t_NOT_EQUAL = r'!='
    t_LESS = r'<'
    t_LESS_EQ = r'<='
    t_GREATER = r'>'
    t_GREATER_EQ = r'>='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_SEMICOLON = r';'
    t_COMMA = r','
    t_ignore = ' \t'

    def t_DECIMAL(self, tok):
        r'\d+\.\d+'
        tok.value = float(tok.value)
        return tok

    def t_INTEGER(self, tok):
        r'\d+'
        tok.value = int(tok.value)
        return tok

    def t_IDENTIFIER(self, tok):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        tok.type = self.keywords.get(tok.value, 'IDENTIFIER')
        return tok

    def t_newline(self, tok):
        r'\n+'
        tok.lexer.lineno += len(tok.value)

    def t_error(self, tok):
        self.issues.append(f"Invalid character '{tok.value[0]}' at line {tok.lineno}")
        tok.lexer.skip(1)

    def __init__(self):
        self.scanner = None
        self.token_stream = []
        self.issues = []

    def initialize(self):
        self.scanner = lex.lex(module=self)

    def scan(self, code):
        self.token_stream = []
        self.issues = []
        self.scanner.input(code)
        
        while True:
            tok = self.scanner.token()
            if not tok:
                break
            self.token_stream.append({
                'kind': tok.type,
                'val': tok.value,
                'ln': tok.lineno,
                'pos': tok.lexpos
            })
        
        return self.token_stream, self.issues



# VARIABLE REGISTRY
class VariableRegistry:
    def __init__(self):
        self.entries = {}
        self.contexts = ['main']
        
    def add(self, identifier, var_type, initial_val=None, ctx=None):
        ctx = ctx or self.contexts[-1]
        key = f"{ctx}:{identifier}"
        self.entries[key] = {
            'id': identifier,
            'dtype': var_type,
            'val': initial_val,
            'ctx': ctx
        }
    
    def find(self, identifier):
        for ctx in reversed(self.contexts):
            key = f"{ctx}:{identifier}"
            if key in self.entries:
                return self.entries[key]
        return None
    
    def all_entries(self):
        return list(self.entries.values())


# SYNTAX & SEMANTIC PROCESSOR

class SyntaxProcessor:
    tokens = TokenScanner.tokens
    
    def __init__(self):
        self.registry = VariableRegistry()
        self.ir_instructions = []
        self.tmp_counter = 0
        self.lbl_counter = 0
        self.issues = []
        self.ast = []
        
    def gen_temp(self):
        self.tmp_counter += 1
        return f"temp{self.tmp_counter}"
    
    def gen_label(self):
        self.lbl_counter += 1
        return f"Label{self.lbl_counter}"
    
    def add_instruction(self, operation, operand1=None, operand2=None, dest=None):
        instr = {'op': operation, 'src1': operand1, 'src2': operand2, 'dst': dest}
        self.ir_instructions.append(instr)
        return dest
    
    # Grammar Productions
    def p_start(self, p):
        '''start : stmt_sequence'''
        p[0] = ('program', p[1])
        self.ast.append(p[0])
    
    def p_stmt_sequence(self, p):
        '''stmt_sequence : stmt_sequence stmt
                        | stmt'''
        p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]
    
    def p_stmt(self, p):
        '''stmt : var_decl
               | var_assign
               | output_stmt
               | conditional
               | loop
               | code_block'''
        p[0] = p[1]
    
    def p_var_decl(self, p):
        '''var_decl : data_type IDENTIFIER SEMICOLON
                   | data_type IDENTIFIER EQUALS expr SEMICOLON'''
        dtype = p[1]
        name = p[2]
        
        if self.registry.find(name):
            self.issues.append(f"Redeclaration of '{name}'")
        else:
            if len(p) == 4:
                self.registry.add(name, dtype)
                p[0] = ('decl', dtype, name)
            else:
                val = p[4]
                self.registry.add(name, dtype, val)
                self.add_instruction('assign', val, None, name)
                p[0] = ('decl_init', dtype, name, val)
    
    def p_data_type(self, p):
        '''data_type : INT
                    | FLOAT'''
        p[0] = p[1]
    
    def p_var_assign(self, p):
        '''var_assign : IDENTIFIER EQUALS expr SEMICOLON'''
        name = p[1]
        val = p[3]
        
        if not self.registry.find(name):
            self.issues.append(f"Undefined variable '{name}'")
        
        self.add_instruction('assign', val, None, name)
        p[0] = ('assign', name, val)
    
    def p_output_stmt(self, p):
        '''output_stmt : PRINT LPAREN expr RPAREN SEMICOLON'''
        self.add_instruction('output', p[3], None, None)
        p[0] = ('output', p[3])
    
    def p_conditional(self, p):
        '''conditional : IF LPAREN comparison RPAREN code_block
                      | IF LPAREN comparison RPAREN code_block ELSE code_block'''
        cmp = p[3]
        lbl_true = self.gen_label()
        lbl_false = self.gen_label()
        lbl_end = self.gen_label()
        
        self.add_instruction('jump_if_false', cmp, lbl_false, None)
        self.add_instruction('mark', lbl_true, None, None)
        
        if len(p) == 6:
            self.add_instruction('jump', lbl_end, None, None)
            self.add_instruction('mark', lbl_false, None, None)
        else:
            self.add_instruction('mark', lbl_false, None, None)
            self.add_instruction('jump', lbl_end, None, None)
        
        self.add_instruction('mark', lbl_end, None, None)
        p[0] = ('if', cmp, p[5])
    
    def p_loop(self, p):
        '''loop : WHILE LPAREN comparison RPAREN code_block'''
        lbl_start = self.gen_label()
        lbl_end = self.gen_label()
        
        self.add_instruction('mark', lbl_start, None, None)
        cmp = p[3]
        self.add_instruction('jump_if_false', cmp, lbl_end, None)
        self.add_instruction('jump', lbl_start, None, None)
        self.add_instruction('mark', lbl_end, None, None)
        
        p[0] = ('loop', cmp, p[5])
    
    def p_code_block(self, p):
        '''code_block : LBRACE stmt_sequence RBRACE'''
        p[0] = ('block', p[2])
    
    def p_comparison(self, p):
        '''comparison : expr rel_op expr'''
        tmp = self.gen_temp()
        self.add_instruction(p[2], p[1], p[3], tmp)
        p[0] = tmp
    
    def p_rel_op(self, p):
        '''rel_op : LESS
                 | LESS_EQ
                 | GREATER
                 | GREATER_EQ
                 | EQUAL_TO
                 | NOT_EQUAL'''
        p[0] = p[1]
    
    def p_expr_add(self, p):
        '''expr : expr PLUS term
               | expr MINUS term'''
        tmp = self.gen_temp()
        self.add_instruction(p[2], p[1], p[3], tmp)
        p[0] = tmp
    
    def p_expr_term(self, p):
        '''expr : term'''
        p[0] = p[1]
    
    def p_term_mul(self, p):
        '''term : term MULTIPLY base
               | term DIVIDE base
               | term MOD base'''
        tmp = self.gen_temp()
        self.add_instruction(p[2], p[1], p[3], tmp)
        p[0] = tmp
    
    def p_term_base(self, p):
        '''term : base'''
        p[0] = p[1]
    
    def p_base_num(self, p):
        '''base : INTEGER
               | DECIMAL'''
        p[0] = p[1]
    
    def p_base_id(self, p):
        '''base : IDENTIFIER'''
        if not self.registry.find(p[1]):
            self.issues.append(f"Undefined variable '{p[1]}'")
        p[0] = p[1]
    
    def p_base_paren(self, p):
        '''base : LPAREN expr RPAREN'''
        p[0] = p[2]
    
    def p_error(self, p):
        if p:
            self.issues.append(f"Syntax error near '{p.value}' (line {p.lineno})")
        else:
            self.issues.append("Unexpected end of input")
    
    def initialize(self):
        self.processor = yacc.yacc(module=self)
    
    def process(self, code):
        self.ir_instructions = []
        self.tmp_counter = 0
        self.lbl_counter = 0
        self.issues = []
        self.ast = []
        
        return self.processor.parse(code)


class AssemblyTranslator:
    def __init__(self):
        self.asm_output = []
        self.regs = ['AX', 'BX', 'CX', 'DX']
        self.reg_alloc = {}
        self.reg_idx = 0
        
    def allocate_reg(self, var):
        if var in self.reg_alloc:
            return self.reg_alloc[var]
        
        reg = self.regs[self.reg_idx % len(self.regs)]
        self.reg_idx += 1
        self.reg_alloc[var] = reg
        return reg
    
    def translate(self, ir_code):
        self.asm_output = []
        self.asm_output.append("; Generated Assembly Code")
        self.asm_output.append("section .data")
        self.asm_output.append("section .text")
        self.asm_output.append("global main")
        self.asm_output.append("main:")
        
        for instr in ir_code:
            op = instr['op']
            s1 = instr['src1']
            s2 = instr['src2']
            d = instr['dst']
            
            if op == 'assign':
                r_src = self.allocate_reg(s1) if isinstance(s1, str) and s1.startswith('temp') else None
                r_dst = self.allocate_reg(d)
                
                if r_src:
                    self.asm_output.append(f"    MOV {r_dst}, {r_src}")
                else:
                    self.asm_output.append(f"    MOV {r_dst}, {s1}")
                    
            elif op in ['+', '-', '*', '/', '%']:
                r1 = self.allocate_reg(s1) if isinstance(s1, str) else None
                r2 = self.allocate_reg(s2) if isinstance(s2, str) else None
                r_res = self.allocate_reg(d)
                
                ops = {'+': 'ADD', '-': 'SUB', '*': 'IMUL', '/': 'IDIV', '%': 'MOD'}
                
                v1 = r1 if r1 else s1
                v2 = r2 if r2 else s2
                
                self.asm_output.append(f"    {ops[op]} {r_res}, {v1}, {v2}")
                    
            elif op in ['<', '<=', '>', '>=', '==', '!=']:
                r1 = self.allocate_reg(s1) if isinstance(s1, str) else None
                r2 = self.allocate_reg(s2) if isinstance(s2, str) else None
                r_res = self.allocate_reg(d)
                
                v1 = r1 if r1 else s1
                v2 = r2 if r2 else s2
                
                self.asm_output.append(f"    CMP {v1}, {v2}")
                self.asm_output.append(f"    SETCC {r_res}")
                
            elif op == 'mark':
                self.asm_output.append(f"{s1}:")
                
            elif op == 'jump':
                self.asm_output.append(f"    JMP {s1}")
                
            elif op == 'jump_if_false':
                r = self.allocate_reg(s1) if isinstance(s1, str) else None
                v = r if r else s1
                self.asm_output.append(f"    CMP {v}, 0")
                self.asm_output.append(f"    JZ {s2}")
                
            elif op == 'output':
                r = self.allocate_reg(s1) if isinstance(s1, str) else None
                v = r if r else s1
                self.asm_output.append(f"    CALL print_{v}")
        
        self.asm_output.append("    MOV EAX, 0")
        self.asm_output.append("    RET")
        
        return self.asm_output

class CompilerInterface:
    def __init__(self, window):
        self.window = window
        self.window.title("Mini Compiler - By Soma Das")
        self.window.geometry("1400x850")
        self.window.configure(bg='#1e1e1e')
        
        # Initialize components
        self.scanner = TokenScanner()
        self.scanner.initialize()
        self.processor = SyntaxProcessor()
        self.processor.initialize()
        self.translator = AssemblyTranslator()
        
        self.build_interface()
        
    def build_interface(self):
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
        
        # Default sample
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
