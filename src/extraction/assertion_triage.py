"""
Assertion and Negation Triage for Regulatory Claims (NegEx-based heuristic engine).
Distinguishes between Implemented, Planned, Absent, and Ambiguous controls.
"""

import re
from typing import Tuple
from src.core.models import AssertionStatus


class AssertionTriage:
    def __init__(self):
        # Absent / Negated Patterns (Pre- and Post-modifiers)
        self.absent_patterns = [
            r"\b(no|not|neither|nor|never|without)\b",
            r"\b(absent|absence|missing)\b",
            r"\b(lacks?|lacking|failed\s+to|omits?|omitted)\b",
            r"\b(not\s+yet|not\s+currently|not\s+implemented|not\s+conducted)\b",
            r"\b(no\s+fallback|no\s+oversight|no\s+mechanism|no\s+testing)\b",
            r"\b(untested|unmitigated|unmonitored)\b",
            r"\b(absence\s+of|exempt\s+from)\b",
        ]

        # Planned / Roadmap Patterns
        self.planned_patterns = [
            r"\b(planned|planning|roadmap|scheduled|targeted|proposed)\b",
            r"\b(will\s+be|to\s+be\s+implemented|in\s+development|in\s+progress)\b",
            r"\b(future\s+(?:releases?|versions?|iterations?|work))\b",
            r"\b(under\s+(?:consideration|evaluation|review))\b",
            r"\b(might\s+be\s+considered|could\s+be\s+considered|considered\s+for)\b",
            r"\b(if\s+budget\s+permits|pending\s+approval)\b",
            r"\b(q[1-4]\s*202[0-9])\b",
        ]

        # Implemented / Verified Patterns
        self.implemented_patterns = [
            r"\b(implemented|operational|deployed|enforced|verified)\b",
            r"\b(active|validated|integrated|established|maintained)\b",
            r"\b(tested\s+(?:and|with|via)|passed|certified|logged)\b",
            r"\b(in\s+production|monitored\s+24/7|real-time)\b",
            r"\b(equipped\s+with|provides\s+a\s+(?:manual|human|stop))\b",
        ]

    def analyze_assertion(self, text: str) -> Tuple[AssertionStatus, float, bool]:
        """
        Analyzes the context sentence surrounding an extracted entity.
        Returns:
            - status (AssertionStatus): IMPLEMENTED, PLANNED, or ABSENT
            - confidence (float): 0.0 to 1.0
            - requires_auditor_review (bool): True if ambiguous or borderline
        """
        clean_text = text.lower().strip()

        absent_hits = sum(1 for p in self.absent_patterns if re.search(p, clean_text))
        planned_hits = sum(1 for p in self.planned_patterns if re.search(p, clean_text))
        implemented_hits = sum(1 for p in self.implemented_patterns if re.search(p, clean_text))

        # Explicit negation takes precedence over generic auxiliary verbs (e.g. "deployed without oversight")
        if absent_hits > 0:
            if planned_hits > 0:
                # Contradiction between absent and planned (e.g., "currently absent but planned")
                return AssertionStatus.PLANNED, 0.65, True
            conf = min(0.96, 0.78 + (0.08 * absent_hits))
            return AssertionStatus.ABSENT, conf, False

        if planned_hits > 0:
            conf = min(0.92, 0.75 + (0.08 * planned_hits))
            return AssertionStatus.PLANNED, conf, False

        if implemented_hits > 0:
            confidence = min(0.96, 0.80 + (0.08 * implemented_hits))
            return AssertionStatus.IMPLEMENTED, confidence, False

        # If no explicit cue found, default to IMPLEMENTED if affirmative sentence,
        # but mark as borderline for human confirmation
        return AssertionStatus.IMPLEMENTED, 0.58, True
