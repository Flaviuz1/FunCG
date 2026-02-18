import streamlit as st
import math
import math_engine
from graphing_utilities import plot_function

st.set_page_config(page_title="FunCG", layout="wide")
st.title("FunCG")

tab1, tab2 = st.tabs(["Instructions", "Graph / Calculator"])

with tab1:
    st.markdown("""
### Calculator Usage Guide

**Basic arithmetic:** `+`, `-`, `*`, `/`, `^`  
**Constants:** `pi`, `e`, `inf` (represents 10⁸)  
**Variables:** any single letter (use `x` for graphing)

### Functions
- `sum(var, lower, upper, expr)`
- `product(var, lower, upper, expr)`
- `integral(var, lower, upper, expr)`
- `lim(var, to, expr)`
- `logarithm(base, x) / log(base, x)` — base is optional, defaults to *e*
- `absolute(x) / abs(x)`
- `factorial(n)`
- `floor(x)`, `ceiling(x) / ceil(x)`
- `sin(x)`, `cos(x)`, `tan(x)` / `tg(x)`, `ctg(x)`
- `arcsin(x)`, `arccos(x)`, `arctg(x)` / `arctan(x)`, `arcctg(x)`
- `arrangements(n, k) / arra(n, k)` — A(n,k) = n! / (n-k)!
- `combinations(n, k) / comb(n, k)` — C(n,k) = n! / (k! · (n-k)!)
- `permutations(n) / perm(n)` — P(n) = n!
- `gcd(a, b)`, `lcm(a, b)` — greatest common divisor / least common multiple
- `mod(a, b)` — remainder of a / b
- `root(n, x)` — nth root of x
- `mean(...)`, `variance(...)`, `stdev(...)` — pass any number of values e.g. `mean(2, 4, 6)`

### Modes

**Simple Mode**
- Enter an expression → result
- Example: `2+2`, `sin(pi/2)`, `integral(x, 0, 1, x^2)`

**Functions Mode**
- Enter a function of `x`, get a graph
- Example: `x^2`, `sin(x)`, `1/x`
- Fixed bounds: x ∈ [−10, 10], y ∈ [−8, 8]

### Writing Rules
- Trigonometric input is in radians - the transformation is num_of_degrees * PI / 180
- Use parentheses for grouping
- Use `^` for exponentiation
- Function names can be any case

---
*Math engine powered by C++ (PyBind11)*
""")

with tab2:
    st.subheader("Calculator / Function Grapher")

    mode = st.radio(
        "Mode",
        ["Simple (Calculate)", "Functions (Graph f(x))"],
        horizontal=True,
    )

    expr = st.text_input("Enter expression", placeholder="x^2  or  sin(x)  or  integral(x, 0, 1, x^2)")

    if st.button("Calculate / Plot"):
        if not expr.strip():
            st.error("Please enter an expression.")
            st.stop()

        try:
            #SIMPLE MODE
            if mode.startswith("Simple"):
                result = math_engine.evaluate(expr)

                if isinstance(result, float):
                    if result == int(result) and abs(result) < 1e15:
                        st.success(f"Result: {int(result)}")
                    else:
                        st.success(f"Result: {round(result, 6)}")
                else:
                    st.success(f"Result: {result}")

            #GRAPH MODE
            else:
                fig = plot_function(expr)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {e}")
