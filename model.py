import joblib
import numpy as np
import os

def calculate_gpa(grades, credits):
    """Calculates weighted GPA based on grades and credit hours."""
    if not grades or not credits or len(grades) != len(credits):
        return 0.0
    
    total_points = sum(g * c for g, c in zip(grades, credits))
    total_credits = sum(credits)
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

def predict_student_outcome(student):
    model_path = 'academic_twin_model.pkl'
    
    if not os.path.exists(model_path):
        return {"error": "Run trainmodel.py first!"}

    try:
        bundle = joblib.load(model_path)
        
        
        calculated_gpa = calculate_gpa(student['grades'], student['credits'])
        
        # Must be in the EXACT same order as X in trainmodel.py
        features = np.array([[
            float(calculated_gpa), 
            int(student['failed_courses']),
            int(student['retaken_courses']),
            int(student['work_hours_per_week']),
            int(student['stress_level']),
            float(student['sleep_hours']),
            int(student['semester_difficulty']),
            int(student['extracurricular_load'])
        ]])

        return {
            "calculated_gpa": calculated_gpa, 
            "projected_gpa": round(float(bundle['gpa_model'].predict(features)[0]), 2),
            "risk_score": int(bundle['risk_model'].predict(features)[0]),
            "burnout_probability": int(bundle['burnout_model'].predict(features)[0]),
            "recommendations": generate_recs(student, calculated_gpa)
        }
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

def generate_recs(student, current_gpa):
    recs = []
    if int(student['work_hours_per_week']) > 20:
        recs.append("High work hours detected. Consider a 15h cap.")
    if float(student['sleep_hours']) < 6:
        recs.append("Prioritize sleep to reduce burnout risk.")
    if current_gpa < 2.5:
        recs.append("GPA is below 2.5. Consider reducing credit load next semester.")
    return recs if recs else ["Current load is balanced."]
