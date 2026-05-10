import streamlit as st
import sys
from pathlib import Path
from src.lexer import Lexer
from src.parser import Parser
from src.semantic import Semantic, SemanticError
from src.ir import IRGen
from src.optimizer import Optimizer
from src.codegen import VM
from graphviz import Digraph  # Import graphviz for visualization

from io import StringIO
import contextlib

@contextlib.contextmanager
def stdout_capture():
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    try:
        yield mystdout
    finally:
        sys.stdout = old_stdout

def visualize_ast(node, graph=None, parent=None):
    """Recursively visualize the Abstract Syntax Tree (AST)."""
    if graph is None:
        graph = Digraph(format="png")
        graph.attr(rankdir="TB")  # Top-to-bottom layout

    node_id = str(id(node))
    label = type(node).__name__

    # Add node-specific labels
    if hasattr(node, "name"):
        label += f"\\nName: {node.name}"
    if hasattr(node, "value"):
        label += f"\\nValue: {node.value}"
    if hasattr(node, "op"):
        label += f"\\nOp: {node.op}"

    graph.node(node_id, label)

    if parent:
        graph.edge(parent, node_id)

    # Recursively add children
    if hasattr(node, "__dict__"):
        for key, value in node.__dict__.items():
            if isinstance(value, list):
                for child in value:
                    if hasattr(child, "__dict__"):
                        visualize_ast(child, graph, node_id)
            elif hasattr(value, "__dict__"):
                visualize_ast(value, graph, node_id)

    return graph

def visualize_symbol_table(scopes):
    """Visualize the Symbol Table as a tree."""
    graph = Digraph(format="png")
    graph.attr(rankdir="TB")  # Top-to-bottom layout

    for i, scope in enumerate(scopes):
        scope_id = f"Scope_{i}"
        graph.node(scope_id, f"Scope {i}")

        for name, symbol in scope.items():
            symbol_id = f"{scope_id}_{name}"
            graph.node(symbol_id, f"{name}: {symbol.typ}")
            graph.edge(scope_id, symbol_id)

    return graph

def run_compiler(code):
    results = {}
    try:
        # Lexing Phase
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        results['tokens'] = "\n".join([f"{t.type}({t.value}) at {t.line}:{t.column}" for t in tokens])

        # Parsing Phase
        parser = Parser(code)
        prog = parser.parse()
        results['ast'] = prog

        # Semantic Analysis Phase
        sem = Semantic()
        sem.check_program(prog)
        results['semantic'] = sem.scopes

        # IR Generation Phase
        ir_gen = IRGen()
        ir = ir_gen.gen_program(prog)
        results['ir'] = "\n".join([str(i) for i in ir])

        # Optimization Phase
        opt = Optimizer()
        ir_opt = opt.fold_constants(ir)
        ir_opt = opt.dce(ir_opt)
        results['opt_ir'] = "\n".join([str(i) for i in ir_opt])

        # Code Execution Phase
        vm = VM(ir_opt)
        with stdout_capture() as out:
            vm.run()
        results['output'] = out.getvalue()
        results['memory'] = str(vm.vars)

    except Exception as e:
        results['error'] = str(e)

    return results

# Streamlit app configuration
st.set_page_config(page_title="Mini Pattern Language Compiler", layout="wide")

# Sidebar for settings
with st.sidebar:
    st.title("⚙️ Compiler Settings")
    example_files = {
        "Sample Fibonacci": "examples/sample_fib.mpl",
        "Sample 1": "examples/sample1.mpl",
        "Sample 2": "examples/sample2.mpl",
        "Sample 3": "examples/sample3.mpl"
    }
    selected_example = st.selectbox("Load Example", list(example_files.keys()))
    uploaded_file = st.file_uploader("Upload MPL File", type=["mpl"])
    compile_button = st.button("🚀 Compile & Run")

# Main UI
st.title("🛠️ Mini Pattern Language Compiler")
st.markdown("### Interactive Compiler Dashboard")

# Source Code Input
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("📜 Source Code")
    if uploaded_file:
        code = uploaded_file.read().decode("utf-8")
    elif selected_example:
        code = Path(example_files[selected_example]).read_text()
    else:
        code = """let n = 7
seq s = fibonacci(n)
print s
loop i from 0 to 3 {
  print i
}"""
    code = st.text_area("Enter MPL Code:", value=code, height=300)

# Compilation and Results
if compile_button:
    with st.spinner("Compiling..."):
        results = run_compiler(code)
        if 'error' in results:
            st.error(f"❌ Compilation Error: {results['error']}")
        else:
            st.session_state['results'] = results
            st.success("✅ Compilation Successful!")

# Display Results
if 'results' in st.session_state:
    res = st.session_state['results']

    with col2:
        st.subheader("📊 Compilation Results")
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "🔍 Lexing", "🌲 Parsing (AST)", "🧠 Semantic Analysis",
            "📄 IR Generation", "⚡ Optimization", "💻 Code Execution", "🗂️ Final Memory", "🌳 Visualizations"
        ])

        with tab1:
            st.subheader("🔍 Lexing Phase")
            st.code(res.get('tokens', ''), language="text")

        with tab2:
            st.subheader("🌲 Parsing Phase (Abstract Syntax Tree)")
            st.code(str(res.get('ast', '')), language="text")

        with tab3:
            st.subheader("🧠 Semantic Analysis Phase")
            st.code(str(res.get('semantic', '')), language="text")

        with tab4:
            st.subheader("📄 IR Generation Phase")
            st.code(res.get('ir', ''), language="text")

        with tab5:
            st.subheader("⚡ Optimization Phase")
            st.code(res.get('opt_ir', ''), language="text")

        with tab6:
            st.subheader("💻 Code Execution Phase")
            st.code(res.get('output', ''), language="text")

        with tab7:
            st.subheader("🗂️ Final Memory State")
            st.code(res.get('memory', ''), language="text")

        with tab8:
            st.subheader("🌳 Visualizations")
            st.markdown("#### Abstract Syntax Tree (AST)")
            ast_graph = visualize_ast(res['ast'])
            st.graphviz_chart(ast_graph)

            st.markdown("#### Symbol Table (Scopes)")
            symbol_graph = visualize_symbol_table(res['semantic'])
            st.graphviz_chart(symbol_graph)