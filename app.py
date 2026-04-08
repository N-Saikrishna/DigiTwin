from flask import Flask, render_template, request
from model import predict_student_outcome

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/survey")
def survey():
    return render_template("survey.html")

@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    grades = request.form.getlist("grades[]")
    credits = request.form.getlist("credits[]")

    try:
        grades = [float(g) for g in grades if g]
        credits = [int(c) for c in credits if c]
    except ValueError:
        return "Invalid input in grades or credits", 400

    data = {
        "student_name": request.form.get("student_name"),
        "grades": grades,
        "credits": credits,
        "failed_courses": request.form.get("failed", 0),
        "retaken_courses": request.form.get("retake", 0),
        "work_hours_per_week": request.form.get("work_hours", 0),
        "stress_level": request.form.get("stress", 5),
        "sleep_hours": request.form.get("sleep", 7),
        "semester_difficulty": request.form.get("difficulty", 3),
        "extracurricular_load": request.form.get("extra", 0)
    }
    
    prediction = predict_student_outcome(data)
    return render_template("result.html", student=data, prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
