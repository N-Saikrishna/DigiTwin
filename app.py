from dotenv import load_dotenv
load_dotenv()
import os
import json
from flask import Flask, render_template, request, jsonify
from model import predict_student_outcome, append_to_dataset
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

if not os.path.exists('academic_twin_model.pkl'):
    from trainmodel import train_brain
    train_brain()


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/simulator")
def index():
    return render_template("index.html")


@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    try:
        raw_credits            = [float(c) for c in request.form.getlist("credits[]") if c]
        total_semester_credits = sum(raw_credits)
        semester_type          = request.form.get("semester", "Fall")

        data = {
            "student_name":         request.form.get("student_name", "Student"),
            "major":                request.form.get("major", "Information Technology"),
            "semester":             semester_type,
            "current_gpa":          float(request.form.get("current_gpa") or request.form.get("gpa") or 0),
            "total_credits_earned": float(request.form.get("total_credits_earned", 0)),
            "grades":               [float(g) for g in request.form.getlist("grades[]") if g],
            "credits":              raw_credits,
            "work_hours":           float(request.form.get("work_hours", 0)),
            "stress":               float(request.form.get("stress", 5)),
            "course_names":         request.form.getlist("course_names[]"),
            "target_gpa":           float(request.form.get("target_gpa", 0)) if request.form.get("target_gpa") else None,
            "sleep_hours":          float(request.form.get("sleep_hours") or request.form.get("sleep") or 7),
            "failed_courses":       float(request.form.get("failed", 0)),
            "retaken_courses":      float(request.form.get("retake", 0)),
            "semester_difficulty":  float(request.form.get("difficulty", 3)),
            "extracurricular_load": float(request.form.get("extra", 0)),
        }

        # Append to dataset and retrain
        append_to_dataset(data)

        res = predict_student_outcome(data)

        prediction = {
            "projected_gpa":       res.get("projected_gpa", 0.0),
            "projected_gpa_range": res.get("projected_gpa_range", "N/A"),
            "risk_score":          res.get("risk_score", 0),
            "burnout_probability": res.get("burnout_rate", 0),
            "recommendations":     res.get("recommendations", [])
        }

        warning_msg = None
        if "Summer" in semester_type and total_semester_credits > 8:
            warning_msg = f"CREDIT OVERLOAD: You are taking {int(total_semester_credits)} credits. Summer max is 8!"
        elif ("Fall" in semester_type or "Spring" in semester_type) and total_semester_credits > 15:
            warning_msg = f"CREDIT OVERLOAD: You are taking {int(total_semester_credits)} credits. Fall/Spring max is 15!"

        return render_template("result.html", student=data, prediction=prediction, warning=warning_msg)

    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/dashboard", methods=["POST"])
def dashboard():
    try:
        student_data    = json.loads(request.form.get("student_data"))
        prediction_data = json.loads(request.form.get("prediction_data"))
        names   = student_data.get("course_names", [])
        grades  = student_data.get("grades", [])
        credits = student_data.get("credits", [])
        course_details = []
        term_credits = term_points = 0.0
        for i in range(len(grades)):
            c_name   = names[i] if i < len(names) and names[i] else f"Course {i+1}"
            c_grade  = grades[i]
            c_credit = credits[i]
            letter   = {4.0:"A",3.0:"B",2.0:"C",1.0:"D",0.0:"F"}.get(c_grade, str(c_grade))
            course_details.append({"name": c_name, "grade_letter": letter, "credits": c_credit})
            term_credits += c_credit
            term_points  += (c_grade * c_credit)
        term_gpa = (term_points / term_credits) if term_credits > 0 else 0.0
        return render_template("dashboard.html", student=student_data, prediction=prediction_data,
                               course_details=course_details, term_gpa=term_gpa, term_credits=term_credits)
    except Exception as e:
        return f"Error Loading Dashboard: {str(e)}", 500


@app.route("/chat", methods=["POST"])
def chat():
    try:
        body       = request.get_json()
        question   = body.get("question", "").strip()
        student    = body.get("student", {})
        prediction = body.get("prediction", {})
        if not question:
            return jsonify({"error": "No question provided"}), 400
        grades  = student.get("grades", [])
        credits = student.get("credits", [])
        courses = []
        for i, (g, c) in enumerate(zip(grades, credits)):
            letter = {4.0:"A",3.0:"B",2.0:"C",1.0:"D",0.0:"F"}.get(float(g), str(g))
            courses.append(f"  Course {i+1}: {letter} ({c} credits)")
        courses_text = "\n".join(courses) if courses else "  No courses entered"
        target_gpa  = student.get("target_gpa")
        target_line = f"Target GPA Goal: {target_gpa}" if target_gpa else "Target GPA Goal: Not specified"

        system_prompt = f"""You are an academic advisor AI for a student's Digital Twin simulation. Answer scenario-based questions precisely.

STUDENT PROFILE:
- Name: {student.get('student_name', 'Student')}
- Current Cumulative GPA: {student.get('current_gpa')}
- Total Credits Earned: {student.get('total_credits_earned')}
- {target_line}

CURRENT SEMESTER COURSES:
{courses_text}

SIMULATION RESULTS:
- Projected GPA: {prediction.get('projected_gpa')}
- Academic Risk Score: {prediction.get('risk_score')}%
- Burnout Probability: {prediction.get('burnout_probability')}%

Keep responses concise, friendly, and specific. Show math when doing GPA calculations."""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4500,
            system=system_prompt,
            messages=[{"role": "user", "content": question}]
        )
        return jsonify({"response": message.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
