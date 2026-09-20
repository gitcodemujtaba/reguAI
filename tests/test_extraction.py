"""
Tests for Regulatory Claim Extraction and Assertion Triage.
"""

import pytest
from src.extraction.gliner_extractor import RegulatoryClaimExtractor
from src.extraction.assertion_triage import AssertionTriage
from src.core.models import AssertionStatus, EntityCategory


def test_assertion_triage_implemented():
    triage = AssertionTriage()
    text = "A clinician-in-the-loop human oversight mechanism is verified and actively operational."
    status, conf, borderline = triage.analyze_assertion(text)
    assert status == AssertionStatus.IMPLEMENTED
    assert conf >= 0.80
    assert borderline is False


def test_assertion_triage_absent():
    triage = AssertionTriage()
    text = "The system was deployed without human oversight or manual override capabilities."
    status, conf, borderline = triage.analyze_assertion(text)
    assert status == AssertionStatus.ABSENT
    assert conf >= 0.75


def test_assertion_triage_planned():
    triage = AssertionTriage()
    text = "Disparate impact testing across demographic groups is planned for future release in Q4."
    status, conf, borderline = triage.analyze_assertion(text)
    assert status == AssertionStatus.PLANNED
    assert conf >= 0.70


def test_claim_extractor_multiple_entities():
    extractor = RegulatoryClaimExtractor()
    doc = """
    # MedAI Model Card
    Continuous risk management system is maintained according to ISO 14971.
    Training data provenance is documented across 50,000 clinical cases.
    Bias examination and mitigation controls are fully implemented.
    A clinician review human oversight mechanism is strictly operational.
    Cybersecurity defenses against adversarial attack perturbations are deployed.
    """
    claims = extractor.extract_claims(doc)
    categories = {c.category for c in claims}

    assert EntityCategory.RISK_MANAGEMENT in categories
    assert EntityCategory.DATA_GOVERNANCE in categories
    assert EntityCategory.BIAS_MITIGATION in categories
    assert EntityCategory.HUMAN_OVERSIGHT in categories
    assert EntityCategory.CYBERSECURITY in categories
