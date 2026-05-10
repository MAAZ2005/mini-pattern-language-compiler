import sys
from pathlib import Path
from src.parser import Parser
from src.semantic import Semantic, SemanticError
from src.ir import IRGen
from src.optimizer import Optimizer
from src.codegen import VM

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <source.mpl>")
        sys.exit(1)
    src_path = Path("examples/" + sys.argv[1])
    code = src_path.read_text()
    parser = Parser(code)
    prog = parser.parse()

    sem = Semantic()
    try:
        sem.check_program(prog)
    except SemanticError as e:
        print("Semantic error:", e)
        sys.exit(2)

    ir = IRGen().gen_program(prog)
    opt = Optimizer()
    ir = opt.fold_constants(ir)
    ir = opt.dce(ir)

    vm = VM(ir)
    vm.run()

if __name__ == '__main__':
    main()
