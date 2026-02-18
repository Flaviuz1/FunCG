import math
import matplotlib.pyplot as plt
import math_engine


def plot_function(expr: str, x_min=-10, x_max=10, y_min=-8, y_max=8, num_points=1000):
    """
    Plot f(x) by evaluating it in C++.
    Accepts the raw expression string rather than a pre-built AST.
    """
    xs, ys = math_engine.evaluate_for_graph(expr, x_min, x_max, num_points)

    # Replace NaN and out-of-range y values with None for matplotlib
    plot_ys = []
    for y in ys:
        if math.isnan(y) or not (y_min <= y <= y_max):
            plot_ys.append(None)
        else:
            plot_ys.append(y)

    if all(v is None for v in plot_ys):
        raise ValueError("Function has no valid values in visible range")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(xs, plot_ys, color="red", linewidth=2)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if x_min <= 0 <= x_max:
        ax.axvline(0, color="#000000")
    if y_min <= 0 <= y_max:
        ax.axhline(0, color="#000000")

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    return fig
