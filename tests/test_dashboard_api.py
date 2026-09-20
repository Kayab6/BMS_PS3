import json
from app import app


def test_index_page():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'MEDFLOW' in html
    assert 'Operations Platform' in html
    assert 'chart-resource-snapshot' in html
    assert 'chart-urgency-mix' in html


def test_all_member4_apis():
    client = app.test_client()

    # 1. GET /api/metrics
    res = client.get('/api/metrics')
    assert res.status_code == 200
    metrics = res.get_json()
    assert 'patients_served' in metrics
    assert 'patients_waiting' in metrics
    assert 'critical_patients' in metrics
    assert 'average_waiting_time' in metrics
    assert 'icu_utilization' in metrics
    assert 'overall_resource_utilization' in metrics

    # 2. GET /api/resources
    res = client.get('/api/resources')
    assert res.status_code == 200
    resources = res.get_json()
    assert 'beds' in resources or 'general_beds' in resources
    assert 'icu' in resources or 'icu_beds' in resources
    assert 'doctors' in resources
    assert 'nurses' in resources
    assert 'operating_rooms' in resources or 'or' in resources
    assert 'ambulances' in resources

    # 3. GET /api/queue
    res = client.get('/api/queue')
    assert res.status_code == 200
    queue = res.get_json()
    assert isinstance(queue, list)
    if queue:
        assert 'department' in queue[0]
        assert 'urgency' in queue[0]
        assert 'priority' in queue[0]

    # 4. GET /api/blood-bank
    res = client.get('/api/blood-bank')
    assert res.status_code == 200
    bb = res.get_json()
    for grp in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
        assert grp in bb

    # 5. GET /api/medicines
    res = client.get('/api/medicines')
    assert res.status_code == 200
    meds = res.get_json()
    assert isinstance(meds, list)
    assert len(meds) > 0
    assert 'medicine_name' in meds[0]
    assert 'status' in meds[0]

    # 6. GET /api/equipment
    res = client.get('/api/equipment')
    assert res.status_code == 200
    eq = res.get_json()
    assert isinstance(eq, list)
    assert len(eq) > 0
    assert 'equipment_name' in eq[0]
    assert 'available_quantity' in eq[0]

    # 7. GET /api/alerts
    res = client.get('/api/alerts')
    assert res.status_code == 200
    alerts = res.get_json()
    assert isinstance(alerts, list)
    assert len(alerts) > 0
    assert 'title' in alerts[0]

    # 8. POST /api/simulation/start & GET /api/simulation/status
    res = client.post('/api/simulation/start', json={'scenario_type': 'normal'})
    assert res.status_code == 200
    sim_start = res.get_json()
    assert sim_start['success'] is True

    res = client.get('/api/simulation/status')
    assert res.status_code == 200
    sim_status = res.get_json()
    assert sim_status['status'] == 'completed'

    # 9. POST /api/simulation/reset
    res = client.post('/api/simulation/reset')
    assert res.status_code == 200
    sim_reset = res.get_json()
    assert sim_reset['success'] is True

    # 10. GET /api/strategies/compare
    res = client.get('/api/strategies/compare')
    assert res.status_code == 200
    compare = res.get_json()
    assert 'FCFS' in compare
    assert 'URGENCY_ONLY' in compare
    assert 'MEDFLOW' in compare

    # 11. POST /api/ml/predict-wait
    res = client.post('/api/ml/predict-wait', json={
        'urgency': 4,
        'queue_length': 10,
        'icu_availability': 2,
        'bed_availability': 4,
        'doctor_availability': 3,
        'nurse_availability': 5,
        'treatment_duration': 30,
        'department': 'Emergency'
    })
    assert res.status_code == 200
    ml_res = res.get_json()
    assert ml_res['success'] is True
    assert 'predicted_waiting_time' in ml_res

    # 12. POST /api/ai/explain
    res = client.post('/api/ai/explain', json={
        'waiting_patients': 18,
        'average_waiting_time': 42,
        'beds_available': 3,
        'doctors_available': 2,
        'nurses_available': 4,
        'icu_available': 1,
        'blood_units': 8,
        'medicine_stock': 64,
        'highest_queue_department': 'Emergency'
    })
    assert res.status_code == 200
    ai_res = res.get_json()
    assert ai_res['success'] is True
    assert 'explanation' in ai_res
