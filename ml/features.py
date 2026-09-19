"""Feature utilities for the MEDFLOW waiting-time prediction model."""

from __future__ import annotations

from typing import Any

FEATURE_COLUMNS = [
    "urgency",
    "queue_length",
    "icu_availability",
    "bed_availability",
    "doctor_availability",
    "nurse_availability",
    "treatment_duration",
    "department",
]

TARGET_COLUMN = "actual_waiting_time"


def build_feature_row(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert a patient/environment payload into the ML feature schema."""
    row = {
        "urgency": int(payload.get("urgency", 1)),
        "queue_length": int(payload.get("queue_length", 0)),
        "icu_availability": int(payload.get("icu_availability", 0)),
        "bed_availability": int(payload.get("bed_availability", 0)),
        "doctor_availability": int(payload.get("doctor_availability", 0)),
        "nurse_availability": int(payload.get("nurse_availability", 0)),
        "treatment_duration": int(payload.get("treatment_duration", 0)),
        "department": str(payload.get("department", "General Medicine")),
    }
    return row


def prepare_features(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize a list of metric dictionaries into the model input format."""
    return [build_feature_row(item) for item in data]


def feature_vector_for_prediction(payload: dict[str, Any]) -> list[float | str]:
    """Return the ordered feature list used by the model pipeline."""
    row = build_feature_row(payload)
    return [
        row["urgency"],
        row["queue_length"],
        row["icu_availability"],
        row["bed_availability"],
        row["doctor_availability"],
        row["nurse_availability"],
        row["treatment_duration"],
        row["department"],
    ]
