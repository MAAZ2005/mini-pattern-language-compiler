from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Expr:
    pass

@dataclass
class Number(Expr):
    value: int

@dataclass
class Var(Expr):
    name: str

@dataclass
class Unary(Expr):
    op: str
    expr: Expr

@dataclass
class Binary(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class SeqFibonacci(Expr):
    n: Expr

@dataclass
class SeqRange(Expr):
    start: Expr
    end: Expr

@dataclass
class Stmt:
    pass

@dataclass
class Let(Stmt):
    name: str
    value: Expr

@dataclass
class SeqDecl(Stmt):
    name: str
    value: Expr

@dataclass
class Print(Stmt):
    value: Expr

@dataclass
class Loop(Stmt):
    var: str
    start: Expr
    end: Expr
    body: List[Stmt]

@dataclass
class If(Stmt):
    cond: Expr
    then_body: List[Stmt]
    else_body: Optional[List[Stmt]]

@dataclass
class Program:
    body: List[Stmt]
