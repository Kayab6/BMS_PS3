import os
from pathlib import Path

import joblib
import numpy as np

from ml.train import DATASET_PATH, train_model

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
ENCODER_PATH = Path(__file__).resolve().parent / "department_encoder.pkl"


def ensure_model_ready():
    if not MODEL_PATH.exists() or not ENCODER_PATH.exists():
        if DATASET_PATH.exists():
            train_model(DATASET_PATH)
        else:
            raise ValueError("The ML model must be trained first. Run python ml/train.py or generate dataset.csv.")


def predict_wait_time(data):
    """Predict waiting time from operational patient queue metrics."""
    required_fields = [
        "urgency",
        "queue_length",
        "icu_availability",
        "bed_availability",
        "doctor_availability",
        "nurse_availability",
        "treatment_duration",
        "department",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(f"Missing required field: {missing[0]}")

    integer_fields = [field for field in required_fields if field != "department"]
    for field in integer_fields:
        value = data[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value):
            raise ValueError(f"{field} must be a finite number")
        if int(value) != value:
            raise ValueError(f"{field} must be a whole number")
        if value < 0:
            raise ValueError(f"{field} must be non-negative")

    if not isinstance(data["department"], str) or not data["department"].strip():
        raise ValueError("department must be a non-empty string")

    ensure_model_ready()

    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)

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

    row = [
        data["urgency"],
        data["queue_length"],
        data["icu_availability"],
        data["bed_availability"],
        data["doctor_availability"],
        data["nurse_availability"],
        data["treatment_duration"],
        data["department"],
    ]

    numeric_values = np.array([[row[0], row[1], row[2], row[3], row[4], row[5], row[6]]], dtype=float)
    department_encoded = encoder.transform(np.array([[row[7]]]))
    prepared = np.hstack([numeric_values, department_encoded])
    prediction = float(model.predict(prepared)[0])
    result = max(0.0, prediction)
    return {"predicted_waiting_time": round(result, 1)}
