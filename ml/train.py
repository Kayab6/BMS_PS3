import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder

DATASET_PATH = Path(__file__).resolve().parent / "dataset.csv"
MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
ENCODER_PATH = Path(__file__).resolve().parent / "department_encoder.pkl"


def generate_synthetic_dataset(path: Path = DATASET_PATH, rows: int = 1200):
    rng = np.random.default_rng(42)
    departments = ["Emergency", "ICU", "Cardiology", "Neurology", "General Medicine", "Gynecology"]
    records = []

    for _ in range(rows):
        department = departments[rng.integers(0, len(departments))]
        urgency = int(rng.integers(1, 6))
        queue_length = int(rng.integers(2, 18))
        icu_availability = int(rng.integers(0, 5))
        bed_availability = int(rng.integers(1, 10))
        doctor_availability = int(rng.integers(1, 8))
        nurse_availability = int(rng.integers(2, 12))
        treatment_duration = int(rng.integers(15, 180))
        base_wait = (
            urgency * 4
            + queue_length * 2
            + (5 - icu_availability) * 5
            + (5 - bed_availability) * 3
            + max(0, 4 - doctor_availability) * 3
            + max(0, 6 - nurse_availability) * 1.5
        )
        noise = rng.normal(0, 6)
        actual_wait = max(0, int(base_wait + noise + (department == "Emergency") * 8))
        records.append(
            {
                "urgency": urgency,
                "queue_length": queue_length,
                "icu_availability": icu_availability,
                "bed_availability": bed_availability,
                "doctor_availability": doctor_availability,
                "nurse_availability": nurse_availability,
                "treatment_duration": treatment_duration,
                "department": department,
                "actual_waiting_time": actual_wait,
            }
        )

    dataframe = pd.DataFrame(records)
    dataframe.to_csv(path, index=False)
    return dataframe


def train_model(dataset_path: Path = DATASET_PATH):
    if not dataset_path.exists():
        dataset = generate_synthetic_dataset(dataset_path)
    else:
        dataset = pd.read_csv(dataset_path)

    features = [
        "urgency",
        "queue_length",
        "icu_availability",
        "bed_availability",
        "doctor_availability",
        "nurse_availability",
        "treatment_duration",
        "department",
    ]
    target = "actual_waiting_time"

    X = dataset[features]
    y = dataset[target]

    numeric_columns = [col for col in features if col != "department"]
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    department_encoded = encoder.fit_transform(X[["department"]])
    numeric_values = X[numeric_columns].to_numpy()
    X_ready = np.hstack([numeric_values, department_encoded])

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_ready, y)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)
    return model, encoder


if __name__ == "__main__":
    train_model()
    print(f"Training complete. Model saved to {MODEL_PATH}")
