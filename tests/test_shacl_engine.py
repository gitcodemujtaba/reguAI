"""
Tests for Deterministic SHACL Normative Reasoning Engine.
"""

import json
from pathlib import Path
import pytest
from src.core.config import SYNTHETIC_DIR
from src.extraction.parser import SpecificationParser
from src.extraction.gliner_extractor import RegulatoryClaimExtractor
from src.ontology.builder import NormativeGraphBuilder
from src.reasoning.shacl_engine import DeterministicSHACLEngine


@pytest.fixture
def components():
    return {
        "parser": SpecificationParser(),
        "extractor": RegulatoryClaimExtractor(),
        "builder": NormativeGraphBuilder(),
        "engine": DeterministicSHACLEngine(),
    }


def test_compliant_samd_conforms(components):
    samd_file = SYNTHETIC_DIR / "compliant_clinical_samd.json"
    spec = components["parser"].parse_file(samd_file)
    spec = components["extractor"].enrich_system_specification(spec)
    graph = components["builder"].build_system_graph(spec)

    conforms, violations, warnings, score = components["engine"].validate_system(graph)

    assert conforms is True
    assert len(violations) == 0
    assert score == 100.0


def test_non_compliant_hr_fails(components):
    hr_file = SYNTHETIC_DIR / "non_compliant_hr_recruitment.json"
    spec = components["parser"].parse_file(hr_file)
    spec = components["extractor"].enrich_system_specification(spec)
    graph = components["builder"].build_system_graph(spec)

    conforms, violations, warnings, score = components["engine"].validate_system(graph)

    assert conforms is False
    assert len(violations) >= 2

    violation_articles = [v.regulatory_article for v in violations]
    # Must flag Article 14 (Human Oversight missing) or Article 10(2)(f) (Bias mitigation missing)
    assert any("14" in art for art in violation_articles)
    assert any("10" in art for art in violation_articles)
    assert score < 80.0


def test_prohibited_emotion_recognition_fails(components):
    proh_file = SYNTHETIC_DIR / "prohibited_emotion_recognition_workplace.json"
    spec = components["parser"].parse_file(proh_file)
    spec = components["extractor"].enrich_system_specification(spec)
    graph = components["builder"].build_system_graph(spec)

    conforms, violations, warnings, score = components["engine"].validate_system(graph)

    assert conforms is False
    assert len(violations) >= 1
    violation_articles = [v.regulatory_article for v in violations]
    # Must flag Article 5 Prohibited Practice
    assert any("5" in art for art in violation_articles)


def test_gpai_foundation_llm_evaluates(components):
    gpai_file = SYNTHETIC_DIR / "gpai_foundation_llm.json"
    spec = components["parser"].parse_file(gpai_file)
    spec = components["extractor"].enrich_system_specification(spec)
    graph = components["builder"].build_system_graph(spec)

    conforms, violations, warnings, score = components["engine"].validate_system(graph)
    assert conforms is True
    assert len(violations) == 0
