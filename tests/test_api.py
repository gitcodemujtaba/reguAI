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
    assert "fine_exposure" in result
    assert "harmonized_frameworks" in result


def test_api_certificate_html():
    response = client.get("/api/v1/certificates/REGU-DEMO-TEST/html")
    assert response.status_code == 200
    assert "EU AI Act Conformity Attestation" in response.text
    assert "Article 99 Statutory Fine Liability Exposure" in response.text


def test_api_framework_crosswalk():
    response = client.get("/api/v1/frameworks/crosswalk")
    assert response.status_code == 200
    data = response.json()
    assert data["total_mappings"] >= 20
    assert any(m["target_framework"] == "NIST AI RMF 1.0" for m in data["mappings"])
    assert any(m["target_framework"] == "ISO/IEC 42001:2023" for m in data["mappings"])
    assert any("GDPR" in m["target_framework"] for m in data["mappings"])


def test_api_penalties_calculate():
    # Test Tier 1 Prohibited practice penalty
    response = client.post(
        "/api/v1/penalties/calculate",
        json={"violations": ["Article 5(1)(c)"], "annual_turnover_eur": 500_000_000, "is_sme": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["highest_tier_triggered"] == "TIER_1_PROHIBITED_AI"
    assert data["applicable_ceiling_eur"] == 35_000_000.0  # 7% of 500M is 35M

    # Test SME cap
    sme_res = client.post(
        "/api/v1/penalties/calculate",
        json={"violations": ["Article 14"], "annual_turnover_eur": 10_000_000, "is_sme": True},
    )
    assert sme_res.status_code == 200
    sme_data = sme_res.json()
    assert sme_data["is_sme_discount_applied"] is True
    assert sme_data["applicable_ceiling_eur"] == 300_000.0  # min(15M, 3% of 10M = 300k)


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


def test_api_benchmark_catalog():
    response = client.get("/api/v1/benchmarks/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "domains" in data
    assert len(data["domains"]) >= 10
    assert data["celex"] == "32024R1689"

    # Test domain filtering query
    filtered = client.get("/api/v1/benchmarks/catalog?domain=healthcare_samd")
    assert filtered.status_code == 200
    f_data = filtered.json()
    assert f_data["total_cases"] >= 1
    assert any("SaMD" in c["title"] for c in f_data["case_studies"])


def test_api_benchmark_case():
    response = client.get("/api/v1/benchmarks/cases/compliant_clinical_samd")
    assert response.status_code == 200
    data = response.json()
    assert "case_metadata" in data
    assert "raw_specification_text" in data
    assert data["case_metadata"]["provenance"]["celex"] == "32024R1689"
    assert "spec_file_sha256" in data["case_metadata"]["provenance"]
