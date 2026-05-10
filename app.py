import streamlit as st
import sys
import os
from src.parser import Parser
from src.semantic import Semantic
from src.ir import IRGen
from src.optimizer import Optimizer
from src.codegen import VM

from io import StringIO
import contextlib

@contextlib.contextmanager
def stdout_capture():
    import sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    try:
        yield mystdout
    finally:
        sys.stdout = old_stdout

def run_compiler(code):
    results = {}
    try:
        parser = Parser(code)
        prog = parser.parse()
        results['ast'] = str(prog)

        sem = Semantic()
        sem.check_program(prog)
        results['semantic'] = "Semantic Check Passed\nSymbol Table: " + str(sem.scopes)

        ir_gen = IRGen()
        ir = ir_gen.gen_program(prog)
        results['ir'] = "\n".join([str(i) for i in ir])

        opt = Optimizer()
        ir_opt = opt.fold_constants(ir)
        ir_opt = opt.dce(ir_opt)
        results['opt_ir'] = "\n".join([str(i) for i in ir_opt])

        vm = VM(ir_opt)
        with stdout_capture() as out:
            vm.run()
        results['output'] = out.getvalue()
        results['memory'] = str(vm.vars)
        
    except Exception as e:
        results['error'] = str(e)
    
    return results

st.set_page_config(page_title="Mini Pattern Language Compiler", layout="wide")

st.title("Mini Pattern Language Compiler")
st.markdown("### Interactive Compiler Dashboard")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Source Code")
    default_code = """let n = 7
seq s = fibonacci(n)
print s
loop i from 0 to 3 {
  print i
}"""
    code = st.text_area("Enter MPL Code:", value=default_code, height=300)
    
    if st.button("Compile & Run", type="primary"):
        if code:
            results = run_compiler(code)
            
            if 'error' in results:
                st.error(f"Compilation Error: {results['error']}")
            else:
                st.session_state['results'] = results
                st.success("Compilation Successful!")

with col2:
    if 'results' in st.session_state:
        res = st.session_state['results']
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Output", "AST", "Symbol Table", "IR Code", "Memory"])
        
        with tab1:
            st.subheader("Console Output")
            st.code(res.get('output', ''), language="text")
            
        with tab2:
            st.subheader("Abstract Syntax Tree")
            st.text(res.get('ast', ''))
            
        with tab3:
            st.subheader("Semantic Analysis")
            st.text(res.get('semantic', ''))
            
        with tab4:
            st.subheader("Intermediate Representation")
            col_ir1, col_ir2 = st.columns(2)
            with col_ir1:
                st.markdown("**Raw IR**")
                st.text(res.get('ir', ''))
            with col_ir2:
                st.markdown("**Optimized IR**")
                st.text(res.get('opt_ir', ''))
                
        with tab5:
            st.subheader("Final Memory State")
            st.text(res.get('memory', ''))
