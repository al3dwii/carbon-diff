# tests/test_api.py
from fastapi.testclient import TestClient
from carbon_diff.api.main import app
from carbon_diff.ledger.record import store

def test_api_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("CARBON_DB", str(tmp_path/"ledger.db"))
    store(["demo/repo","abc123","1",'{"kwh":1,"co2":0.4}'])
    client = TestClient(app)
    resp = client.get("/deltas/demo/repo?days=30")
    assert resp.status_code == 200
    assert resp.json()[0]["kwh"] == 1
