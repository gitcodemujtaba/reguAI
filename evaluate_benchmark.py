"""
ReguAI Benchmark Evaluation Runner.
Evaluates regulatory claim extraction, NegEx assertion triage, and normative mapping
against the ground-truth benchmark dataset.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from src.core.config import BENCHMARKS_DIR
from src.extraction.gliner_extractor import RegulatoryClaimExtractor
from src.core.models import AssertionStatus, EntityCategory


def run_benchmark():
    benchmark_file = BENCHMARKS_DIR / "conformity_ground_truth_benchmark.jsonl"
    if not benchmark_file.exists():
        print(f"Error: Benchmark file {benchmark_file} not found.")
        return

    extractor = RegulatoryClaimExtractor()

    total_samples = 0
    correct_category = 0
    correct_status = 0
    borderline_correct = 0

    results_table = []

    with open(benchmark_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line.strip())
            total_samples += 1

            sentence = item["sentence"]
            gold_cat = item["gold_category"]
            gold_status = item["gold_status"]
            gold_borderline = item.get("is_borderline", False)

            claims = extractor.extract_claims(sentence)
            pred_claim = claims[0] if claims else None

            pred_cat = pred_claim.category.value if pred_claim else "NOT_FOUND"
            pred_status = pred_claim.assertion_status.value if pred_claim else "NOT_FOUND"
            pred_borderline = pred_claim.requires_auditor_review if pred_claim else False

            cat_match = pred_cat == gold_cat
            status_match = pred_status == gold_status

            if cat_match:
                correct_category += 1
            if status_match:
                correct_status += 1
            if pred_borderline == gold_borderline:
                borderline_correct += 1

            results_table.append({
                "id": item["id"],
                "gold_cat": gold_cat,
                "pred_cat": pred_cat,
                "cat_match": cat_match,
                "gold_status": gold_status,
                "pred_status": pred_status,
                "status_match": status_match,
            })

    cat_acc = (correct_category / total_samples) * 100.0
    status_acc = (correct_status / total_samples) * 100.0

    print("================================================================================")
    print("               REGUAI REGULATORY EXTRACTION & TRIAGE BENCHMARK SCORECARD        ")
    print("================================================================================")
    print(f"Total Evaluated Benchmark Sentences : {total_samples}")
    print(f"Entity Category Extraction Accuracy  : {correct_category}/{total_samples} ({cat_acc:.1f}%)")
    print(f"NegEx Assertion Triage Accuracy      : {correct_status}/{total_samples} ({status_acc:.1f}%)")
    print("--------------------------------------------------------------------------------")
    print(f"{'Sample ID':<12} | {'Gold Category':<22} | {'Pred Category':<22} | {'Status Match':<12}")
    print("--------------------------------------------------------------------------------")
    for r in results_table[:10]:
        sm_badge = "✓ MATCH" if r["status_match"] and r["cat_match"] else "✗ MISMATCH"
        print(f"{r['id']:<12} | {r['gold_cat']:<22} | {r['pred_cat']:<22} | {sm_badge:<12}")
    if len(results_table) > 10:
        print(f"... and {len(results_table) - 10} more benchmark cases.")
    print("================================================================================")


if __name__ == "__main__":
    run_benchmark()
