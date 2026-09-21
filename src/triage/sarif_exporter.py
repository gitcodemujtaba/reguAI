"""
OASIS SARIF 2.1.0 (Static Analysis Results Interchange Format) Exporter.
Exports ReguAI Conformity Reports to standard SARIF JSON for GitHub Code Scanning,
GitLab SAST, and CI/CD security/compliance dashboards.
"""

from typing import Dict, Any, List, Optional
import json
import re
from pathlib import Path

from src.core.models import ConformityReport, ValidationViolation


class SarifExporter:
    """Exports ConformityReport objects to OASIS SARIF v2.1.0 JSON format."""

    SCHEMA_URI = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
    SARIF_VERSION = "2.1.0"
    TOOL_NAME = "ReguAI"
    TOOL_VERSION = "0.1.0"
    INFORMATION_URI = "https://github.com/gitcodemujtaba/reguAI"

    @classmethod
    def _normalize_rule_id(cls, regulatory_article: str, component: str = "") -> str:
        """Converts regulatory article strings into canonical SARIF rule identifiers."""
        clean_art = re.sub(r"[^\w\s-]", "", regulatory_article).strip()
        clean_art = re.sub(r"\s+", "-", clean_art).upper()
        if not clean_art.startswith("REGU-"):
            clean_art = f"REGU-{clean_art}"
        return clean_art

    @classmethod
    def generate_sarif(
        cls,
        report: ConformityReport,
        target_file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates a valid SARIF 2.1.0 dictionary from a ConformityReport.
        """
        file_uri = target_file_path or f"{report.system_metadata.system_id}.json"
        
        rules_dict: Dict[str, Dict[str, Any]] = {}
        results: List[Dict[str, Any]] = []

        # Process hard violations (SARIF error level)
        for v in report.violations:
            rule_id = cls._normalize_rule_id(v.regulatory_article, v.source_constraint_component)
            if rule_id not in rules_dict:
                rules_dict[rule_id] = {
                    "id": rule_id,
                    "name": f"EU_AI_Act_{v.regulatory_article.replace(' ', '_')}",
                    "shortDescription": {
                        "text": f"Mandatory compliance check: {v.regulatory_article}"
                    },
                    "fullDescription": {
                        "text": v.message
                    },
                    "help": {
                        "text": f"Remediation: {v.remediation_guidance}\nNormative Reference: {v.normative_reference}",
                        "markdown": f"### Remediation Guidance\n{v.remediation_guidance}\n\n**Normative Reference:** `{v.normative_reference}`"
                    },
                    "defaultConfiguration": {
                        "level": "error"
                    },
                    "helpUri": "https://data.europa.eu/eli/reg/2024/1689/oj",
                    "properties": {
                        "tags": ["compliance", "eu-ai-act", "governance", "shacl"],
                        "precision": "very-high"
                    }
                }

            result_obj = {
                "ruleId": rule_id,
                "level": "error",
                "message": {
                    "text": f"[{v.regulatory_article}] {v.message}. Remediation: {v.remediation_guidance}"
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": file_uri,
                                "uriBaseId": "%SRCROOT%"
                            },
                            "region": {
                                "startLine": 1,
                                "startColumn": 1
                            }
                        }
                    }
                ],
                "properties": {
                    "focusNode": v.focus_node,
                    "resultPath": v.result_path,
                    "remediationGuidance": v.remediation_guidance,
                    "normativeReference": v.normative_reference
                }
            }
            results.append(result_obj)

        # Process warnings (SARIF warning level)
        for w in report.warnings:
            rule_id = cls._normalize_rule_id(w.regulatory_article, w.source_constraint_component)
            if rule_id not in rules_dict:
                rules_dict[rule_id] = {
                    "id": rule_id,
                    "name": f"Advisory_{w.regulatory_article.replace(' ', '_')}",
                    "shortDescription": {
                        "text": f"Regulatory Advisory: {w.regulatory_article}"
                    },
                    "fullDescription": {
                        "text": w.message
                    },
                    "defaultConfiguration": {
                        "level": "warning"
                    },
                    "helpUri": "https://data.europa.eu/eli/reg/2024/1689/oj",
                    "properties": {
                        "tags": ["advisory", "eu-ai-act", "governance"],
                        "precision": "high"
                    }
                }

            result_obj = {
                "ruleId": rule_id,
                "level": "warning",
                "message": {
                    "text": f"[{w.regulatory_article}] {w.message}"
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": file_uri,
                                "uriBaseId": "%SRCROOT%"
                            },
                            "region": {
                                "startLine": 1,
                                "startColumn": 1
                            }
                        }
                    }
                ],
                "properties": {
                    "focusNode": w.focus_node,
                    "resultPath": w.result_path,
                }
            }
            results.append(result_obj)

        sarif_doc = {
            "$schema": cls.SCHEMA_URI,
            "version": cls.SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": cls.TOOL_NAME,
                            "version": cls.TOOL_VERSION,
                            "informationUri": cls.INFORMATION_URI,
                            "rules": list(rules_dict.values()),
                        }
                    },
                    "invocations": [
                        {
                            "executionSuccessful": True,
                            "endTimeUtc": report.generated_at_utc,
                            "properties": {
                                "conformityScore": report.conformity_score,
                                "overallConforms": report.overall_conforms,
                                "digitalSignature": report.provenance.digital_signature,
                            }
                        }
                    ],
                    "results": results,
                }
            ]
        }
        return sarif_doc

    @classmethod
    def export_sarif_json(
        cls,
        report: ConformityReport,
        output_file_path: Optional[str] = None,
        target_file_path: Optional[str] = None,
        indent: int = 2,
    ) -> str:
        """Serializes SARIF document to JSON string and optionally writes to file."""
        sarif_data = cls.generate_sarif(report, target_file_path=target_file_path)
        json_str = json.dumps(sarif_data, indent=indent)
        if output_file_path:
            out_p = Path(output_file_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(json_str, encoding="utf-8")
        return json_str
