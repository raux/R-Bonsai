from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.lsystem import MODES, generate_lsystem
from app.main import app


client = TestClient(app)


def test_generate_bonsai_first_iteration():
    rules = {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}
    result = generate_lsystem("X", rules, 1)
    assert result == "F+[[X]-X]-F[-FX]+X"


def test_api_generate_koch_iteration_one():
    koch_mode = MODES[1]
    payload = {
        "mode": 1,
        "iterations": 1,
        "axiom": koch_mode.axiom,
        "rules": koch_mode.rules,
        "angle": koch_mode.angle,
    }

    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()

    expected = "F-F++F-F++F-F++F-F++F-F++F-F"

    assert data["result"] == expected
    assert data["angle"] == 60.0
