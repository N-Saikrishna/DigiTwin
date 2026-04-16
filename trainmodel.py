import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
import joblib
import os

COLS = [
    'current_gpa', 'failed_courses', 'retaken_courses', 'work_hours_per_week',
    'stress_level', 'sleep_hours', 'semester_difficulty', 'extracurricular_load'
]

def derive_targets(data):
    work_norm = ((data['work_hours_per_week'] - 15) / 25.0).clip(0, 1)

    stress_norm = np.where(
        data['stress_level'] <= 5,
        (data['stress_level'] / 5.0) * 0.15,
        0.15 + ((data['stress_level'] - 5) / 5.0) * 0.85
    )

    failed_norm     = (data['failed_courses'] / 5.0).clip(0, 1)
    retaken_norm    = (data['retaken_courses'] / 5.0).clip(0, 1)
    difficulty_norm = (data['semester_difficulty'] / 5.0)
    extra_norm      = (data['extracurricular_load'] / 20.0).clip(0, 1)
    sleep_penalty   = ((8.0 - data['sleep_hours']) / 8.0).clip(0, 1)
    gpa_deficit     = ((4.0 - data['current_gpa']) / 4.0).clip(0, 1)

    burnout = (
        stress_norm     * 0.30 +
        work_norm       * 0.20 +
        sleep_penalty   * 0.15 +
        failed_norm     * 0.15 +
        gpa_deficit     * 0.10 +
        difficulty_norm * 0.05 +
        extra_norm      * 0.03 +
        retaken_norm    * 0.02
    ) * 100

    risk = (stress_norm * 40 + gpa_deficit * 40 + failed_norm * 20)

    return pd.Series(burnout).clip(0, 100), pd.Series(risk).clip(0, 100)


def generate_seed_dataset(n=200):
    np.random.seed(42)
    rows = []
    for _ in range(n):
        stress    = np.random.randint(1, 11)
        work_hrs  = np.random.choice([0,5,10,15,20,25,30,35,40],
                                      p=[0.1,0.1,0.15,0.2,0.15,0.1,0.1,0.05,0.05])
        sleep     = round(np.random.uniform(4.0, 9.5), 1)
        failed    = np.random.choice([0,1,2,3,4,5], p=[0.45,0.25,0.15,0.08,0.04,0.03])
        retaken   = min(failed, np.random.randint(0, failed + 1)) if failed > 0 else 0
        difficulty = np.random.randint(1, 6)
        extra     = np.random.choice([0,2,5,8,10,15,20], p=[0.15,0.2,0.25,0.15,0.1,0.1,0.05])
        base_gpa  = 4.0 - (stress * 0.1) - (failed * 0.25)
        gpa       = round(np.clip(base_gpa + np.random.normal(0, 0.3), 0.0, 4.0), 2)
        rows.append({
            'current_gpa': gpa, 'failed_courses': failed, 'retaken_courses': retaken,
            'work_hours_per_week': work_hrs, 'stress_level': stress, 'sleep_hours': sleep,
            'semester_difficulty': difficulty, 'extracurricular_load': extra
        })
    df = pd.DataFrame(rows)
    df.to_csv('data.csv', index=False)
    print(f"Generated seed dataset with {n} rows -> data.csv")
    return df


def train_brain():
    if os.path.exists('data.csv'):
        df = pd.read_csv('data.csv')
        missing = [c for c in COLS if c not in df.columns]
        if missing:
            print(f"data.csv missing columns {missing}, regenerating seed...")
            df = generate_seed_dataset()
    else:
        print("No data.csv found, generating seed dataset...")
        df = generate_seed_dataset()

    if len(df) < 10:
        print(f"Only {len(df)} rows — padding with seed data...")
        seed = generate_seed_dataset(100)
        df = pd.concat([df, seed], ignore_index=True)

    data = df[COLS].copy()
    data['burnout_probability'], data['risk_score'] = derive_targets(data)

    X = data[COLS]
    bundle = {
        'risk_model':    GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42).fit(X, data['risk_score']),
        'burnout_model': GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42).fit(X, data['burnout_probability'])
    }
    joblib.dump(bundle, 'academic_twin_model.pkl')
    print(f"Model trained on {len(df)} rows.")


if __name__ == "__main__":
    train_brain()
