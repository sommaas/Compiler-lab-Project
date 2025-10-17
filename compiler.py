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
