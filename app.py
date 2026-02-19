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
            elif result == int(result) and abs(result) < 1e15:
                return jsonify({"result": int(result)})
            else:
                return jsonify({"result": round(result, 3)})
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/graph", methods=["POST"])
def graph():
    data = request.json
    expr   = data.get("expr", "").strip()
    x_min  = float(data.get("x_min", -10))
    x_max  = float(data.get("x_max",  10))
    points = int(data.get("points", 800))
    if not expr:
        return jsonify({"error": "Empty expression"}), 400
    try:
        xs, ys = math_engine.evaluate_for_graph(expr, x_min, x_max, points)
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
