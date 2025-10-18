class AssemblyTranslator:
    """Converts IR to assembly language"""
    
    def __init__(self):
        self.asm_output = []
        self.regs = ['AX', 'BX', 'CX', 'DX']
        self.reg_alloc = {}
        self.reg_idx = 0
        
    def allocate_reg(self, var):
        """
        Allocate a register for a variable
        
        Args:
            var: Variable name
            
        Returns:
            str: Register name
        """
        if var in self.reg_alloc:
            return self.reg_alloc[var]
        
        reg = self.regs[self.reg_idx % len(self.regs)]
        self.reg_idx += 1
        self.reg_alloc[var] = reg
        return reg
    
    def translate(self, ir_code):
        """
        Translate intermediate representation to assembly code
        
        Args:
            ir_code: List of IR instructions
            
        Returns:
            list: Assembly code lines
        """
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