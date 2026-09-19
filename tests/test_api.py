import json

from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_predict_wait_endpoint_requires_fields():
    client = app.test_client()
    response = client.post('/api/ml/predict-wait', json={})
    assert response.status_code == 400
    payload = response.get_json()
    assert payload['success'] is False
    assert 'Missing required field' in payload['error']


def test_ai_explain_falls_back_without_hf_token():
    client = app.test_client()
    response = client.post('/api/ai/explain', json={
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
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert payload['source'] in {'fallback', 'huggingface'}
