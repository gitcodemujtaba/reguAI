"""
Multi-Framework Regulatory Harmonization Crosswalk.
Projects EU AI Act (Regulation EU 2024/1689) conformity findings onto:
- NIST AI RMF 1.0 (GOVERN, MAP, MEASURE, MANAGE)
- ISO/IEC 42001:2023 (Clauses & Annex A Controls)
- GDPR (Regulation EU 2016/679)
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from src.core.config import BENCHMARKS_DIR
from src.core.models import ValidationViolation


class FrameworkControlStatus(BaseModel):
    control_id: str
    control_name: str
    target_framework: str
    status: str  # "SATISFIED", "NON_COMPLIANT", "NOT_EVALUATED"
    eu_ai_act_article: str
    relationship_type: str
    semantic_rationale: str
    audit_guidance: str


class FrameworkSummary(BaseModel):
    total_mapped_controls: int
    satisfied_controls_count: int
    non_compliant_controls_count: int
    conformity_percentage: float
    controls: List[FrameworkControlStatus] = Field(default_factory=list)


class MultiFrameworkCrosswalkResult(BaseModel):
    frameworks: Dict[str, FrameworkSummary] = Field(default_factory=dict)
    high_level_summary: str = ""


class MultiFrameworkCrosswalk:
    def __init__(self, mappings_path: Optional[Path] = None):
        self.mappings_file = mappings_path or (BENCHMARKS_DIR / "rules" / "cross_regulatory_frameworks.json")
        self.mappings: List[Dict[str, Any]] = []
        self._load_mappings()

    def _load_mappings(self) -> None:
        if self.mappings_file.exists():
            with open(self.mappings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.mappings = data.get("mappings", [])
        else:
            self.mappings = []

    def harmonize(
        self,
        violations: List[ValidationViolation],
        all_evaluated_articles: Optional[List[str]] = None,
    ) -> MultiFrameworkCrosswalkResult:
        """
        Projects EU AI Act conformity assessment results across target frameworks.
        """
        violation_articles = set(v.regulatory_article.strip() for v in violations)
        # Normalize: e.g. "Article 9(2)" -> "Article 9" prefix match
        def is_article_violated(article_name: str) -> bool:
            for v_art in violation_articles:
                if article_name.startswith(v_art) or v_art.startswith(article_name):
                    return True
            return False

        framework_controls: Dict[str, List[FrameworkControlStatus]] = {
            "NIST AI RMF 1.0": [],
            "ISO/IEC 42001:2023": [],
            "GDPR (EU 2016/679)": [],
        }

        for m in self.mappings:
            target_fw = m.get("target_framework", "Unknown")
            eu_art = m.get("eu_ai_act_article", "")
            has_violation = is_article_violated(eu_art)

            status = "NON_COMPLIANT" if has_violation else "SATISFIED"

            ctrl_status = FrameworkControlStatus(
                control_id=m.get("target_control_id", ""),
                control_name=m.get("target_control_name", ""),
                target_framework=target_fw,
                status=status,
                eu_ai_act_article=eu_art,
                relationship_type=m.get("relationship_type", "EXACT_EQUIVALENT"),
                semantic_rationale=m.get("semantic_rationale", ""),
                audit_guidance=m.get("audit_guidance", ""),
            )

            if target_fw in framework_controls:
                framework_controls[target_fw].append(ctrl_status)
            else:
                framework_controls.setdefault(target_fw, []).append(ctrl_status)

        framework_summaries: Dict[str, FrameworkSummary] = {}
        total_satisfied = 0
        total_controls = 0

        for fw_name, ctrls in framework_controls.items():
            tot = len(ctrls)
            sat = sum(1 for c in ctrls if c.status == "SATISFIED")
            non = sum(1 for c in ctrls if c.status == "NON_COMPLIANT")
            pct = round((sat / tot * 100.0), 1) if tot > 0 else 100.0

            total_satisfied += sat
            total_controls += tot

            framework_summaries[fw_name] = FrameworkSummary(
                total_mapped_controls=tot,
                satisfied_controls_count=sat,
                non_compliant_controls_count=non,
                conformity_percentage=pct,
                controls=ctrls,
            )

        overall_pct = round((total_satisfied / total_controls * 100.0), 1) if total_controls > 0 else 100.0
        summary_text = (
            f"Multi-framework crosswalk mapped across {len(framework_summaries)} international frameworks: "
            f"{total_satisfied}/{total_controls} controls satisfied ({overall_pct}% alignment). "
            f"NIST AI RMF: {framework_summaries.get('NIST AI RMF 1.0', FrameworkSummary(total_mapped_controls=0, satisfied_controls_count=0, non_compliant_controls_count=0, conformity_percentage=0.0)).conformity_percentage}%, "
            f"ISO 42001: {framework_summaries.get('ISO/IEC 42001:2023', FrameworkSummary(total_mapped_controls=0, satisfied_controls_count=0, non_compliant_controls_count=0, conformity_percentage=0.0)).conformity_percentage}%, "
            f"GDPR: {framework_summaries.get('GDPR (EU 2016/679)', FrameworkSummary(total_mapped_controls=0, satisfied_controls_count=0, non_compliant_controls_count=0, conformity_percentage=0.0)).conformity_percentage}%."
        )

        return MultiFrameworkCrosswalkResult(
            frameworks=framework_summaries,
            high_level_summary=summary_text,
        )
