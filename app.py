from flask import Flask, request, jsonify, send_from_directory
import os
import math_engine
BACKEND = "C++ (PyBind11)"

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/evaluate", methods=["POST"])
def evaluate():
    data = request.json
    expr = data.get("expr", "").strip()
    if not expr:
        return jsonify({"error": "Empty expression"}), 400
    try:
        result = math_engine.evaluate(expr)
        import math
        if isinstance(result, float):
            if not math.isfinite(result):
                return jsonify({"result": str(result)})
            # Snap to integer if very close
            rounded_int = round(result)
            if abs(result - rounded_int) < 1e-6 * max(1.0, abs(rounded_int)):
                return jsonify({"result": int(rounded_int)})
            # Round to 6 sig figs
            from decimal import Decimal
            import math as m
            if result != 0:
                magnitude = m.floor(m.log10(abs(result)))
                factor = 10 ** (6 - 1 - magnitude)
                result = round(result * factor) / factor
            return jsonify({"result": result})
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/graph", methods=["POST"])
def graph():
    data = request.json
    expr   = data.get("expr", "").strip()
    x_min  = float(data.get("x_min", -10))
    x_max  = float(data.get("x_max",  10))
    y_min  = float(data.get("y_min",  -8))
    y_max  = float(data.get("y_max",   8))
    points = int(data.get("points", 1000))
    if not expr:
        return jsonify({"error": "Empty expression"}), 400
    try:
        xs, ys = math_engine.evaluate_for_graph(expr, x_min, x_max, points, y_min, y_max)
        import math
        clean_ys = [None if (y is None or not math.isfinite(y)) else y for y in ys]
        return jsonify({"xs": list(xs), "ys": clean_ys})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/info")
def info():
    return jsonify({"backend": BACKEND})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
