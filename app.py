from flask import Flask, render_template, request, jsonify
from model_loader import model

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True) or {}

        user_input = {
            "funding_total": float(data.get("funding_total", 0)),
            "funding_rounds": int(data.get("funding_rounds", 0)),
            "startup_age": float(data.get("startup_age", 0)),
            "milestones": int(data.get("milestones", 0)),
            "relationships": int(data.get("relationships", 0)),
            "avg_participants": float(data.get("avg_participants", 0)),
            "category": data.get("category", "software"),
            "state": data.get("state", "other"),
            "has_vc": int(data.get("has_vc", 0)),
            "has_angel": int(data.get("has_angel", 0)),
            "has_roundA": int(data.get("has_roundA", 0)),
            "is_top500": int(data.get("is_top500", 0)),
        }

        result = model.predict(user_input)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
