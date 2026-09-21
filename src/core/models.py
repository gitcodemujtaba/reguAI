"""
Pydantic schemas for ReguAI system models, claims, verification results, and audit ledger.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AssertionStatus(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    PLANNED = "PLANNED"
    ABSENT = "ABSENT"
    UNKNOWN = "UNKNOWN"


class RegulatoryFramework(str, Enum):
    EU_AI_ACT = "EU_AI_ACT"
    NIST_AI_RMF = "NIST_AI_RMF"
    ISO_42001 = "ISO_42001"


class EntityCategory(str, Enum):
    RISK_MANAGEMENT = "RISK_MANAGEMENT"                     # Art 9 / NIST GOVERN
    DATA_GOVERNANCE = "DATA_GOVERNANCE"                     # Art 10 / NIST MAP
    BIAS_MITIGATION = "BIAS_MITIGATION"                     # Art 10(2)(f) / NIST MEASURE
    TECHNICAL_DOCUMENTATION = "TECHNICAL_DOCUMENTATION"     # Art 11 & Annex IV
    RECORD_KEEPING = "RECORD_KEEPING"                       # Art 12 / Logging
    TRANSPARENCY = "TRANSPARENCY"                           # Art 13
    HUMAN_OVERSIGHT = "HUMAN_OVERSIGHT"                     # Art 14 / Human-in-the-loop
    ACCURACY_ROBUSTNESS = "ACCURACY_ROBUSTNESS"             # Art 15(1)
    CYBERSECURITY = "CYBERSECURITY"                         # Art 15(4)
    FAIL_SAFE = "FAIL_SAFE"                                 # Art 14(4)(e) / Art 15
    WATERMARKING_CONTROL = "WATERMARKING_CONTROL"           # Art 50(2) / Synthetic Content Marking


class ExtractedClaim(BaseModel):
    claim_id: str
    entity_text: str
    category: EntityCategory
    assertion_status: AssertionStatus
    confidence: float = Field(ge=0.0, le=1.0)
    source_span: Optional[tuple[int, int]] = None
    normative_article: str
    evidence_quote: str
    requires_auditor_review: bool = False
    auditor_verified: Optional[bool] = None
    auditor_notes: Optional[str] = None


class SystemMetadata(BaseModel):
    system_id: str
    name: str
    version: str = "1.0.0"
    domain: str
    intended_purpose: str
    eu_risk_classification: str = "High-Risk (Annex III)"
    developer_name: str = "Enterprise AI Labs"
    deployment_context: str = "Production"


class SystemSpecification(BaseModel):
    metadata: SystemMetadata
    raw_document_text: str
    extracted_claims: List[ExtractedClaim] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)


class ValidationViolation(BaseModel):
    focus_node: str
    result_path: str
    source_constraint_component: str
    message: str
    severity: str = "Violation"  # Violation, Warning, Info
    regulatory_article: str
    normative_reference: str
    remediation_guidance: str


class AuditProvenance(BaseModel):
    input_doc_sha256: str
    graph_triples_sha256: str
    ruleset_sha256: str
    certificate_sha256: str
    prov_o_rdf: str
    timestamp_utc: str
    digital_signature: str


class ConformityReport(BaseModel):
    report_id: str
    system_metadata: SystemMetadata
    overall_conforms: bool
    conformity_score: float = Field(ge=0.0, le=100.0)
    total_requirements_evaluated: int
    passed_requirements_count: int
    violations: List[ValidationViolation] = Field(default_factory=list)
    warnings: List[ValidationViolation] = Field(default_factory=list)
    claims_analyzed: List[ExtractedClaim] = Field(default_factory=list)
    borderline_claims: List[ExtractedClaim] = Field(default_factory=list)
    provenance: AuditProvenance
    generated_at_utc: str
    executive_summary: str
    fine_exposure: Optional[Dict[str, Any]] = None
    harmonized_frameworks: Optional[Dict[str, Any]] = None
