"""
CycloneDX 1.6 AI Bill of Materials (AIBOM) Generator.
Produces machine-readable AI Bill of Materials adhering to OWASP CycloneDX v1.6
specifications for EU AI Act Annex IV, NIST AI RMF, and enterprise GRC ingestion.
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone
import json

from src.core.models import ConformityReport, EntityCategory, AssertionStatus


class AIBOMGenerator:
    """Generates official CycloneDX 1.6 AI Bill of Materials (AIBOM) documents."""

    CYCLONEDX_VERSION = "1.6"
    SPEC_SCHEMA = f"http://cyclonedx.org/schema/bom-{CYCLONEDX_VERSION}.schema.json"

    @classmethod
    def generate_bom(cls, report: ConformityReport) -> Dict[str, Any]:
        """Translates a ConformityReport into a structured CycloneDX 1.6 AIBOM dictionary."""
        meta = report.system_metadata
        prov = report.provenance
        serial_uuid = f"urn:uuid:{uuid.uuid4()}"

        # Extract datasets and governance components from claims
        sub_components: List[Dict[str, Any]] = []
        for idx, claim in enumerate(report.claims_analyzed):
            comp_type = "data" if claim.category == EntityCategory.DATA_GOVERNANCE else "framework"
            sub_components.append({
                "type": comp_type,
                "bom-ref": f"component-{claim.claim_id}",
                "name": claim.category.value,
                "description": claim.entity_text,
                "properties": [
                    {"name": "reguai:assertionStatus", "value": claim.assertion_status.value},
                    {"name": "reguai:confidence", "value": str(round(claim.confidence, 3))},
                    {"name": "reguai:normativeArticle", "value": claim.normative_article},
                    {"name": "reguai:evidenceQuote", "value": claim.evidence_quote[:200]},
                ]
            })

        # Base CycloneDX 1.6 AI model component
        model_component: Dict[str, Any] = {
            "type": "machine-learning-model",
            "bom-ref": f"model-{meta.system_id}",
            "name": meta.name,
            "version": meta.version,
            "description": meta.intended_purpose,
            "supplier": {
                "name": meta.developer_name,
            },
            "modelCard": {
                "modelParameters": {
                    "task": meta.domain,
                    "architecture": meta.eu_risk_classification,
                },
                "quantitativeAnalysis": {
                    "performanceMetrics": [
                        {
                            "type": "ConformityScore",
                            "value": f"{report.conformity_score:.1f}%",
                            "description": "Deterministic EU AI Act SHACL Normative Conformity Index"
                        },
                        {
                            "type": "PassedRequirements",
                            "value": f"{report.passed_requirements_count}/{report.total_requirements_evaluated}",
                            "description": "Total satisfied legal shape constraints"
                        }
                    ]
                },
                "considerations": {
                    "users": [meta.deployment_context],
                    "useCases": [meta.intended_purpose],
                    "limitations": [
                        v.message for v in report.violations
                    ] if report.violations else ["None identified under verified constraints."]
                }
            },
            "properties": [
                {"name": "reguai:riskClassification", "value": meta.eu_risk_classification},
                {"name": "reguai:conformityStatus", "value": "CONFORMS" if report.overall_conforms else "NON_CONFORMANT"},
                {"name": "reguai:digitalSignature", "value": prov.digital_signature},
                {"name": "reguai:inputDocSha256", "value": prov.input_doc_sha256},
                {"name": "reguai:rulesetSha256", "value": prov.ruleset_sha256},
            ]
        }

        # Regulatory compliance declarations under CycloneDX 1.6 declarations
        declarations = {
            "standards": [
                {
                    "name": "Regulation (EU) 2024/1689 (EU AI Act)",
                    "version": "2024/1689",
                    "description": "European Union Artificial Intelligence Act",
                    "status": "passed" if report.overall_conforms else "failed",
                    "requirements": [
                        {
                            "identifier": v.regulatory_article,
                            "title": v.regulatory_article,
                            "conformance": {
                                "score": 0.0,
                                "rationale": v.message
                            }
                        } for v in report.violations
                    ]
                },
                {
                    "name": "NIST AI RMF 1.0",
                    "version": "1.0",
                    "description": "NIST Artificial Intelligence Risk Management Framework",
                    "status": "passed" if report.overall_conforms else "warning"
                },
                {
                    "name": "ISO/IEC 42001:2023",
                    "version": "2023",
                    "description": "Artificial Intelligence Management System",
                    "status": "passed" if report.overall_conforms else "warning"
                }
            ]
        }

        bom_doc: Dict[str, Any] = {
            "$schema": cls.SPEC_SCHEMA,
            "bomFormat": "CycloneDX",
            "specVersion": cls.CYCLONEDX_VERSION,
            "serialNumber": serial_uuid,
            "version": 1,
            "metadata": {
                "timestamp": report.generated_at_utc,
                "tools": [
                    {
                        "vendor": "ReguAI Governance",
                        "name": "ReguAI Neuro-Symbolic GRC Core",
                        "version": "0.1.0"
                    }
                ],
                "component": model_component,
            },
            "components": sub_components,
            "declarations": declarations,
            "vulnerabilities": [
                {
                    "id": f"EU-AI-ACT-{v.regulatory_article.replace(' ', '-')}",
                    "description": v.message,
                    "recommendation": v.remediation_guidance,
                    "analysis": {
                        "state": "exploitable" if v.severity == "Violation" else "in_triage",
                        "detail": v.normative_reference
                    }
                } for v in report.violations
            ]
        }

        return bom_doc
