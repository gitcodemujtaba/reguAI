"""
Unit and integration tests for ReguAI CLI, SARIF Exporter, CycloneDX 1.6 AI-BOM,
and Active Learning Triplet Metric Learner.
"""

import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient

from src.engine import ReguAIEngine
from src.core.config import SYNTHETIC_DIR
from src.triage.sarif_exporter import SarifExporter
from src.triage.bom_generator import AIBOMGenerator
from src.triage.train_triplets import TripletMetricLearner
from api import app


@pytest.fixture
def engine():
    return ReguAIEngine()


@pytest.fixture
def compliant_report(engine):
    path = SYNTHETIC_DIR / "compliant_clinical_samd.json"
    return engine.evaluate_system(path)


@pytest.fixture
def non_compliant_report(engine):
    path = SYNTHETIC_DIR / "non_compliant_hr_recruitment.json"
    return engine.evaluate_system(path)


def test_sarif_export_structure(compliant_report, non_compliant_report):
    # Compliant system SARIF
    sarif_pass = SarifExporter.generate_sarif(compliant_report)
    assert sarif_pass["version"] == "2.1.0"
    assert sarif_pass["$schema"] == SarifExporter.SCHEMA_URI
    assert len(sarif_pass["runs"]) == 1
    assert sarif_pass["runs"][0]["tool"]["driver"]["name"] == "ReguAI"
    assert len(sarif_pass["runs"][0]["results"]) == 0

    # Non-compliant system SARIF
    sarif_fail = SarifExporter.generate_sarif(non_compliant_report)
    assert len(sarif_fail["runs"][0]["results"]) > 0
    first_result = sarif_fail["runs"][0]["results"][0]
    assert first_result["level"] == "error"
    assert "ruleId" in first_result
    assert first_result["ruleId"].startswith("REGU-")
    assert "locations" in first_result


def test_cyclonedx_bom_structure(compliant_report, non_compliant_report):
    bom = AIBOMGenerator.generate_bom(compliant_report)
    assert bom["bomFormat"] == "CycloneDX"
    assert bom["specVersion"] == "1.6"
    assert "serialNumber" in bom
    assert bom["serialNumber"].startswith("urn:uuid:")
    assert bom["metadata"]["component"]["type"] == "machine-learning-model"
    assert bom["metadata"]["component"]["name"] == compliant_report.system_metadata.name
    assert "declarations" in bom
    assert len(bom["declarations"]["standards"]) >= 1
    assert bom["declarations"]["standards"][0]["name"] == "Regulation (EU) 2024/1689 (EU AI Act)"
    assert bom["declarations"]["standards"][0]["status"] == "passed"

    # Non-compliant BOM has vulnerabilities and failed standards
    bom_fail = AIBOMGenerator.generate_bom(non_compliant_report)
    assert bom_fail["declarations"]["standards"][0]["status"] == "failed"
    assert len(bom_fail["vulnerabilities"]) > 0


def test_triplet_metric_learner():
    learner = TripletMetricLearner()
    results = learner.train_prototypes(epochs=3)
    assert results["status"] in ("CONVERGED", "NO_DATA")
    if results["status"] == "CONVERGED":
        assert results["separation_accuracy"] >= 80.0
        # Test category prediction
        cat, conf = learner.predict_category("Clinician manual override and emergency kill switch.")
        assert cat in ("HUMAN_OVERSIGHT", "FAIL_SAFE", "UNKNOWN")


def test_api_bom_and_sarif_endpoints():
    client = TestClient(app)
    
    # 1. Evaluate to register token in cache
    eval_resp = client.post(
        "/api/v1/audit/evaluate",
        json={"specification_text": "Clinical diagnostic assistant with continuous risk management, bias mitigation, human-in-the-loop review and automated logging."}
    )
    assert eval_resp.status_code == 200
    token = eval_resp.json()["certificate_token"]

    # 2. Retrieve CycloneDX BOM
    bom_resp = client.get(f"/api/v1/certificates/{token}/bom")
    assert bom_resp.status_code == 200
    bom_data = bom_resp.json()
    assert bom_data["bomFormat"] == "CycloneDX"
    assert bom_data["specVersion"] == "1.6"

    # 3. Retrieve SARIF report
    sarif_resp = client.get(f"/api/v1/certificates/{token}/sarif")
    assert sarif_resp.status_code == 200
    sarif_data = sarif_resp.json()
    assert sarif_data["version"] == "2.1.0"
    assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "ReguAI"

    # 4. Direct audit to BOM endpoint
    direct_bom = client.post(
        "/api/v1/audit/bom",
        json={"specification_text": "Autonomous triage system with verified operational data governance and testing."}
    )
    assert direct_bom.status_code == 200
    assert direct_bom.json()["bomFormat"] == "CycloneDX"


def test_cli_audit_execution(tmp_path):
    from src.cli import main
    import sys

    sarif_file = tmp_path / "test.sarif"
    json_file = tmp_path / "test.json"
    bom_file = tmp_path / "test.bom.json"
    target = str(SYNTHETIC_DIR / "compliant_clinical_samd.json")

    test_args = [
        "reguai", "audit", target,
        "--format", "text",
        "--sarif-out", str(sarif_file),
        "--json-out", str(json_file),
        "--bom-out", str(bom_file),
        "--fail-on-violation"
    ]
    
    old_argv = sys.argv
    try:
        sys.argv = test_args
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    finally:
        sys.argv = old_argv

    assert sarif_file.exists()
    assert json_file.exists()
    assert bom_file.exists()
