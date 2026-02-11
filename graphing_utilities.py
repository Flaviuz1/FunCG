import matplotlib.pyplot as plt
import math
from functions import evaluate

num_points = 20000
def plot_function(ast, x_min=-10, x_max=10, y_min=-8, y_max=8):

    x_values = []
    y_values = []
    
    for i in range(num_points):
        x = x_min + (x_max - x_min) * i / num_points
        x_values.append(x)

        try:
            y = evaluate(ast, {"x": x})

            if math.isfinite(y) and y_min <= y <= y_max:
                y_values.append(y)
            else:
                y_values.append(None)

        except:
            y_values.append(None)

    if all(v is None for v in y_values):
        raise ValueError("Function has no valid values in visible range")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_values, y_values, color = 'red', linewidth=2)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True)

    # Optional: hide top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if x_min <= 0 <= x_max:
        ax.axvline(0, color = "#000000")

    if y_min <= 0 <= y_max:
        ax.axhline(0, color = "#000000")

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    return fig
