"""
Auditor-in-the-Loop Active Learning Queue and Triplet Generation.
Captures human auditor feedback on borderline claims and formats triplet loss
training pairs (anchor, positive, negative) for continuous model alignment.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.core.models import ExtractedClaim, AssertionStatus, EntityCategory
from src.core.config import DATA_DIR


class ActiveLearningTriageQueue:
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or (DATA_DIR / "active_learning_triplets.jsonl")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def filter_borderline_claims(self, claims: List[ExtractedClaim]) -> List[ExtractedClaim]:
        """Filters claims that need human auditor review."""
        return [c for c in claims if c.requires_auditor_review or c.confidence < 0.85]

    def record_auditor_decision(
        self,
        claim: ExtractedClaim,
        auditor_id: str,
        verified_status: AssertionStatus,
        verified_category: EntityCategory,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Records human compliance decision and generates triplet feedback sample.
        Anchor: evidence quote
        Positive: auditor-verified category
        Negative: rejected/original category (if changed) or alternative category
        """
        claim.auditor_verified = True
        claim.assertion_status = verified_status
        claim.requires_auditor_review = False
        claim.auditor_notes = notes

        # Formulate Triplet Instance
        original_cat = claim.category.value
        positive_label = verified_category.value
        negative_label = original_cat if original_cat != positive_label else "IRRELEVANT_TEXT"

        triplet_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "auditor_id": auditor_id,
            "claim_id": claim.claim_id,
            "anchor_text": claim.evidence_quote,
            "positive_label": positive_label,
            "negative_label": negative_label,
            "verified_assertion_status": verified_status.value,
            "auditor_notes": notes,
        }

        # Append to feedback file
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(triplet_record) + "\n")

        return triplet_record

    def get_audit_history(self) -> List[Dict[str, Any]]:
        """Reads recorded active learning triplet feedback history."""
        if not self.storage_path.exists():
            return []
        records = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
        return records
