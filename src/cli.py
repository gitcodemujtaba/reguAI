"""
ReguAI CLI: Automated CI/CD Regulatory Conformity Gate & Audit Runner.
Evaluates model cards, system specifications, and documentation for EU AI Act,
NIST AI RMF, and ISO 42001 compliance, outputting SARIF, JSON, or Annex IV reports.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.engine import ReguAIEngine
from src.core.models import ConformityReport
from src.triage.sarif_exporter import SarifExporter


def render_terminal_summary(report: ConformityReport, target_path: str) -> str:
    """Renders an executive terminal compliance summary."""
    status_symbol = "[PASS]" if report.overall_conforms else "[FAIL]"
    lines = [
        "=" * 78,
        f"  REGUAI REGULATORY AUDIT REPORT: {report.system_metadata.name}",
        "=" * 78,
        f"Target Specification : {target_path}",
        f"System Identifier    : {report.system_metadata.system_id} (v{report.system_metadata.version})",
        f"Risk Classification  : {report.system_metadata.eu_risk_classification}",
        f"Conformity Status    : {status_symbol} ({report.conformity_score:.1f}%)",
        f"Requirements Passed  : {report.passed_requirements_count} / {report.total_requirements_evaluated}",
        f"Digital Audit Token  : {report.provenance.digital_signature}",
        "-" * 78,
    ]

    if report.violations:
        lines.append(f"CRITICAL LEGAL VIOLATIONS ({len(report.violations)}):")
        for idx, v in enumerate(report.violations, 1):
            lines.append(f"  {idx}. [{v.regulatory_article}] {v.message}")
            lines.append(f"     Remediation: {v.remediation_guidance}")
            lines.append(f"     Reference  : {v.normative_reference}")
        lines.append("-" * 78)

    if report.warnings:
        lines.append(f"ADVISORY WARNINGS ({len(report.warnings)}):")
        for idx, w in enumerate(report.warnings, 1):
            lines.append(f"  {idx}. [{w.regulatory_article}] {w.message}")
        lines.append("-" * 78)

    if report.fine_exposure and report.fine_exposure.get("total_potential_fine_eur", 0) > 0:
        fine = report.fine_exposure
        lines.append(f"EU AI ACT ARTICLE 99 MAXIMUM FINE LIABILITY:")
        lines.append(f"  Statutory Fine Exposure: €{fine['total_potential_fine_eur']:,.2f}")
        lines.append(f"  Severity Bracket       : {fine.get('severity_bracket', 'Standard')}")
        lines.append("-" * 78)

    return "\n".join(lines)


def audit_target(args: argparse.Namespace) -> int:
    """Executes conformity audit on single file or directory."""
    target = Path(args.target)
    if not target.exists():
        print(f"Error: Target path '{target}' does not exist.", file=sys.stderr)
        return 2

    files_to_audit: List[Path] = []
    if target.is_dir():
        for ext in ("*.json", "*.md", "*.yaml", "*.yml"):
            files_to_audit.extend(target.glob(ext))
    else:
        files_to_audit.append(target)

    if not files_to_audit:
        print(f"Error: No JSON, Markdown, or YAML specifications found in '{target}'.", file=sys.stderr)
        return 2

    engine = ReguAIEngine()
    overall_exit_code = 0
    all_reports: List[ConformityReport] = []

    for file_path in files_to_audit:
        report = engine.evaluate_system(
            input_data=file_path,
            auditor_id=args.auditor or "reguai_ci_cd",
            annual_turnover_eur=args.turnover,
            is_sme=args.sme,
        )
        all_reports.append(report)

        if not report.overall_conforms:
            overall_exit_code = 1

        # Format output
        if args.format == "text":
            print(render_terminal_summary(report, str(file_path)))
        elif args.format == "json":
            print(json.dumps(report.model_dump(), indent=2))
        elif args.format == "markdown":
            print(engine.report_generator.generate_markdown_report(report))
        elif args.format == "sarif":
            sarif_doc = SarifExporter.generate_sarif(report, target_file_path=str(file_path))
            print(json.dumps(sarif_doc, indent=2))

        # Output file artifacts if requested
        if args.sarif_out:
            SarifExporter.export_sarif_json(
                report,
                output_file_path=args.sarif_out,
                target_file_path=str(file_path),
            )
            if args.format == "text":
                print(f"  [+] SARIF report written to: {args.sarif_out}")

        if args.json_out:
            p = Path(args.json_out)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
            if args.format == "text":
                print(f"  [+] JSON report written to: {args.json_out}")

        if args.md_out:
            p = Path(args.md_out)
            p.parent.mkdir(parents=True, exist_ok=True)
            md_content = engine.report_generator.generate_markdown_report(report)
            p.write_text(md_content, encoding="utf-8")
            if args.format == "text":
                print(f"  [+] Annex IV Markdown written to: {args.md_out}")

        if args.bom_out:
            p = Path(args.bom_out)
            p.parent.mkdir(parents=True, exist_ok=True)
            bom_content = engine.report_generator.generate_cyclonedx_bom(report)
            p.write_text(json.dumps(bom_content, indent=2), encoding="utf-8")
            if args.format == "text":
                print(f"  [+] CycloneDX AI-BOM written to: {args.bom_out}")

    if args.fail_on_violation and overall_exit_code != 0:
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="reguai",
        description="ReguAI: Neuro-Symbolic AI GRC & Deterministic Conformity Assessment Engine",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Audit sub-command
    audit_parser = subparsers.add_parser("audit", help="Audit model card or system spec against EU AI Act")
    audit_parser.add_argument("target", help="Path to specification file or directory")
    audit_parser.add_argument("--format", choices=["text", "json", "markdown", "sarif"], default="text", help="Output format")
    audit_parser.add_argument("--fail-on-violation", action="store_true", help="Exit with code 1 if violations are detected")
    audit_parser.add_argument("--auditor", default="ci_cd_automated_gate", help="Auditor / pipeline identifier")
    audit_parser.add_argument("--turnover", type=float, default=0.0, help="Annual turnover in EUR for fine calculation")
    audit_parser.add_argument("--sme", action="store_true", help="Whether developer is SME under Art 99(6)")
    audit_parser.add_argument("--sarif-out", help="File path to write SARIF 2.1.0 output")
    audit_parser.add_argument("--json-out", help="File path to write JSON report output")
    audit_parser.add_argument("--md-out", help="File path to write Annex IV Markdown output")
    audit_parser.add_argument("--bom-out", help="File path to write CycloneDX AI-BOM output")

    # Benchmark sub-command
    benchmark_parser = subparsers.add_parser("benchmark", help="Run regulatory extraction and triage benchmark")

    # Version sub-command
    subparsers.add_parser("version", help="Print ReguAI version")

    args = parser.parse_args()

    if args.command == "audit":
        sys.exit(audit_target(args))
    elif args.command == "benchmark":
        from evaluate_benchmark import run_benchmark
        run_benchmark()
        sys.exit(0)
    elif args.command == "version":
        print("ReguAI Neuro-Symbolic GRC Engine v0.1.0")
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
