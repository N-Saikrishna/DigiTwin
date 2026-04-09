from flask import Flask, render_template, request
from model import predict_student_outcome

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    try:
        # 1. Capture the new Target GPA from the form
        # We use the name="target_gpa" from the new index.html
        user_target = float(request.form.get("target_gpa", 3.0)) 
        
        current_gpa = float(request.form.get("current_gpa", 0))
        total_credits_earned = float(request.form.get("total_credits_earned", 0))

        # 2. Capture lists from the 6-course grid
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
        
        # 3. Get machine learning results from model.py
        res = predict_student_outcome(data)
        
        # 4. Calculate Goal Math using the dynamic user_target
        total_credits_after = total_credits_earned + sum(credits_list)
        
        if sum(credits_list) > 0:
            # How many points do they need this term to hit the user's specific target?
            points_needed = (user_target * total_credits_after) - (current_gpa * total_credits_earned)
            avg_needed = points_needed / sum(credits_list)
        else:
            avg_needed = 0

        # Determine if they are "On Track" based on the high end of the predicted range
        # We extract the high number from the string "3.55 - 3.75"
        high_val = float(res["projected_gpa_range"].split(" - ")[1])
        goal_status = "On Track" if high_val >= user_target else "Behind Schedule"

        # 5. Map everything to the result.html variables
        prediction = {
            "gpa_range": res["projected_gpa_range"],
            "risk_score": res["risk_score"],
            "burnout_probability": res["burnout_rate"],
            "recommendations": [res["advice"]],
            "goal_status": goal_status,
            "target_needed": round(avg_needed, 2),
            "user_goal": user_target  # Pass this so result.html can display it
        }
        
        return render_template("result.html", student=data, prediction=prediction)

    except ValueError:
        return "Error: Please ensure all inputs (GPA, Credits, Target) are valid numbers.", 400

if __name__ == "__main__":
    app.run(debug=True, port=5001)

if __name__ == "__main__":
    # Using port 5001 as per your previous screenshot
    app.run(debug=True, port=5001)
