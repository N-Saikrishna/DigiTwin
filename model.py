import numpy as np
import joblib

def predict_student_outcome(student):
    try:
        bundle = joblib.load('academic_twin_model.pkl')
        
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

        pred_gpa = bundle['gpa_model'].predict(features)[0]
        pred_risk = bundle['risk_model'].predict(features)[0]
        pred_burnout = bundle['burnout_model'].predict(features)[0]

        recommendations = []
        if int(student['work_hours_per_week']) > 20:
            recommendations.append("High work hours detected. Consider a 15h cap to protect your GPA.")
        if float(student['sleep_hours']) < 6:
            recommendations.append("Sleep deprivation is your highest risk factor for burnout.")
        if not recommendations:
            recommendations.append("Current load is balanced. Continue your current routine.")

        return {
            "projected_gpa": round(max(0, min(4.0, float(pred_gpa))), 2),
            "risk_score": int(max(0, min(100, pred_risk))),
            "burnout_probability": int(max(0, min(100, pred_burnout))),
            "recommendations": recommendations
        }
    except Exception as e:
        return {"error": "Prediction failed. Check model file."}