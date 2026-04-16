from dotenv import load_dotenv
load_dotenv()
import joblib
import os
import numpy as np
import pandas as pd

COLS = [
    'current_gpa', 'failed_courses', 'retaken_courses', 'work_hours_per_week',
    'stress_level', 'sleep_hours', 'semester_difficulty', 'extracurricular_load'
]


def calculate_gpa(current_gpa, total_credits_earned, grades, credits):
    semester_points = semester_credits = 0.0
    for grade, credit in zip(grades, credits):
        if credit > 0:
            semester_points  += grade * credit
            semester_credits += credit
    total_points  = (current_gpa * total_credits_earned) + semester_points
    total_credits = total_credits_earned + semester_credits
    if total_credits == 0:
        return current_gpa
    return max(0.0, min(4.0, total_points / total_credits))


def _formula_fallback(work_hours, stress, sleep, failed_courses, retaken_courses,
                      semester_difficulty, extracurricular_load, final_gpa):
    work_norm = min(max(0, (work_hours - 15) / 25.0), 1.0)
    if stress <= 5:
        stress_norm = (stress / 5.0) * 0.15
    else:
        stress_norm = 0.15 + ((stress - 5) / 5.0) * 0.85
    failed_norm     = min(failed_courses / 5.0, 1.0)
    retaken_norm    = min(retaken_courses / 5.0, 1.0)
    difficulty_norm = semester_difficulty / 5.0
    extra_norm      = min(extracurricular_load / 20.0, 1.0)
    sleep_penalty   = max((8.0 - sleep) / 8.0, 0.0)
    gpa_deficit     = max(0, 4.0 - final_gpa) / 4.0

    burnout = (
        stress_norm * 0.30 + work_norm * 0.20 + sleep_penalty * 0.15 +
        failed_norm * 0.15 + gpa_deficit * 0.10 + difficulty_norm * 0.05 +
        extra_norm * 0.03 + retaken_norm * 0.02
    ) * 100
    risk = (stress_norm * 0.40 + gpa_deficit * 0.40 + failed_norm * 0.20) * 100
    return int(np.clip(burnout, 5, 98)), int(np.clip(risk, 5, 98))


def append_to_dataset(data, csv_path='data.csv'):
    row = {
        'current_gpa':          data.get('current_gpa', 0.0),
        'failed_courses':       data.get('failed_courses', 0),
        'retaken_courses':      data.get('retaken_courses', 0),
        'work_hours_per_week':  data.get('work_hours', 0),
        'stress_level':         data.get('stress', 5),
        'sleep_hours':          data.get('sleep_hours', 7),
        'semester_difficulty':  data.get('semester_difficulty', 3),
        'extracurricular_load': data.get('extracurricular_load', 0),
    }
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(csv_path, index=False)
    try:
        from trainmodel import train_brain
        train_brain()
    except Exception as e:
        print(f"Retrain failed: {e}")


def predict_student_outcome(data):
    current_gpa          = data.get('current_gpa', 0.0)
    total_credits_earned = data.get('total_credits_earned', 0.0)
    grades               = data.get('grades', [])
    credits              = data.get('credits', [])
    work_hours           = data.get('work_hours', 0)
    stress               = data.get('stress', 5)
    sleep                = data.get('sleep_hours', 7)
    failed_courses       = data.get('failed_courses', 0)
    retaken_courses      = data.get('retaken_courses', 0)
    semester_difficulty  = data.get('semester_difficulty', 3)
    extracurricular_load = data.get('extracurricular_load', 0)

    final_gpa     = calculate_gpa(current_gpa, total_credits_earned, grades, credits)
    gpa_range_str = f"{max(0.0, final_gpa - 0.05):.2f} - {min(4.0, final_gpa + 0.05):.2f}"

    burnout_rate = risk_score = 0
    use_fallback = True

    if os.path.exists('academic_twin_model.pkl'):
        try:
            bundle = joblib.load('academic_twin_model.pkl')
            X = pd.DataFrame([[current_gpa, failed_courses, retaken_courses, work_hours,
                               stress, sleep, semester_difficulty, extracurricular_load]],
                             columns=COLS)
            burnout_rate = int(np.clip(bundle['burnout_model'].predict(X)[0], 5, 98))
            risk_score   = int(np.clip(bundle['risk_model'].predict(X)[0], 5, 98))
            use_fallback = False
        except Exception as e:
            print(f"Model predict failed: {e}")

    if use_fallback:
        burnout_rate, risk_score = _formula_fallback(
            work_hours, stress, sleep, failed_courses,
            retaken_courses, semester_difficulty, extracurricular_load, final_gpa
        )

    return {
        "projected_gpa":       f"{final_gpa:.2f}",
        "projected_gpa_range": gpa_range_str,
        "risk_score":          risk_score,
        "burnout_rate":        burnout_rate,
        "advice":              "Growth Mode" if final_gpa > current_gpa else "Maintenance Mode"
    }
