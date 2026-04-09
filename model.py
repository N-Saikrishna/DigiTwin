def predict_student_outcome(data):
    # Retrieve data from dictionary
    old_gpa = data['current_gpa']
    old_credits = data['total_credits_earned']
    
    # 1. Calculate Starting Points (GPA * Credits)
    starting_points = old_gpa * old_credits
    
    # 2. Calculate New Semester Points (Grade * Credits for each class)
    # Using zip ensures we pair the right grade with the right credit amount
    semester_points = sum(g * c for g, c in zip(data['grades'], data['credits']))
    semester_credits = sum(data['credits'])
    
    # 3. Final Cumulative Calculation
    total_points = starting_points + semester_points
    total_sum_credits = old_credits + semester_credits
    
    if total_sum_credits > 0:
        final_gpa = total_points / total_sum_credits
    else:
        final_gpa = old_gpa

    # 4. Determine Risk and Burnout
    risk = 15 if final_gpa >= 3.0 else 45
    if data.get('failed_courses', 0) > 0: risk += 20
        
    burnout = (data['work_hours'] * 2.2) + (data['stress'] * 4)

    return {
        "projected_gpa": f"{final_gpa:.2f}",
        "risk_score": min(95, int(risk)),
        "burnout_rate": min(98, int(burnout)),
        "advice": "Excellent trajectory! Your GPA is showing strong growth." if final_gpa > old_gpa else "Solid work. Keep focused on your study-life balance."
    }
