import ply.yacc as yacc
from lexer import TokenScanner
from symbol_table import VariableRegistry


class SyntaxProcessor:
    """Parser and semantic analyzer"""
    
    tokens = TokenScanner.tokens
    
    def __init__(self):
        self.registry = VariableRegistry()
        self.ir_instructions = []
        self.tmp_counter = 0
        self.lbl_counter = 0
        self.issues = []
        self.ast = []
        
    def gen_temp(self):
        """Generate a temporary variable name"""
        self.tmp_counter += 1
        return f"temp{self.tmp_counter}"
    
    def gen_label(self):
        """Generate a label for control flow"""
        self.lbl_counter += 1
        return f"Label{self.lbl_counter}"
    
    def add_instruction(self, operation, operand1=None, operand2=None, dest=None):
        """
        Add an instruction to the intermediate representation
        
        Args:
            operation: Operation type (assign, add, jump, etc.)
            operand1: First operand
            operand2: Second operand
            dest: Destination variable
            
        Returns:
            dest: The destination variable
        """
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
        
        # Check if variable already declared in current scope
        if self.registry.is_declared_in_current_scope(name):
            self.issues.append(f"Redeclaration of '{name}' in current scope")
        else:
            if len(p) == 4:
                self.registry.add(name, dtype, None, context='declaration')
                p[0] = ('decl', dtype, name)
            else:
                val = p[4]
                self.registry.add(name, dtype, val, context='declaration')
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
        '''code_block : block_start stmt_sequence block_end'''
        p[0] = ('block', p[2])
    
    def p_block_start(self, p):
        '''block_start : LBRACE'''
        # Push new scope when entering block
        scope_name = f"block_{self.registry.current_scope_id + 1}"
        self.registry.push_scope(scope_name)
        p[0] = 'block_start'
    
    def p_block_end(self, p):
        '''block_end : RBRACE'''
        # Pop scope when exiting block
        self.registry.pop_scope()
        p[0] = 'block_end'
    
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
        """Handle syntax errors"""
        if p:
            self.issues.append(f"Syntax error near '{p.value}' (line {p.lineno})")
        else:
            self.issues.append("Unexpected end of input")
    
    def initialize(self):
        """Initialize the parser"""
        self.processor = yacc.yacc(module=self)
    
    def process(self, code):
        """
        Parse source code and generate IR
        
        Args:
            code: Source code string
            
        Returns:
            Abstract syntax tree
        """
        self.ir_instructions = []
        self.tmp_counter = 0
        self.lbl_counter = 0
        self.issues = []
        self.ast = []
        
        # Ensure symbol table is at global scope
        self.registry.clear()
        
        return self.processor.parse(code)
