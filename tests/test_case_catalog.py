"""
Tests for Domain-Driven Case Study Catalog and Cryptographic Provenance Anchors.
"""

import hashlib
import json
from pathlib import Path
import pytest

from src.core.config import PROJECT_ROOT, BENCHMARKS_DIR
from src.core.case_catalog import CaseStudyCatalog
from src.engine import ReguAIEngine


@pytest.fixture
def catalog():
    return CaseStudyCatalog()


@pytest.fixture
def engine():
    return ReguAIEngine()


def test_catalog_structure_and_domains(catalog):
    domains = catalog.list_domains()
    assert len(domains) == 11
    domain_ids = [d["domain_id"] for d in domains]
    assert "healthcare_samd" in domain_ids
    assert "employment_hr" in domain_ids
    assert "banking_finance" in domain_ids
    assert "transport_safety" in domain_ids
    assert "critical_infrastructure" in domain_ids
    assert "education_training" in domain_ids
    assert "justice_law_enforcement" in domain_ids
    assert "frontier_gpai" in domain_ids
    assert "prohibited_practices" in domain_ids
    assert "limited_risk_generative" in domain_ids
    assert "minimal_risk" in domain_ids


def test_cryptographic_provenance_integrity(catalog):
    """
    Cryptographic verification: Recomputes SHA-256 digests of all specification
    files and statutory text excerpts and asserts exact parity with catalog ledger.
    """
    for domain in catalog.list_domains():
        for case in domain["case_studies"]:
            file_path = PROJECT_ROOT / case["file_path"]
            assert file_path.exists(), f"File missing: {file_path}"

            # 1. Spec file SHA-256 verification
            computed_file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            assert case["file_sha256"] == computed_file_hash
            assert case["provenance"]["spec_file_sha256"] == computed_file_hash

            # 2. Statutory quote SHA-256 verification
            quote = case["statutory_quote"]
            computed_quote_hash = hashlib.sha256(quote.encode("utf-8")).hexdigest()
            assert case["provenance"]["statutory_quote_sha256"] == computed_quote_hash

            # 3. Provenance anchor metadata
            assert case["provenance"]["celex"] == "32024R1689"
            assert "eli_uri" in case["provenance"]
            assert case["provenance"]["prov_o_entity"].startswith("urn:reguai:benchmark:case:")


def test_render_factsheet_html(catalog):
    case = catalog.get_case("transport_autonomous_braking")
    assert case is not None
    html = catalog.render_factsheet_html("transport_autonomous_braking")
    assert "AutoDrive SafeStop" in html
    assert "CELEX:32024R1689" in html
    assert "Statutory Quote SHA-256" in html
    assert "Model Spec SHA-256" in html
    assert "W3C PROV-O Entity" in html


def test_transport_safety_conforms(engine, catalog):
    doc_text = catalog.get_case_document_text("transport_autonomous_braking")
    assert len(doc_text) > 0
    report = engine.evaluate_system(doc_text)
    assert report.overall_conforms is True
    assert report.conformity_score == 100.0


def test_education_surveillance_fails(engine, catalog):
    doc_text = catalog.get_case_document_text("education_remote_proctoring")
    assert len(doc_text) > 0
    report = engine.evaluate_system(doc_text)
    assert report.overall_conforms is False
    assert len(report.violations) > 0
    # Must fail Article 14 (oversight) and Article 10(2)(f) (bias)
    violated_articles = [v.regulatory_article for v in report.violations]
    assert any("14" in art for art in violated_articles)
    assert any("10" in art for art in violated_articles)


def test_prohibited_social_scoring_fails_with_tier_1_fine(engine, catalog):
    doc_text = catalog.get_case_document_text("prohibited_social_scoring")
    assert len(doc_text) > 0
    report = engine.evaluate_system(doc_text, annual_turnover_eur=100_000_000.0)
    assert report.overall_conforms is False
    assert report.conformity_score == 0.0
    assert report.fine_exposure is not None
    # fine_exposure is stored as a dict in ConformityReport
    if isinstance(report.fine_exposure, dict):
        assert report.fine_exposure["highest_tier_triggered"] == "TIER_1_PROHIBITED_AI"
        assert report.fine_exposure["applicable_ceiling_eur"] == 35_000_000.0
    else:
        assert report.fine_exposure.highest_tier_triggered == "TIER_1_PROHIBITED_AI"
        assert report.fine_exposure.applicable_ceiling_eur == 35_000_000.0
