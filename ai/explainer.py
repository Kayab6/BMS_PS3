import os

from huggingface_hub import InferenceClient

SYSTEM_PROMPT = (
    "You are an operations analyst for a hospital simulation. "
    "Analyze ONLY the provided operational metrics. "
    "Do not diagnose patients. "
    "Do not recommend medical treatment. "
    "Do not make clinical decisions. "
    "Identify: 1. Main operational bottleneck 2. Resource pressure 3. Waiting-time issue 4. Inventory issue 5. Concise operational observation. "
    "Base every statement only on the supplied metrics. "
    "If a metric is not provided, do not invent it. "
    "Keep the response concise and suitable for a hospital operations dashboard."
)


def generate_rule_based_explanation(metrics):
    waiting_patients = metrics.get("waiting_patients", 0)
    average_wait = metrics.get("average_waiting_time", 0)
    beds_available = metrics.get("beds_available", 0)
    doctors_available = metrics.get("doctors_available", 0)
    nurses_available = metrics.get("nurses_available", 0)
    icu_available = metrics.get("icu_available", 0)
    blood_units = metrics.get("blood_units", 0)
    medicine_stock = metrics.get("medicine_stock", 0)
    highest_queue_department = metrics.get("highest_queue_department", "Emergency")

    lines = []
    if waiting_patients > 10:
        lines.append(f"Main bottleneck: {highest_queue_department} has the heaviest queue pressure.")
    else:
        lines.append("Main bottleneck: Queue pressure is moderate but manageable.")

    if beds_available < 3 or icu_available < 2:
        lines.append("Resource pressure: Bed and ICU capacity are constrained relative to current demand.")
    elif doctors_available < 3 or nurses_available < 4:
        lines.append("Resource pressure: Clinical staffing is limited and is affecting throughput.")
    else:
        lines.append("Resource pressure: Core staffing and bed capacity are stable for the current load.")

    if average_wait > 30:
        lines.append(f"Waiting-time issue: Average waiting time is elevated at {average_wait} minutes.")
    else:
        lines.append("Waiting-time issue: Average wait remains within a moderate operating range.")

    if blood_units < 10 or medicine_stock < 50:
        lines.append("Inventory issue: Blood or medication stock is below the desired operating buffer.")
    else:
        lines.append("Inventory issue: Inventory levels appear sufficient for the current patient load.")

    summary = "Operational observation: Reduce queue pressure in the highest-volume department and monitor bed and staff constraints closely."
    lines.append(summary)
    return "\n".join(lines)


def generate_hf_explanation(metrics):
    token = os.getenv("HF_TOKEN")
    model = os.getenv("HF_MODEL", "microsoft/Phi-3-mini-4k-instruct")

    if not token:
        raise ValueError("HF_TOKEN is not configured.")

    try:
        client = InferenceClient(model=model, token=token)
        payload = {
            "waiting_patients": metrics.get("waiting_patients", 0),
            "average_waiting_time": metrics.get("average_waiting_time", 0),
            "beds_available": metrics.get("beds_available", 0),
            "doctors_available": metrics.get("doctors_available", 0),
            "nurses_available": metrics.get("nurses_available", 0),
            "icu_available": metrics.get("icu_available", 0),
            "blood_units": metrics.get("blood_units", 0),
            "medicine_stock": metrics.get("medicine_stock", 0),
            "highest_queue_department": metrics.get("highest_queue_department", "Emergency"),
        }
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "Hospital operational metrics:\n"
            f"Waiting patients: {payload['waiting_patients']}\n"
            f"Average waiting time: {payload['average_waiting_time']} minutes\n"
            f"Available beds: {payload['beds_available']}\n"
            f"Available doctors: {payload['doctors_available']}\n"
            f"Available nurses: {payload['nurses_available']}\n"
            f"ICU availability: {payload['icu_available']}\n"
            f"Blood units: {payload['blood_units']}\n"
            f"Medicine stock: {payload['medicine_stock']}\n"
            f"Department with highest queue: {payload['highest_queue_department']}"
        )
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc


def explain_metrics(metrics):
    try:
        explanation = generate_hf_explanation(metrics)
        return {"success": True, "source": "huggingface", "explanation": explanation}
    except Exception:
        fallback = generate_rule_based_explanation(metrics)
        return {"success": True, "source": "fallback", "explanation": fallback}
