from dataclasses import dataclass
from typing import List, Optional
from . import ast as A

@dataclass
class Instr:
    op: str
    a: Optional[str] = None
    b: Optional[str] = None
    c: Optional[str] = None

class IRGen:
    def __init__(self):
        self.code: List[Instr] = []
        self.temp_id = 0

    def new_temp(self) -> str:
        self.temp_id += 1
        return f"t{self.temp_id}"

    def gen_program(self, p: A.Program) -> List[Instr]:
        for s in p.body:
            self.gen_stmt(s)
        return self.code

    def gen_stmt(self, s: A.Stmt):
        if isinstance(s, A.Let):
            t = self.gen_expr(s.value)
            self.code.append(Instr('assign', s.name, t))
        elif isinstance(s, A.SeqDecl):
            t = self.gen_expr(s.value)
            self.code.append(Instr('assign', s.name, t))
        elif isinstance(s, A.Print):
            t = self.gen_expr(s.value)
            self.code.append(Instr('print', t))
        elif isinstance(s, A.Loop):
            start = self.gen_expr(s.start)
            end = self.gen_expr(s.end)
            i = s.var
            self.code.append(Instr('assign', i, start))
            lbl_start = f"L{len(self.code)}"
            self.code.append(Instr('label', lbl_start))
            cond = self.new_temp()
            self.code.append(Instr('le', cond, i, end))
            lbl_end = f"L{len(self.code)+1}"
            self.code.append(Instr('jz', cond, lbl_end))
            for ss in s.body:
                self.gen_stmt(ss)
            self.code.append(Instr('add', i, i, '1'))
            self.code.append(Instr('jmp', lbl_start))
            self.code.append(Instr('label', lbl_end))
        elif isinstance(s, A.If):
            cond = self.gen_expr(s.cond)
            lbl_else = f"L{len(self.code)+1}"
            lbl_end = f"L{len(self.code)+2}"
            self.code.append(Instr('jz', cond, lbl_else))
            for ss in s.then_body:
                self.gen_stmt(ss)
            self.code.append(Instr('jmp', lbl_end))
            self.code.append(Instr('label', lbl_else))
            if s.else_body:
                for ss in s.else_body:
                    self.gen_stmt(ss)
            self.code.append(Instr('label', lbl_end))
        else:
            raise RuntimeError('Unknown stmt for IR')

    def gen_expr(self, e: A.Expr) -> str:
        if isinstance(e, A.Number):
            return str(e.value)
        if isinstance(e, A.Var):
            return e.name
        if isinstance(e, A.Unary) and e.op == '-':
            t = self.gen_expr(e.expr)
            r = self.new_temp()
            self.code.append(Instr('neg', r, t))
            return r
        if isinstance(e, A.Binary):
            a = self.gen_expr(e.left)
            b = self.gen_expr(e.right)
            r = self.new_temp()
            self.code.append(Instr(e.op, r, a, b))
            return r
        if isinstance(e, A.SeqFibonacci):
            n = self.gen_expr(e.n)
            r = self.new_temp()
            self.code.append(Instr('fib', r, n))
            return r
        if isinstance(e, A.SeqRange):
            s = self.gen_expr(e.start)
            en = self.gen_expr(e.end)
            r = self.new_temp()
            self.code.append(Instr('range', r, s, en))
            return r
        raise RuntimeError('Unknown expr for IR')
