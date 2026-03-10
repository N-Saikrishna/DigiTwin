from flask import Flask, render_template, request, redirect, url_for, session
from model import predict_student_outcome

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secure-secret-key"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/profile")
def profile():
    student_profile = session.get("student_profile", {})
    return render_template("profile.html", profile=student_profile)


@app.route("/data", methods=["GET", "POST"])
def data_entry():
    if request.method == "POST":
        student_data = {
            "name": request.form.get("name", "").strip(),
            "major": request.form.get("major", "").strip(),
            "current_gpa": float(request.form.get("current_gpa", 0) or 0),
            "credit_hours": int(request.form.get("credit_hours", 0) or 0),
            "failed_courses": int(request.form.get("failed_courses", 0) or 0),
            "retaken_courses": int(request.form.get("retaken_courses", 0) or 0),
            "work_hours_per_week": int(request.form.get("work_hours_per_week", 0) or 0),
            "stress_level": int(request.form.get("stress_level", 1) or 1),
            "sleep_hours": float(request.form.get("sleep_hours", 0) or 0),
            "semester_difficulty": int(request.form.get("semester_difficulty", 1) or 1),
            "extracurricular_load": int(request.form.get("extracurricular_load", 0) or 0),
        }

        session["student_profile"] = student_data
        prediction = predict_student_outcome(student_data)

        return render_template(
            "result.html",
            student=student_data,
            prediction=prediction
        )

    return render_template("data_entry.html")


if __name__ == "__main__":
    app.run(debug=True)
