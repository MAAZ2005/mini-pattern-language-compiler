from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

KEYWORDS = {
    'let', 'seq', 'print', 'loop', 'from', 'to', 'if', 'else', 'true', 'false',
    'fibonacci', 'range'
}

SYMBOLS = {
    '{', '}', '(', ')', ',',
}

OPERATORS = {
    '==', '!=', '<=', '>=', '&&', '||',
    '+', '-', '*', '/', '%', '<', '>', '='
}

class Lexer:
    def __init__(self, code: str):
        self.code = code

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        i = 0
        line = 1
        col = 1
        src = self.code

        def emit(t, v):
            tokens.append(Token(t, v, line, col))

        while i < len(src):
            ch = src[i]
            if ch in ' \t':
                i += 1; col += 1
                continue
            if ch == '\n':
                emit('NEWLINE', '\n')
                i += 1; line += 1; col = 1
                continue
            if ch == '#':
                while i < len(src) and src[i] != '\n':
                    i += 1; col += 1
                continue
            if ch.isdigit():
                start = i
                while i < len(src) and src[i].isdigit():
                    i += 1
                emit('NUMBER', src[start:i])
                col += (i - start)
                continue
            if ch.isalpha() or ch == '_':
                start = i
                while i < len(src) and (src[i].isalnum() or src[i] == '_'):
                    i += 1
                word = src[start:i]
                typ = word if word in KEYWORDS else 'IDENT'
                emit(typ, word)
                col += (i - start)
                continue
            two = src[i:i+2]
            if two in OPERATORS:
                emit(two, two)
                i += 2; col += 2
                continue
            if ch in OPERATORS:
                emit(ch, ch)
                i += 1; col += 1
                continue
            if ch in SYMBOLS:
                emit(ch, ch)
                i += 1; col += 1
                continue
            raise SyntaxError(f'Unknown character {ch} at {line}:{col}')
        tokens.append(Token('EOF', '', line, col))
        return tokens
