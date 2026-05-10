from typing import List
from .ir import Instr

class Optimizer:
    def fold_constants(self, code: List[Instr]) -> List[Instr]:
        out: List[Instr] = []
        for ins in code:
            if ins.op in ('+','-','*','/','%') and ins.b is not None and ins.c is not None:
                if ins.b.isdigit() and ins.c.isdigit():
                    a = int(ins.b); b = int(ins.c)
                    if ins.op == '+': val = a + b
                    elif ins.op == '-': val = a - b
                    elif ins.op == '*': val = a * b
                    elif ins.op == '/': val = a // b
                    else: val = a % b
                    out.append(Instr('assign', ins.a, str(val)))
                    continue
            out.append(ins)
        return out

    def dce(self, code: List[Instr]) -> List[Instr]:
        used = set()
        for ins in code:
            for x in (ins.a, ins.b, ins.c):
                if x and x.startswith('t'):
                    used.add(x)
        out = []
        for ins in code:
            if ins.op == 'assign' and ins.a and ins.a.startswith('t') and ins.a not in used:
                continue
            out.append(ins)
        return out
