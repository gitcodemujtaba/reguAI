"""
Article 99 Statutory Fine Liability & SME Exposure Calculator.
Calculates maximum corporate balance sheet exposure under Regulation (EU) 2024/1689:
- Tier 1 (Article 5 Prohibitions): Up to 35M€ or 7% global turnover
- Tier 2 (Chapter III High-Risk Obligations): Up to 15M€ or 3% global turnover
- Tier 3 (Misinformation / Notified Body Requests): Up to 7.5M€ or 1.5% global turnover
- Article 99(6) Special Cap: Fines on SMEs/startups use min(fixed, percentage)
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from src.core.config import BENCHMARKS_DIR
from src.core.models import ValidationViolation


class FineExposureEstimate(BaseModel):
    is_non_compliant: bool
    highest_tier_triggered: str
    statutory_legal_basis: str
    maximum_fine_eur: float
    turnover_percentage: float
    applicable_ceiling_eur: float
    is_sme_discount_applied: bool
    assumed_annual_turnover_eur: float
    affected_articles: List[str] = Field(default_factory=list)
    executive_liability_summary: str


class FineLiabilityCalculator:
    def __init__(self, guidelines_path: Optional[Path] = None):
        self.guidelines_file = guidelines_path or (BENCHMARKS_DIR / "rules" / "ai_act_fine_guidelines.json")
        self.guidelines: Dict[str, Any] = {}
        self._load_guidelines()

    def _load_guidelines(self) -> None:
        if self.guidelines_file.exists():
            with open(self.guidelines_file, "r", encoding="utf-8") as f:
                self.guidelines = json.load(f)
        else:
            # Standard statutory default fallbacks under Article 99
            self.guidelines = {
                "tiers": [
                    {"tier": "TIER_1_PROHIBITED_AI", "maximum_fine_eur": 35000000, "maximum_turnover_pct": 7.0, "legal_basis": "Article 99(3)"},
                    {"tier": "TIER_2_HIGH_RISK_OBLIGATIONS", "maximum_fine_eur": 15000000, "maximum_turnover_pct": 3.0, "legal_basis": "Article 99(4)"},
                    {"tier": "TIER_3_MISINFORMATION_NOTIFICATION", "maximum_fine_eur": 7500000, "maximum_turnover_pct": 1.5, "legal_basis": "Article 99(5)"},
                ]
            }

    def calculate_exposure(
        self,
        violations: List[ValidationViolation],
        annual_turnover_eur: float = 0.0,
        is_sme: bool = False,
    ) -> FineExposureEstimate:
        """
        Calculates maximum fine liability exposure according to Article 99 rules.
        """
        if not violations:
            return FineExposureEstimate(
                is_non_compliant=False,
                highest_tier_triggered="NONE",
                statutory_legal_basis="Article 99 (Full Compliance)",
                maximum_fine_eur=0.0,
                turnover_percentage=0.0,
                applicable_ceiling_eur=0.0,
                is_sme_discount_applied=is_sme,
                assumed_annual_turnover_eur=annual_turnover_eur,
                affected_articles=[],
                executive_liability_summary="Zero statutory fine liability. System satisfies audited regulatory constraints.",
            )

        affected_articles = sorted(set(v.regulatory_article for v in violations))
        has_prohibited = any("5" in art for art in affected_articles)
        has_high_risk = any(any(hr in art for hr in ["9", "10", "11", "12", "13", "14", "15", "16", "26", "27"]) for art in affected_articles)

        if has_prohibited:
            tier_name = "TIER_1_PROHIBITED_AI"
            fixed_max = 35_000_000.0
            pct_max = 7.0
            legal_basis = "Article 99(3) [Infringement of Prohibited AI Practices in Article 5]"
        elif has_high_risk:
            tier_name = "TIER_2_HIGH_RISK_OBLIGATIONS"
            fixed_max = 15_000_000.0
            pct_max = 3.0
            legal_basis = "Article 99(4) [Non-compliance with Chapter III High-Risk Requirements]"
        else:
            tier_name = "TIER_3_MISINFORMATION_NOTIFICATION"
            fixed_max = 7_500_000.0
            pct_max = 1.5
            legal_basis = "Article 99(5) [General Infringement]"

        turnover_based_fine = (annual_turnover_eur * (pct_max / 100.0)) if annual_turnover_eur > 0 else 0.0

        if is_sme:
            # Article 99(6): min(fixed_max, percentage_based_fine)
            if annual_turnover_eur > 0:
                applicable_ceiling = min(fixed_max, turnover_based_fine)
            else:
                applicable_ceiling = fixed_max
            summary = (
                f"SME Status Active (Article 99(6)): Maximum statutory fine capped at "
                f"€{applicable_ceiling:,.2f} under {legal_basis} (subject to the lower of €{fixed_max:,.0f} or {pct_max}% of turnover)."
            )
        else:
            # Standard enterprise: whichever is higher
            applicable_ceiling = max(fixed_max, turnover_based_fine)
            summary = (
                f"Enterprise Exposure: Maximum statutory fine of up to "
                f"€{applicable_ceiling:,.2f} under {legal_basis} (higher of €{fixed_max:,.0f} or {pct_max}% worldwide annual turnover)."
            )

        return FineExposureEstimate(
            is_non_compliant=True,
            highest_tier_triggered=tier_name,
            statutory_legal_basis=legal_basis,
            maximum_fine_eur=fixed_max,
            turnover_percentage=pct_max,
            applicable_ceiling_eur=applicable_ceiling,
            is_sme_discount_applied=is_sme,
            assumed_annual_turnover_eur=annual_turnover_eur,
            affected_articles=affected_articles,
            executive_liability_summary=summary,
        )
