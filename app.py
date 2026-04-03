from flask import Flask, render_template, request
from model import predict_student_outcome

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/survey")
def survey():
    return render_template("survey.html")

@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    # We pull the data directly from the form and pass it to the model
    # No database, no saving—just instant results
    student_data = {
        "name": request.form.get("student_name", "Knight"),
        "current_gpa": float(request.form.get("gpa") or 0.0),
        "failed_courses": int(request.form.get("failed") or 0),
        "retaken_courses": int(request.form.get("retake") or 0),
        "work_hours_per_week": int(request.form.get("work_hours") or 0),
        "stress_level": int(request.form.get("stress") or 5),
        "sleep_hours": float(request.form.get("sleep") or 7.0),
        "semester_difficulty": int(request.form.get("difficulty") or 3),
        "extracurricular_load": int(request.form.get("extra") or 0)
    }
    
    prediction = predict_student_outcome(student_data)
    
    return render_template("result.html", student=student_data, prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
