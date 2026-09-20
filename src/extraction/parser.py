"""
Document and Model Card Ingestion Parser.
Handles Markdown, YAML, JSON, and plaintext AI system specifications.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

from src.core.models import SystemMetadata, SystemSpecification


class SpecificationParser:
    def __init__(self):
        self.section_headers = [
            "model details",
            "intended use",
            "risk management",
            "data governance",
            "training data",
            "evaluation data",
            "bias examination",
            "fairness",
            "human oversight",
            "robustness",
            "cybersecurity",
            "logging",
            "ethical considerations",
            "caveats and recommendations",
        ]

    def parse_file(self, file_path: Path) -> SystemSpecification:
        """Parses a specification file (.json, .yaml, .md, .txt)."""
        suffix = file_path.suffix.lower()
        content = file_path.read_text(encoding="utf-8")

        if suffix == ".json":
            return self.parse_json(content)
        elif suffix in [".yaml", ".yml"]:
            return self.parse_yaml(content)
        else:
            return self.parse_markdown(content, default_id=file_path.stem)

    def parse_json(self, raw_json: str) -> SystemSpecification:
        """Parses JSON-formatted model card or system spec."""
        data = json.loads(raw_json)
        
        meta_dict = data.get("metadata", {})
        metadata = SystemMetadata(
            system_id=meta_dict.get("system_id", "sys-unknown"),
            name=meta_dict.get("name", "Unnamed AI System"),
            version=meta_dict.get("version", "1.0.0"),
            domain=meta_dict.get("domain", "General Purpose"),
            intended_purpose=meta_dict.get("intended_purpose", "Not specified"),
            eu_risk_classification=meta_dict.get("eu_risk_classification", "High-Risk (Annex III)"),
            developer_name=meta_dict.get("developer_name", "Enterprise AI Team"),
            deployment_context=meta_dict.get("deployment_context", "Production"),
        )

        doc_text = data.get("raw_document_text") or json.dumps(data.get("sections", {}), indent=2)

        return SystemSpecification(
            metadata=metadata,
            raw_document_text=doc_text,
            custom_attributes=data.get("custom_attributes", {}),
        )

    def parse_yaml(self, raw_yaml: str) -> SystemSpecification:
        """Parses YAML-formatted model specification."""
        data = yaml.safe_load(raw_yaml) or {}
        return self.parse_json(json.dumps(data))

    def parse_markdown(self, raw_markdown: str, default_id: str = "sys-md-01") -> SystemSpecification:
        """Parses Markdown model card (e.g. Hugging Face model card format)."""
        name_match = re.search(r"^#\s+(.+)$", raw_markdown, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else default_id.replace("-", " ").title()

        domain = "High-Risk Healthcare / HR / Finance"
        if re.search(r"\b(medical|clinical|diagnostic|radiology|samd)\b", raw_markdown, re.I):
            domain = "Healthcare & Medical Diagnostics"
        elif re.search(r"\b(recruitment|employment|cv|resume|interview)\b", raw_markdown, re.I):
            domain = "Employment & HR Screening"
        elif re.search(r"\b(credit|loan|financial|underwriting)\b", raw_markdown, re.I):
            domain = "Financial Services & Credit Scoring"

        metadata = SystemMetadata(
            system_id=default_id,
            name=name,
            domain=domain,
            intended_purpose="Automated processing and evaluation in high-impact workflows.",
            eu_risk_classification="High-Risk (Annex III)",
        )

        return SystemSpecification(
            metadata=metadata,
            raw_document_text=raw_markdown,
            custom_attributes={},
        )

    def segment_sentences(self, text: str) -> List[str]:
        """Segments raw text into candidate claim sentences."""
        clean = re.sub(r"```[\s\S]*?```", "", text)  # remove code blocks
        clean = re.sub(r"^#+.*$", "", clean, flags=re.MULTILINE)  # remove headings
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
