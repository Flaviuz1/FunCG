import streamlit as st
from functions import tokenize, Parser, evaluate
from graphing_utilities import plot_function

st.set_page_config(page_title="GraphMaker Calculator", layout="wide")

st.title("FunCG")

# ---------------------------
# Tabs (replaces Tkinter notebook)
# ---------------------------
tab1, tab2 = st.tabs(["Instructions", "Graph / Calculator"])

# ---------------------------
# Instructions tab
# ---------------------------
with tab1:
    st.markdown("""
### Calculator Usage Guide

**Basic arithmetic:** `+`, `-`, `*`, `/`, `^`  
**Constants:** `pi`, `e`, `inf` (represents 10^8)  
**Variables:** any single letter (use `x` for graphing)

### Functions
- `sum(var, lower, upper, expr)`
- `product(var, lower, upper, expr)`
- `integral(var, lower, upper, expr)`
- `lim(var, to, expr)`
- `logarithm(base, x) - base is optional, if left empty it will be replaced with e`
- `absolute(x)`
- `factorial(n)`
- `floor(x)`, `ceiling(x)`
- `sin(x)`, `cos(x)`, `tg(x)`, `ctg(x)`
- `arcsin(x)`, `arccos(x)`, `arctg(x)`, `arcctg(x)`

### Modes

**Simple Mode**
- Enter an expression → result
- Example: `2+2`, `sin(pi/2)`

**Functions Mode**
- Enter a function of `x`
- Example: `x^2`, `sin(x)`
- Fixed bounds: (in the future custom bounds will be implemented)
  - x ∈ [-10, 10]
  - y ∈ [-8, 8]

### Writing Rules
- Use parentheses for grouping
- Use `^` for exponentiation
- Function names must be lowercase
- Trigonometric input is in radians
                
### WARNINGS
- Although the calculationa are fairly accurate (every result has a minimum of 1-2 correct decimals), errors 'might' still happen
""")

# ---------------------------
# Calculator tab
# ---------------------------
with tab2:

    st.subheader("Calculator / Function Grapher")

    mode = st.radio(
        "Mode",
        ["Simple (Calculate)", "Functions (Graph f(x))"],
        horizontal=True
    )

    if mode.startswith("Functions"):
        col1, col2 = st.columns([4, 1])  # 4:1 width ratio
        with col2:
            num_points = st.number_input(
            "Number of points for graph",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=1000
            )
    
        with col1:
            expr = st.text_input("Enter expression", placeholder="x^2 or sin(x)")
    else:
        expr = st.text_input("Enter expression", placeholder="x^2 or sin(x)")

    if st.button("Calculate / Plot"):

        if not expr.strip():
            st.error("Please enter an expression.")
            st.stop()

        try:
            tokens = tokenize(expr)
            ast = Parser(tokens).parse()

            # ---------------- SIMPLE MODE
            if mode.startswith("Simple"):
                result = evaluate(ast)

                if isinstance(result, float):
                    if result.is_integer():
                        result = int(result)
                    else:
                        result = round(result, 6)

                st.success(f"Result: {result}")

            # ---------------- GRAPH MODE
            else:
                fig = plot_function(ast)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {e}")

