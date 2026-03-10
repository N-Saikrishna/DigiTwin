#NEEDS TO BE UPDATED AND IMPROVED WITH A TRAINED ML MODEL

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def predict_student_outcome(student):
    gpa = student["current_gpa"]
    failed = student["failed_courses"]
    retaken = student["retaken_courses"]
    work_hours = student["work_hours_per_week"]
    stress = student["stress_level"]
    sleep = student["sleep_hours"]
    difficulty = student["semester_difficulty"]
    extracurricular = student["extracurricular_load"]

    risk_score = 0

    # GPA impact
    if gpa < 2.5:
        risk_score += 30
    elif gpa < 3.0:
        risk_score += 20
    elif gpa < 3.5:
        risk_score += 10
    else:
        risk_score += 3

    # Academic history
    risk_score += failed * 8
    risk_score += retaken * 4

    # Workload / outside pressure
    if work_hours > 25:
        risk_score += 15
    elif work_hours > 15:
        risk_score += 8

    risk_score += difficulty * 5
    risk_score += extracurricular * 3

    # Wellbeing
    risk_score += stress * 6
    if sleep < 5:
        risk_score += 15
    elif sleep < 6.5:
        risk_score += 8
    elif sleep >= 8:
        risk_score -= 4

    risk_score = clamp(risk_score, 0, 100)

    # Projected GPA change
    projected_delta = 0.0
    if risk_score < 20:
        projected_delta = 0.20
    elif risk_score < 35:
        projected_delta = 0.10
    elif risk_score < 50:
        projected_delta = 0.00
    elif risk_score < 70:
        projected_delta = -0.15
    else:
        projected_delta = -0.30

    projected_gpa = clamp(round(gpa + projected_delta, 2), 0.0, 4.0)

    # Burnout probability
    burnout_probability = clamp(int(risk_score * 1.1), 0, 100)

    # Graduation impact
    if risk_score < 30:
        graduation_outlook = "On track for expected graduation timeline."
    elif risk_score < 55:
        graduation_outlook = "Moderate risk of delay if workload increases."
    else:
        graduation_outlook = "High risk of delayed graduation unless academic load is adjusted."

    # Advice generation
    recommendations = []

    if work_hours > 20:
        recommendations.append("Consider reducing work hours during heavy academic terms.")
    if stress >= 4:
        recommendations.append("Meet with an advisor or counselor to address stress and workload.")
    if failed > 0 or retaken > 0:
        recommendations.append("Review prerequisite sequencing and retake planning with an academic advisor.")
    if sleep < 6.5:
        recommendations.append("Improving sleep consistency may reduce burnout risk.")
    if difficulty >= 4:
        recommendations.append("Consider balancing technical courses with lighter electives next semester.")

    if not recommendations:
        recommendations.append("Current profile looks stable. Maintain consistent study and recovery habits.")

    return {
        "risk_score": risk_score,
        "projected_gpa": projected_gpa,
        "burnout_probability": burnout_probability,
        "graduation_outlook": graduation_outlook,
        "recommendations": recommendations
    }
