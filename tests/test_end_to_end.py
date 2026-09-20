"""
End-to-End Pipeline Integration Tests.
"""

from src.engine import ReguAIEngine
from src.core.config import SYNTHETIC_DIR


def test_full_pipeline_compliant():
    engine = ReguAIEngine()
    report = engine.evaluate_system(SYNTHETIC_DIR / "compliant_clinical_samd.json")

    assert report.overall_conforms is True
    assert report.conformity_score == 100.0
    assert len(report.violations) == 0
    assert len(report.claims_analyzed) >= 5
    assert report.provenance.digital_signature.startswith("REGU-")

    # Generate Markdown & JSON-LD
    md = engine.report_generator.generate_markdown_report(report)
    json_ld = engine.report_generator.generate_json_ld(report)

    assert "CONFORMS (PASS)" in md
    assert json_ld["regu:conformityStatus"] == "PASS"


def test_full_pipeline_non_compliant():
    engine = ReguAIEngine()
    report = engine.evaluate_system(SYNTHETIC_DIR / "non_compliant_hr_recruitment.json")

    assert report.overall_conforms is False
    assert len(report.violations) >= 2
    assert report.conformity_score < 80.0

    md = engine.report_generator.generate_markdown_report(report)
    json_ld = engine.report_generator.generate_json_ld(report)

    assert "NON-CONFORMANT (FAIL)" in md
    assert json_ld["regu:conformityStatus"] == "FAIL"
