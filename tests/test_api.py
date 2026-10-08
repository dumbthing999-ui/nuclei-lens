from io import BytesIO

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from nuclei_lens.api import app

client = TestClient(app, base_url="http://127.0.0.1:8000")


def test_health_and_security_headers():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["storage"] == "none"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"


def test_actual_analysis_response():
    buffer = BytesIO()
    Image.fromarray(np.zeros((64, 64), dtype=np.uint16)).save(buffer, format="TIFF")
    response = client.post("/api/analyze", content=buffer.getvalue(), headers={"Content-Type": "image/tiff"})
    assert response.status_code == 200
    assert response.json()["raw_count"] == 0
    assert response.json()["outline_pngs"]


def test_invalid_upload_and_type():
    assert client.post("/api/analyze", content=b"bad", headers={"Content-Type": "image/png"}).status_code == 422
    assert client.post("/api/analyze", content=b"bad", headers={"Content-Type": "text/html"}).status_code == 415


def test_cross_origin_and_rebinding_hosts_rejected():
    assert client.post("/api/analyze", content=b"bad", headers={"Content-Type":"image/png", "Origin":"https://attacker.example"}).status_code == 403
    assert client.get("/api/health", headers={"Host":"attacker.example"}).status_code == 400


def test_oversized_upload_rejected():
    assert client.post("/api/analyze", content=b"x"*(10*1024*1024+1), headers={"Content-Type":"image/png"}).status_code == 413
