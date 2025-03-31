import pytest
from flask import Flask
from app.controllers.api import api_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    # Registra el blueprint que contiene el endpoint a testear.
    app.register_blueprint(api_bp)
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == {"status": "UP"}
