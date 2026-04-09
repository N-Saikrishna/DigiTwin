from flask import Flask, render_template, request
from model import predict_student_outcome

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    try:
        # Convert baseline stats to float immediately
        current_gpa = float(request.form.get("current_gpa", 0))
        total_credits_earned = float(request.form.get("total_credits_earned", 0))

        # Capture lists from the 6-column grid
        grades_list = [float(g) for g in request.form.getlist("grades[]") if g]
        credits_list = [float(c) for c in request.form.getlist("credits[]") if c]

        data = {
            "student_name": request.form.get("student_name", "Student"),
            "current_gpa": current_gpa,
            "total_credits_earned": total_credits_earned,
            "grades": grades_list,
            "credits": credits_list,
            "failed_courses": int(request.form.get("failed", 0)),
            "work_hours": float(request.form.get("work_hours", 0)),
            "stress": float(request.form.get("stress", 5))
        }
        
        # Get result from model.py
        res = predict_student_outcome(data)
        
        # Map results to variables used in result.html
        prediction = {
            "projected_gpa": res["projected_gpa"],
            "risk_score": res["risk_score"],
            "burnout_probability": res["burnout_rate"],
            "recommendations": [res["advice"]]
        }
        
        return render_template("result.html", student=data, prediction=prediction)

    except ValueError:
        return "Error: Please ensure GPA and Credits are valid numbers.", 400

if __name__ == "__main__":
    app.run(debug=True, port=5001)
