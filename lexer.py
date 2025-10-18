import ply.lex as lex


class TokenScanner:
    """Lexical analyzer for scanning and tokenizing source code"""
    
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

    # Token rules
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
        """Initialize the lexer"""
        self.scanner = lex.lex(module=self)

    def scan(self, code):
        """
        Scan source code and generate token stream
        
        Args:
            code: Source code string to tokenize
            
        Returns:
            tuple: (token_stream, issues) - list of tokens and list of errors
        """
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