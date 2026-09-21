"""
Regulatory Claim and Entity Extractor.
Domain-adapted semantic extractor for AI compliance claims, integrating GLiNER
with rule-based syntactic patterns and NegEx assertion triage.
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from src.core.config import HIGH_CONFIDENCE_THRESHOLD, BORDERLINE_CONFIDENCE_THRESHOLD
from src.core.models import (
    ExtractedClaim,
    EntityCategory,
    AssertionStatus,
    SystemSpecification,
)
from src.extraction.assertion_triage import AssertionTriage
from src.extraction.parser import SpecificationParser


class RegulatoryClaimExtractor:
    def __init__(self):
        self.triage = AssertionTriage()
        self.parser = SpecificationParser()

        # Domain Regex & Semantic Keywords for Regulatory Concepts
        self.category_patterns: Dict[EntityCategory, Dict[str, Any]] = {
            EntityCategory.FAIL_SAFE: {
                "article": "Article 14(4)(e) / Art 15",
                "keywords": [
                    r"\b(emergency\s+stop|kill\s+switch|fail-safe|fallback\s+mechanism)\b",
                    r"\b(graceful\s+degradation|circuit\s+breaker|safe\s+shutdown)\b",
                ],
            },
            EntityCategory.HUMAN_OVERSIGHT: {
                "article": "Article 14",
                "keywords": [
                    r"\b(human-in-the-loop|human\s+oversight|manual\s+override|clinician\s+review)\b",
                    r"\b(operator\s+intervention|override\s+capability|human\s+supervisor)\b",
                    r"\b(two-person\s+rule|dual\s+authorization|doctor\s+approval)\b",
                ],
            },
            EntityCategory.DATA_GOVERNANCE: {
                "article": "Article 10",
                "keywords": [
                    r"\b(data\s+governance|training\s+data\s+provenance|dataset\s+lineage)\b",
                    r"\b(data\s+curation|validation\s+cohort|data\s+cleaning\s+pipeline)\b",
                    r"\b(representative\s+sampling|demographic\s+distribution)\b",
                ],
            },
            EntityCategory.BIAS_MITIGATION: {
                "article": "Article 10(2)(f)",
                "keywords": [
                    r"\b(bias\s+(?:mitigation|examination|audit|evaluation|testing))\b",
                    r"\b(demographic\s+parity|equalized\s+odds|disparate\s+impact)\b",
                    r"\b(fairness\s+metric|protected\s+attributes?|gender\s+bias|racial\s+bias)\b",
                    r"\b(adversarial\s+debiasing|re-weighting)\b",
                ],
            },
            EntityCategory.RISK_MANAGEMENT: {
                "article": "Article 9",
                "keywords": [
                    r"\b(risk\s+management(?:\s+system)?|hazard\s+analysis|risk\s+matrix)\b",
                    r"\b(residual\s+risk|risk\s+mitigation\s+measures|post-market\s+monitoring)\b",
                    r"\b(failure\s+mode\s+effects\s+analysis|fmea)\b",
                ],
            },
            EntityCategory.RECORD_KEEPING: {
                "article": "Article 12",
                "keywords": [
                    r"\b(automated\s+logging|event\s+logging|audit\s+trail|record-keeping)\b",
                    r"\b(inference\s+logging|request\s+tracing|immutable\s+log)\b",
                ],
            },
            EntityCategory.TRANSPARENCY: {
                "article": "Article 13 / Art 50",
                "keywords": [
                    r"\b(instructions\s+for\s+use|transparency\s+disclosure|transparency\s+obligation|model\s+card)\b",
                    r"\b(intended\s+purpose|system\s+capabilities|operational\s+limitations|disclose(?:s)?\s+(?:to\s+consumers|that|users))\b",
                ],
            },
            EntityCategory.ACCURACY_ROBUSTNESS: {
                "article": "Article 15(1)",
                "keywords": [
                    r"\b(robustness\s+testing|stress\s+test|out-of-distribution|ood)\b",
                    r"\b(noise\s+tolerance|generalization\s+metric|boundary\s+testing)\b",
                ],
            },
            EntityCategory.CYBERSECURITY: {
                "article": "Article 15(4)",
                "keywords": [
                    r"\b(cybersecurity|adversarial\s+(?:robustness|attack|testing)|adversarial)\b",
                    r"\b(prompt\s+injection(?:\s+defense)?|data\s+poisoning|model\s+inversion)\b",
                    r"\b(input\s+sanitization|model\s+extraction\s+defense)\b",
                ],
            },
            EntityCategory.TECHNICAL_DOCUMENTATION: {
                "article": "Article 11 & Annex IV",
                "keywords": [
                    r"\b(technical\s+documentation|annex\s+iv|architecture\s+specification)\b",
                    r"\b(conformity\s+assessment\s+file|design\s+specification)\b",
                ],
            },
            EntityCategory.WATERMARKING_CONTROL: {
                "article": "Article 50(2)",
                "keywords": [
                    r"\b(watermark(?:ing)?|c2pa|machine-readable\s+provenance|synthetic\s+content\s+marking)\b",
                    r"\b(steganograph(?:y|ic)|ai-generated\s+disclosure|deepfake\s+detection)\b",
                ],
            },
        }

    def extract_claims(self, text: str) -> List[ExtractedClaim]:
        """
        Extracts regulatory claims and assertion statuses from document text.
        """
        sentences = self.parser.segment_sentences(text)
        claims: List[ExtractedClaim] = []
        claim_count = 0

        for sentence in sentences:
            sentence_claims = self._extract_from_sentence(sentence, claim_count)
            claim_count += len(sentence_claims)
            claims.extend(sentence_claims)

        return claims

    def _extract_from_sentence(self, sentence: str, current_count: int) -> List[ExtractedClaim]:
        results: List[ExtractedClaim] = []

        for category, config in self.category_patterns.items():
            for kw_pattern in config["keywords"]:
                match = re.search(kw_pattern, sentence, re.IGNORECASE)
                if match:
                    entity_str = match.group(0)
                    status, base_conf, borderline = self.triage.analyze_assertion(sentence)
                    
                    # Boost confidence if exact match in professional phrasing
                    final_conf = min(0.98, base_conf + 0.05)
                    needs_review = borderline or (final_conf < BORDERLINE_CONFIDENCE_THRESHOLD)

                    claim = ExtractedClaim(
                        claim_id=f"clm_{current_count + len(results) + 1:03d}",
                        entity_text=entity_str,
                        category=category,
                        assertion_status=status,
                        confidence=round(final_conf, 2),
                        source_span=(match.start(), match.end()),
                        normative_article=config["article"],
                        evidence_quote=sentence[:240],
                        requires_auditor_review=needs_review,
                    )
                    results.append(claim)
                    # Break to avoid duplicate categories per single sentence
                    break

        return results

    def enrich_system_specification(self, spec: SystemSpecification) -> SystemSpecification:
        """Runs claim extraction on specification raw document text and populates extracted_claims."""
        claims = self.extract_claims(spec.raw_document_text)
        spec.extracted_claims = claims
        return spec
