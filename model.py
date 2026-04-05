import joblib
import numpy as np
import os

def predict_student_outcome(student):
    model_path = 'academic_twin_model.pkl'
    
    if not os.path.exists(model_path):
        return {"error": "Run trainmodel.py first!"}

    try:
        bundle = joblib.load(model_path)
        
        # Must be in the EXACT same order as X in trainmodel.py
        features = np.array([[
            float(student['current_gpa']),
            int(student['failed_courses']),
            int(student['retaken_courses']),
            int(student['work_hours_per_week']),
            int(student['stress_level']),
            float(student['sleep_hours']),
            int(student['semester_difficulty']),
            int(student['extracurricular_load'])
        ]])

        return {
            "projected_gpa": round(float(bundle['gpa_model'].predict(features)[0]), 2),
            "risk_score": int(bundle['risk_model'].predict(features)[0]),
            "burnout_probability": int(bundle['burnout_model'].predict(features)[0]),
            "recommendations": generate_recs(student)
        }
    except:
        return {"error": "Prediction failed."}

def generate_recs(student):
    recs = []
    if int(student['work_hours_per_week']) > 20:
        recs.append("High work hours detected. Consider a 15h cap.")
    if float(student['sleep_hours']) < 6:
        recs.append("Prioritize sleep to reduce burnout risk.")
    return recs if recs else ["Current load is balanced."]
