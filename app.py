from flask import Flask, render_template, request
from model import predict_student_outcome

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    try:
        # 1. Capture basic inputs
        current_gpa = float(request.form.get("current_gpa", 0))
        total_credits_earned = float(request.form.get("total_credits_earned", 0))

        # 2. Capture lists from the 6-column grid
        # request.form.getlist collects all inputs with the same name into a list
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
        
        # 3. Get results from your updated model.py
        res = predict_student_outcome(data)
        
        # --- GOAL MATH (Targeting 3.85) ---
        target = 3.85
        total_credits_after = total_credits_earned + sum(credits_list)
        
        # Calculate what term GPA is needed to reach the cumulative target
        if sum(credits_list) > 0:
            points_needed = (target * total_credits_after) - (current_gpa * total_credits_earned)
            avg_needed = points_needed / sum(credits_list)
        else:
            avg_needed = 0

        # Determine status based on the high-end of the range from model.py
        # We split the string "3.63 - 3.83" to get the high number for comparison
        high_val = float(res["projected_gpa_range"].split(" - ")[1])
        goal_status = "On Track" if high_val >= target else "Behind Schedule"
        
        # 4. Map results to variables used in result.html
        prediction = {
            "gpa_range": res["projected_gpa_range"], # The "3.63 - 3.83" string
            "risk_score": res["risk_score"],
            "burnout_probability": res["burnout_rate"],
            "recommendations": [res["advice"]],
            "goal_status": goal_status,
            "target_needed": round(avg_needed, 2)
        }
        
        return render_template("result.html", student=data, prediction=prediction)

    except ValueError:
        return "Error: Please ensure all inputs are valid numbers.", 400

if __name__ == "__main__":
    # Using port 5001 as per your previous screenshot
    app.run(debug=True, port=5001)