import tkinter as tk
from tkinter import ttk
from functions import tokenize, Parser, evaluate, VariableNode
import math

root = tk.Tk()
root.title("GraphMaker Calculator")
root.geometry("1100x700")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# --- Instructions Tab ---
instructions_frame = tk.Frame(notebook)
notebook.add(instructions_frame, text="Instructions")

description = (
        "Calculator Usage Guide:\n"
        "\n"
        "Basic arithmetic: +, -, *, /, ^\n"
        "Constants: pi, e, inf (represents a large number 10^6)\n"
        "Variables: any single letter (use 'x' for graphing functions)\n"
        "\n"
        "Functions and their syntax:\n"
        "- sum(var, lower, upper, expr): Σ, e.g. sum(i, 1, 5, i^2)\n"
        "- product(var, lower, upper, expr): Π, e.g. product(i, 1, 5, i)\n"
        "- integral(var, lower, upper, expr): definite integral, e.g. integral(x, 0, 1, x^2)\n"
        "- limit(var, to, expr): limit as var approaches 'to', e.g. limit(x, 0, sin(x)/x)\n"
        "- logarithm(base, x): log, e.g. logarithm(e, 2) for ln(2)\n"
        "- module(x): absolute value, e.g. module(-5)\n"
        "- factorial(n): n!\n"
        "- floor(x), ceiling(x): integer rounding\n"
        "- sin(x), cos(x), tan(x), ctg(x): trigonometric functions (x in radians)\n"
        "- arcsin(x), arccos(x), arctg(x), arcctg(x): inverse trig functions\n"
        "\n"
        "Modes:\n"
        "- Simple Mode: Enter an expression and get the result\n"
        "  Example: 2+2, sin(pi/2), sum(i, 1, 10, i)\n"
        "\n"
        "- Functions Mode: Enter a function of x and see it graphed\n"
        "  Example: x^2, sin(x), x^3 - 2*x, 1/x\n"
        "  The graph has fixed bounds: x from -10 to 10, y from -8 to 8\n"
        "\n"
        "Writing rules:\n"
        "- Use parentheses for grouping and function arguments.\n"
        "- Use ^ for exponentiation.\n"
        "- All function names must be written in lowercase.\n"
        "- For integrals, sums, products, and limits, the first argument is the variable.\n"
        "- For trigonometric functions, input is in radians.\n"
        "- In Functions mode, use 'x' as your variable.\n"
        "\n"
        "Examples:\n"
        "Simple mode:\n"
        "- sum(i, 1, 10, i^2)\n"
        "- integral(x, 0, pi, sin(x))\n"
        "- limit(x, 0, sin(x)/x)\n"
        "- logarithm(10, 100)\n"
        "- factorial(5)\n"
        "- sin(pi/2)\n"
        "- arcsin(0.5)\n"
        "\n"
        "Functions mode:\n"
        "- x^2\n"
        "- sin(x)\n"
        "- x^3 - 2*x + 1\n"
        "- module(x)\n"
        "- 1/x\n"
        "- cos(x) + sin(x)\n"
    )

# Make the instructions scrollable
scrollbar = tk.Scrollbar(instructions_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

canvas_instructions = tk.Canvas(instructions_frame, yscrollcommand=scrollbar.set, bg="white")
canvas_instructions.pack(side="left", fill="both", expand=True)
scrollbar.config(command=canvas_instructions.yview)

instructions_inner_frame = tk.Frame(canvas_instructions, bg="white")
canvas_window = canvas_instructions.create_window((0, 0), window=instructions_inner_frame, anchor="nw")

instructions_label = tk.Label(instructions_inner_frame, text=description, font=("Arial", 11), justify="left", anchor="nw", bg="white")
instructions_label.pack(pady=10, padx=10)

# Update scroll region when frame changes size
def on_frame_configure(event=None):
    canvas_instructions.configure(scrollregion=canvas_instructions.bbox("all"))

def on_canvas_configure(event):
    # Make the frame fill the canvas width
    canvas_instructions.itemconfig(canvas_window, width=event.width)

instructions_inner_frame.bind("<Configure>", on_frame_configure)
canvas_instructions.bind("<Configure>", on_canvas_configure)

# Enable mousewheel scrolling
def on_mousewheel(event):
    canvas_instructions.yview_scroll(int(-1*(event.delta/120)), "units")

canvas_instructions.bind_all("<MouseWheel>", on_mousewheel)

# --- Grid/Graph Tab ---
graph_frame = tk.Frame(notebook)
notebook.add(graph_frame, text="Graph/Grid")

# Mode selection
mode_var = tk.StringVar(value="simple")
mode_frame = tk.Frame(graph_frame)
mode_frame.pack(pady=5)
tk.Label(mode_frame, text="Mode:", font=("Arial", 12)).pack(side="left", padx=5)
tk.Radiobutton(mode_frame, text="Simple (Calculate)", variable=mode_var, value="simple").pack(side="left", padx=5)
tk.Radiobutton(mode_frame, text="Functions (Graph f(x))", variable=mode_var, value="functions").pack(side="left", padx=5)

# Entry and output for calculations
entry_label = tk.Label(graph_frame, text="Enter expression:", font=("Arial", 10))
entry_label.pack(pady=(5, 0))

entry = tk.Entry(graph_frame, font=("Arial", 12), width=60)
entry.pack(pady=5)

output = tk.Label(graph_frame, text="", font=("Arial", 12), anchor="center", justify="center", fg="blue")
output.pack(pady=5, fill="x")

# Canvas for grid/graph
canvas = tk.Canvas(graph_frame, bg="white", width=800, height=500, highlightthickness=1, highlightbackground="gray")
canvas.pack(pady=10)

# Store current function for graphing
current_ast = None

def draw_grid(x_min=-10, x_max=10, y_min=-8, y_max=8):
    """Draw coordinate grid with fixed bounds"""
    canvas.delete("all")
    w, h = 800, 500
    
    # Simple scaling - map ranges directly to canvas
    x_scale = w / (x_max - x_min)
    y_scale = h / (y_max - y_min)
    
    # Draw grid lines and labels
    # Vertical grid lines (along x-axis)
    x_step = 1
    for x_val in range(int(x_min), int(x_max) + 1, x_step):
        screen_x = (x_val - x_min) * x_scale
        if 0 <= screen_x <= w:
            # Draw grid line
            if x_val == 0:
                canvas.create_line(screen_x, 0, screen_x, h, fill="black", width=2)
            else:
                canvas.create_line(screen_x, 0, screen_x, h, fill="#e0e0e0", width=1)
            
            # Label
            if x_val != 0:
                screen_y_axis = (0 - y_min) * y_scale
                if 0 <= screen_y_axis <= h:
                    canvas.create_text(screen_x, h - screen_y_axis + 15, text=str(x_val), font=("Arial", 8))
    
    # Horizontal grid lines (along y-axis)
    y_step = 1
    for y_val in range(int(y_min), int(y_max) + 1, y_step):
        screen_y = h - (y_val - y_min) * y_scale
        if 0 <= screen_y <= h:
            # Draw grid line
            if y_val == 0:
                canvas.create_line(0, screen_y, w, screen_y, fill="black", width=2)
            else:
                canvas.create_line(0, screen_y, w, screen_y, fill="#e0e0e0", width=1)
            
            # Label
            if y_val != 0:
                screen_x_axis = (0 - x_min) * x_scale
                if 0 <= screen_x_axis <= w:
                    canvas.create_text(screen_x_axis - 20, screen_y, text=str(y_val), font=("Arial", 8))
    
    # Draw axes labels
    screen_x_axis = (0 - x_min) * x_scale
    screen_y_axis = h - (0 - y_min) * y_scale
    
    if 0 <= screen_x_axis <= w:
        canvas.create_text(screen_x_axis + 15, 15, text="Y", font=("Arial", 10, "bold"))
    
    if 0 <= screen_y_axis <= h:
        canvas.create_text(w - 15, screen_y_axis - 15, text="X", font=("Arial", 10, "bold"))

def plot_function(ast, x_min=-10, x_max=10, y_min=-8, y_max=8):
    """Plot a function on the canvas with fixed bounds"""
    w, h = 800, 500
    
    # Redraw grid with fixed bounds
    draw_grid(x_min, x_max, y_min, y_max)
    
    # Simple scaling
    x_scale = w / (x_max - x_min)
    y_scale = h / (y_max - y_min)
    
    # Sample points
    num_points = 1000
    points = []
    
    # Evaluate function at each point
    for i in range(num_points):
        x = x_min + (x_max - x_min) * i / num_points
        try:
            y = evaluate(ast, {'x': x})
            # Only plot if y is in our fixed range
            if math.isfinite(y) and y_min <= y <= y_max:
                screen_x = (x - x_min) * x_scale
                screen_y = h - (y - y_min) * y_scale
                points.append((screen_x, screen_y, i))
        except:
            # Skip points where function is undefined
            pass
    
    if not points:
        output.config(text="Error: Function has no valid values in visible range", fg="red")
        return
    
    # Draw the function
    if len(points) > 1:
        for i in range(len(points) - 1):
            x1, y1, idx1 = points[i]
            x2, y2, idx2 = points[i + 1]
            
            # Only connect consecutive points (avoid connecting over undefined regions)
            if idx2 - idx1 <= 2:
                # Don't connect if jump is too large (discontinuity)
                if abs(y2 - y1) < h / 3:
                    canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
    
    output.config(text=f"Function plotted successfully", fg="green")

def show_text():
    """Handle calculate/plot button based on mode"""
    text = entry.get()
    mode = mode_var.get()
    
    if not text.strip():
        output.config(text="Error: Please enter an expression", fg="red")
        return
    
    try:
        tokens = tokenize(text)
        ast = Parser(tokens).parse()
        
        if mode == "simple":
            # Simple calculation mode
            result = evaluate(ast)
            if isinstance(result, float):
                if result.is_integer():
                    result_str = str(int(result))
                else:
                    result_str = str(round(result, 6))
            else:
                result_str = str(result)
            output.config(text=f"Result: {result_str}", fg="blue")
            draw_grid()  # Show empty grid
            
        elif mode == "functions":
            # Function graphing mode
            # Check if expression contains 'x' variable
            global current_ast
            current_ast = ast
            
            # Try to plot the function
            plot_function(ast)
            
    except Exception as e:
        output.config(text=f"Error: {e}", fg="red")
        if mode == "functions":
            draw_grid()  # Show empty grid on error

button = tk.Button(graph_frame, text="Calculate / Plot", command=show_text, font=("Arial", 11), bg="#4CAF50", fg="white", padx=20, pady=5)
button.pack(pady=5)

# Add info label
info_label = tk.Label(graph_frame, 
                     text="Simple mode: Enter any expression. Functions mode: Enter f(x) using variable 'x'.",
                     font=("Arial", 9), fg="gray")
info_label.pack()

# Bind Enter key to calculate
entry.bind('<Return>', lambda e: show_text())

# Initialize with empty grid
draw_grid()

root.mainloop()