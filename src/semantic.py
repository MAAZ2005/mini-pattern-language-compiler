from dataclasses import dataclass
from typing import Dict, List, Optional
from . import ast as A

@dataclass
class Symbol:
    name: str
    typ: str

class SemanticError(Exception):
    pass

class Semantic:
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]

    def enter(self):
        self.scopes.append({})

    def exit(self):
        self.scopes.pop()

    def declare(self, name: str, typ: str):
        scope = self.scopes[-1]
        if name in scope:
            raise SemanticError(f'Redeclaration of {name}')
        scope[name] = Symbol(name, typ)

    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def check_program(self, p: A.Program):
        for s in p.body:
            self.check_stmt(s)

    def check_stmt(self, s: A.Stmt):
        if isinstance(s, A.Let):
            val_t = self.check_expr(s.value)
            if val_t != 'int':
                raise SemanticError('let expects int value')
            self.declare(s.name, 'int')
        elif isinstance(s, A.SeqDecl):
            val_t = self.check_expr(s.value)
            if val_t != 'seq':
                raise SemanticError('seq expects sequence value')
            self.declare(s.name, 'seq')
        elif isinstance(s, A.Print):
            t = self.check_expr(s.value)
            if t not in ('int','seq'):
                raise SemanticError('print expects int or seq')
        elif isinstance(s, A.Loop):
            start_t = self.check_expr(s.start)
            end_t = self.check_expr(s.end)
            if start_t != 'int' or end_t != 'int':
                raise SemanticError('loop bounds must be int')
            self.enter()
            self.declare(s.var, 'int')
            for ss in s.body:
                self.check_stmt(ss)
            self.exit()
        elif isinstance(s, A.If):
            cond_t = self.check_expr(s.cond)
            if cond_t != 'int':
                raise SemanticError('if condition must be int (0/1)')
            self.enter()
            for ss in s.then_body:
                self.check_stmt(ss)
            self.exit()
            if s.else_body is not None:
                self.enter()
                for ss in s.else_body:
                    self.check_stmt(ss)
                self.exit()
        else:
            raise SemanticError('Unknown statement')

    def check_expr(self, e: A.Expr) -> str:
        if isinstance(e, A.Number):
            return 'int'
        if isinstance(e, A.Var):
            sym = self.lookup(e.name)
            if not sym:
                raise SemanticError(f'Undeclared identifier {e.name}')
            return sym.typ
        if isinstance(e, A.Unary):
            t = self.check_expr(e.expr)
            if e.op == '-' and t == 'int':
                return 'int'
            raise SemanticError('invalid unary op')
        if isinstance(e, A.Binary):
            lt = self.check_expr(e.left)
            rt = self.check_expr(e.right)
            if e.op in ('+','-','*','/','%'):
                if lt == rt == 'int':
                    return 'int'
                raise SemanticError('arithmetic expects int operands')
            if e.op in ('<','<=','>','>=','==','!='):
                if lt == rt == 'int':
                    return 'int'  # boolean as int
                raise SemanticError('comparison expects int operands')
            if e.op in ('&&','||'):
                if lt == rt == 'int':
                    return 'int'
                raise SemanticError('logic expects int operands')
            raise SemanticError('unknown binary op')
        if isinstance(e, A.SeqFibonacci):
            t = self.check_expr(e.n)
            if t != 'int':
                raise SemanticError('fibonacci expects int n')
            return 'seq'
        if isinstance(e, A.SeqRange):
            st = self.check_expr(e.start)
            en = self.check_expr(e.end)
            if st != 'int' or en != 'int':
                raise SemanticError('range expects int bounds')
            return 'seq'
        raise SemanticError('Unknown expression')
