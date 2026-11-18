import json
from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
CONFIG = json.loads(Path('config.json').read_text())


def test_metrics_fields():
    res = client.get('/metrics')
    assert res.status_code == 200
    m = res.json()
    for key in ['student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha']:
        assert key in m
    assert m['student_id'] == CONFIG['student_id']
    assert m['training_rows'] == len(pd.read_csv('dataset/train.csv'))
    assert 0.5 <= m['accuracy'] <= 1.0


def test_predict():
    record = {name: 0.1 for name in CONFIG['features']}
    res = client.post('/predict', json={'records': [record, record]})
    assert res.status_code == 200
    assert len(res.json()['predictions']) == 2
