Mini Pattern Language Compiler

how to run:
```
streamlit run app.py
```

Overview:
- A tiny DSL to generate numeric sequences and perform simple arithmetic, control flow, and printing.
- Implements all six compiler phases: lexing, parsing (AST), semantic analysis, IR (three-address), optimization, and code generation via an interpreter.

Example Program:
```
let n = 7
seq s = fibonacci(n)
print s
seq t = range(1, 5)
print t
let x = 2 * 3 + 4
print x
loop i from 0 to 3 {
  print i
}
```

Keywords:
- `let`, `seq`, `print`, `loop`, `from`, `to`, `if`, `else`, `true`, `false`, `fibonacci`, `range`

Types:
- `int` (implicit for numeric literals and `let` values)
- `seq` (sequence of ints)

Grammar (EBNF):
```
program      := { statement }
statement    := let_stmt | seq_stmt | print_stmt | loop_stmt | if_stmt
let_stmt     := "let" IDENT "=" expr NEWLINE
seq_stmt     := "seq" IDENT "=" seq_expr NEWLINE
print_stmt   := "print" expr NEWLINE
loop_stmt    := "loop" IDENT "from" expr "to" expr compound
if_stmt      := "if" expr compound [ "else" compound ]
compound     := "{" { statement } "}"

seq_expr     := "fibonacci" "(" expr ")"
              | "range"     "(" expr "," expr ")"

expr         := logic
logic        := equality { ("&&" | "||") equality }
 eqaulity    := rel { ("==" | "!=") rel }
rel          := add { ("<" | "<=" | ">" | ">=") add }
add          := mul { ("+" | "-") mul }
mul          := unary { ("*" | "/" | "%") unary }
unary        := ["-"] primary
primary      := NUMBER | IDENT | "(" expr ")"
```

Semantic Rules:
- Identifiers must be declared before use.
- `let` defines `int` variables; `seq` defines `seq` variables.
- `print` accepts `int` or `seq` and prints appropriately.
- Type checks on operators (arithmetic only on `int`).

Compiler Phases Artifacts:
- Lexical DFA: to be added as handwritten diagram (scan/photo).
- Parse trees: provide two derivations for sample programs (handwritten).
- Symbol table sample: provide scope table including loop-block scope (handwritten).

Run:
```
python -m mini_pattern_lang.run examples/sample1.mpl
```
Demo Video: (https://drive.google.com/file/d/1GcE-aMOHyM_9jJ81TJHYhd-pfbGjhaPt/view?usp=drive_link)