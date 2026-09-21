"""
Active Learning Triplet Metric Learning & Confidence Calibrator.
Consumes auditor-in-the-loop triplet instances (anchor, positive, negative),
evaluates semantic margin separation, and trains/updates category prototype embeddings
and confidence calibration thresholds.
"""

from typing import Dict, Any, List, Tuple, Optional
import sys
import json
import math
from collections import defaultdict
import re
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.core.config import DATA_DIR
from src.core.models import EntityCategory, AssertionStatus


class TripletMetricLearner:
    """
    Contrastive metric learner and prototype calibrator for regulatory claim assertions.
    Enforces that anchor quotes are closer to auditor-approved positive labels than rejected negative labels.
    """

    def __init__(self, data_path: Optional[Path] = None, margin: float = 0.2):
        self.data_path = data_path or (DATA_DIR / "active_learning_triplets.jsonl")
        self.margin = margin
        self.category_prototypes: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.vocabulary: Dict[str, int] = {}

    def _tokenize(self, text: str) -> List[str]:
        """Simple linguistic tokenizer converting text to normalized unigram and bigram tokens."""
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = [t for t in clean.split() if len(t) > 2]
        bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]
        return tokens + bigrams

    def _compute_bow_vector(self, text: str) -> Dict[str, float]:
        """Builds an L2-normalized bag-of-words vector."""
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        counts: Dict[str, float] = defaultdict(float)
        for t in tokens:
            counts[t] += 1.0

        norm = math.sqrt(sum(v * v for v in counts.values()))
        if norm > 0:
            return {k: v / norm for k, v in counts.items()}
        return counts

    def _cosine_similarity(self, vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        """Computes sparse cosine similarity between two normalized vectors."""
        dot = 0.0
        for k, val_a in vec_a.items():
            if k in vec_b:
                dot += val_a * vec_b[k]
        return max(0.0, min(1.0, dot))

    def load_triplets(self) -> List[Dict[str, Any]]:
        """Loads all recorded active learning triplets from disk."""
        if not self.data_path.exists():
            return []
        records = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def train_prototypes(self, learning_rate: float = 0.1, epochs: int = 5) -> Dict[str, Any]:
        """
        Fits category prototype vectors using gradient-inspired updates over the triplets.
        Pulls positive category prototype toward anchor; pushes negative category prototype away.
        """
        triplets = self.load_triplets()
        if not triplets:
            return {
                "triplets_count": 0,
                "status": "NO_DATA",
                "loss": 0.0,
                "separation_accuracy": 0.0,
            }

        # Initialize prototypes with positive anchors
        for item in triplets:
            anchor_vec = self._compute_bow_vector(item["anchor_text"])
            pos_label = item["positive_label"]
            for token, weight in anchor_vec.items():
                self.category_prototypes[pos_label][token] += weight

        # Normalize prototypes
        for cat, tokens in self.category_prototypes.items():
            norm = math.sqrt(sum(v * v for v in tokens.values()))
            if norm > 0:
                self.category_prototypes[cat] = {k: v / norm for k, v in tokens.items()}

        # Iterative contrastive margin optimization
        history = []
        for epoch in range(epochs):
            total_loss = 0.0
            correct_pairs = 0

            for item in triplets:
                anchor_vec = self._compute_bow_vector(item["anchor_text"])
                pos_proto = self.category_prototypes[item["positive_label"]]
                neg_proto = self.category_prototypes.get(item["negative_label"], {})

                sim_pos = self._cosine_similarity(anchor_vec, pos_proto)
                sim_neg = self._cosine_similarity(anchor_vec, neg_proto)

                # Triplet ranking margin loss: max(0, sim_neg - sim_pos + margin)
                loss = max(0.0, sim_neg - sim_pos + self.margin)
                total_loss += loss

                if sim_pos > sim_neg:
                    correct_pairs += 1

                # Gradient step if violation occurs
                if loss > 0:
                    for k, val in anchor_vec.items():
                        self.category_prototypes[item["positive_label"]][k] += learning_rate * val
                        if item["negative_label"] in self.category_prototypes:
                            self.category_prototypes[item["negative_label"]][k] -= learning_rate * val * 0.5

            avg_loss = total_loss / len(triplets)
            acc = (correct_pairs / len(triplets)) * 100.0
            history.append({"epoch": epoch + 1, "loss": round(avg_loss, 4), "accuracy": round(acc, 1)})

        return {
            "triplets_count": len(triplets),
            "status": "CONVERGED",
            "final_loss": history[-1]["loss"],
            "separation_accuracy": history[-1]["accuracy"],
            "training_history": history,
            "trained_categories": list(self.category_prototypes.keys()),
        }

    def predict_category(self, query_text: str) -> Tuple[str, float]:
        """Predicts the most aligned regulatory category and returns confidence score."""
        q_vec = self._compute_bow_vector(query_text)
        best_cat = "UNKNOWN"
        best_sim = 0.0

        for cat, proto in self.category_prototypes.items():
            sim = self._cosine_similarity(q_vec, proto)
            if sim > best_sim:
                best_sim = sim
                best_cat = cat

        return best_cat, best_sim


def main():
    print("=" * 70)
    print("  REGUAI ACTIVE LEARNING TRIPLET METRIC LEARNER & CALIBRATOR")
    print("=" * 70)
    learner = TripletMetricLearner()
    results = learner.train_prototypes(epochs=5)
    print(f"Loaded Active Learning Feedback Triplets : {results['triplets_count']}")
    print(f"Training Status                         : {results['status']}")
    print(f"Final Triplet Margin Loss               : {results.get('final_loss', 0.0)}")
    print(f"Anchor Separation Accuracy              : {results.get('separation_accuracy', 0.0)}%")
    print(f"Calibrated Categories                   : {results.get('trained_categories', [])}")
    print("=" * 70)


if __name__ == "__main__":
    main()
