from typing import List, Dict, Any
from .ir import Instr

class VM:
    def __init__(self, code: List[Instr]):
        self.code = code
        self.vars: Dict[str, Any] = {}
        self.labels: Dict[str, int] = {}
        for idx, ins in enumerate(code):
            if ins.op == 'label' and ins.a:
                self.labels[ins.a] = idx

    def get(self, x: str):
        if x is None:
            return None
        if x.isdigit():
            return int(x)
        return self.vars.get(x, 0)

    def run(self):
        pc = 0
        while pc < len(self.code):
            ins = self.code[pc]
            op = ins.op
            if op == 'assign':
                self.vars[ins.a] = self.get(ins.b)
            elif op == 'print':
                val = self.get(ins.a)
                if isinstance(val, list):
                    print('[' + ', '.join(map(str, val)) + ']')
                else:
                    print(val)
            elif op in ('+','-','*','/','%','<','<=','>','>=','==','!=','&&','||','add','le'):
                a = self.get(ins.b)
                b = self.get(ins.c)
                if op == '+': r = a + b
                elif op == '-': r = a - b
                elif op == '*': r = a * b
                elif op == '/': r = a // b
                elif op == '%': r = a % b
                elif op == '<': r = 1 if a < b else 0
                elif op == '<=': r = 1 if a <= b else 0
                elif op == '>': r = 1 if a > b else 0
                elif op == '>=': r = 1 if a >= b else 0
                elif op == '==': r = 1 if a == b else 0
                elif op == '!=': r = 1 if a != b else 0
                elif op == '&&': r = 1 if (a and b) else 0
                elif op == '||': r = 1 if (a or b) else 0
                elif op == 'add': r = a + b
                elif op == 'le': r = 1 if a <= b else 0
                else: r = 0
                self.vars[ins.a] = r
            elif op == 'neg':
                self.vars[ins.a] = - self.get(ins.b)
            elif op == 'fib':
                n = self.get(ins.b)
                seq = []
                a, b = 0, 1
                for _ in range(n):
                    seq.append(a)
                    a, b = b, a + b
                self.vars[ins.a] = seq
            elif op == 'range':
                s = self.get(ins.b)
                e = self.get(ins.c)
                self.vars[ins.a] = list(range(s, e+1))
            elif op == 'jz':
                cond = self.get(ins.a)
                if cond == 0:
                    pc = self.labels.get(ins.b, pc)
                    continue
            elif op == 'jmp':
                pc = self.labels.get(ins.a, pc)
                continue
            pc += 1
