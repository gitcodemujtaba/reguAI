"""
Tests for ReguAI Enterprise REST API.
"""

from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"


def test_api_list_samples():
    response = client.get("/api/v1/audit/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 3


def test_api_evaluate_endpoint():
    sample_res = client.get("/api/v1/audit/samples/compliant_clinical_samd")
    assert sample_res.status_code == 200
    sample_data = sample_res.json()

    eval_res = client.post(
        "/api/v1/audit/evaluate",
        json={"specification_text": sample_data["raw_document_text"], "auditor_id": "test_ci_pipeline"},
    )
    assert eval_res.status_code == 200
    result = eval_res.json()
    assert result["overall_conforms"] is True
    assert result["conformity_score"] == 100.0
    assert result["certificate_token"].startswith("REGU-")


def test_api_certificate_html():
    response = client.get("/api/v1/certificates/REGU-DEMO-TEST/html")
    assert response.status_code == 200
    assert "EU AI Act Conformity Attestation" in response.text


def test_api_triage_feedback():
    response = client.post(
        "/api/v1/triage/feedback",
        json={
            "claim_id": "clm_test_99",
            "auditor_id": "compliance_lead_01",
            "verified_status": "IMPLEMENTED",
            "verified_category": "HUMAN_OVERSIGHT",
            "notes": "Verified operational override in production dashboard.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RECORDED"
    assert "positive_label" in data["triplet"]
