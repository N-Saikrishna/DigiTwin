#NEEDS TO BE UPDATED AND IMPROVED WITH A TRAINED ML MODEL

def clamp(value, minimum, maximum):
    """Ensures a number stays within a specific range (e.g., 0-100 for percentage)."""
    return max(minimum, min(value, maximum))

def predict_student_outcome(student):
    """
    Processes student data to forecast academic risk, burnout, and GPA.
    Input: 'student' dictionary from the Flask form.
    """
    # 1. Extract data from the dictionary
    gpa = student.get("current_gpa", 0.0)
    failed = student.get("failed_courses", 0)
    retaken = student.get("retaken_courses", 0)
    work_hours = student.get("work_hours_per_week", 0)
    stress = student.get("stress_level", 1)
    sleep = student.get("sleep_hours", 7)
    difficulty = student.get("semester_difficulty", 1)
    extra = student.get("extracurricular_load", 0)

    # 2. Calculate the Risk Score (0-100)
    risk_score = 0

    # GPA Impact (Lower GPA = Higher Risk)
    if gpa < 2.5: risk_score += 30
    elif gpa < 3.0: risk_score += 20
    elif gpa < 3.5: risk_score += 10
    else: risk_score += 3

    # Academic History Impact
    risk_score += (failed * 8) + (retaken * 4)

    # Workload Impact
    if work_hours > 25: risk_score += 15
    elif work_hours > 15: risk_score += 8
    
    risk_score += (difficulty * 5) + (extra * 3)

    # Wellbeing Impact (Stress & Sleep)
    risk_score += (stress * 6)
    
    if sleep < 5: risk_score += 15
    elif sleep < 6.5: risk_score += 8
    elif sleep >= 8: risk_score -= 5  # Bonus for good sleep!

    # Keep risk within 0-100 bounds
    risk_score = clamp(risk_score, 0, 100)

    # 3. Calculate Projected GPA Change
    # High risk leads to GPA drops; low risk leads to GPA growth
    if risk_score < 25:
        projected_delta = 0.20
    elif risk_score < 50:
        projected_delta = 0.05
    elif risk_score < 75:
        projected_delta = -0.15
    else:
        projected_delta = -0.40

    projected_gpa = clamp(round(gpa + projected_delta, 2), 0.0, 4.0)

    # 4. Burnout and Graduation Outlook
    burnout_prob = clamp(int(risk_score * 1.1), 0, 100)
    
    if risk_score < 35:
        outlook = "On track for expected graduation timeline."
    elif risk_score < 65:
        outlook = "Moderate risk of delay. Monitor workload closely."
    else:
        outlook = "High risk of delayed graduation. Academic intervention suggested."

    # 5. Generate Dynamic Recommendations
    recommendations = []
    if work_hours > 20:
        recommendations.append("Consider reducing work hours during heavy exam weeks.")
    if stress >= 7:
        recommendations.append("High stress detected. Schedule a check-in with your advisor.")
    if sleep < 6.5:
        recommendations.append("Increasing sleep to 7+ hours could significantly lower burnout risk.")
    if difficulty >= 4:
        recommendations.append("Balance high-difficulty STEM labs with lighter electives next term.")
    
    # Default if everything is looking good
    if not recommendations:
        recommendations.append("Current profile is stable. Maintain your current study/rest balance.")

    # 6. Return the full analysis dictionary
    return {
        "risk_score": risk_score,
        "projected_gpa": projected_gpa,
        "burnout_probability": burnout_prob,
        "graduation_outlook": outlook,
        "recommendations": recommendations
    }
