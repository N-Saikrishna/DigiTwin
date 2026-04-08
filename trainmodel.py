import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import numpy as np

def train_brain():
    # Load the source dataset
    df_src = pd.read_csv('student_habits_performance.csv')
    
    data = pd.DataFrame()
    
    # This aligns with the "Heavy course loads" and "Stacked technical classes" goals 
    data['total_credits'] = (df_src['age'] % 12) + 3 # Simulating a range of 3-15 credits
    
    # Calculate current GPA based on exam scores 
    data['current_gpa'] = (df_src['exam_score'] / 25.0).clip(0, 4.0)
    
    data['failed_courses'] = df_src['exam_score'].apply(lambda x: 1 if x < 40 else 0)
    data['retaken_courses'] = df_src['exam_score'].apply(lambda x: 1 if x < 55 else 0)
    data['work_hours_per_week'] = df_src['part_time_job'].apply(lambda x: 15 if x == 'Yes' else 0)
    data['stress_level'] = (11 - df_src['mental_health_rating']).clip(1, 10)
    data['sleep_hours'] = df_src['sleep_hours']
    data['semester_difficulty'] = (df_src['age'] % 5) + 1
    data['extracurricular_load'] = df_src['extracurricular_participation'].apply(lambda x: 3 if x == 'Yes' else 1)

    
   
    data['projected_gpa'] = (
        data['current_gpa'] * 0.50 
        - data['stress_level'] * 0.05 
        - data['total_credits'] * 0.01  
        - data['failed_courses'] * 0.10 
        + data['sleep_hours'] * 0.03 
        - data['work_hours_per_week'] * 0.005
    ).clip(0, 4.0)


    data['risk_score'] = (
        data['stress_level'] * 8 
        + data['total_credits'] * 2     
        + data['failed_courses'] * 15 
        + data['work_hours_per_week'] * 0.8 
        - data['sleep_hours'] * 3 
        - data['current_gpa'] * 8
    ).clip(0, 100)

    data['burnout_probability'] = (
        data['stress_level'] * 7 
        + data['total_credits'] * 3     
        + data['work_hours_per_week'] * 0.7 
        - data['sleep_hours'] * 4 
        + data['failed_courses'] * 10 
        - data['current_gpa'] * 5
    ).clip(0, 100)

    # consistent with the order used in model.py
    X = data[['current_gpa', 'failed_courses', 'retaken_courses', 'work_hours_per_week', 
             'stress_level', 'sleep_hours', 'semester_difficulty', 'extracurricular_load']]

    bundle = {
        'gpa_model': LinearRegression().fit(X, data['projected_gpa']),
        'risk_model': LinearRegression().fit(X, data['risk_score']),
        'burnout_model': LinearRegression().fit(X, data['burnout_probability'])
    }

    joblib.dump(bundle, 'academic_twin_model.pkl')
    print("✅ Model trained successfully with Credit-Weighting logic.")

if __name__ == "__main__":
    train_brain()
