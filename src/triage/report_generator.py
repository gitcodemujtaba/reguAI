"""
Conformity Assessment Report and Technical Documentation Package Generator.
Produces human-readable Annex IV audit reports (Markdown/HTML) and JSON-LD digital certificates.
"""

from datetime import datetime, timezone
import json
from typing import Dict, Any

from src.core.models import ConformityReport, ValidationViolation, ExtractedClaim


class ConformityReportGenerator:
    def generate_markdown_report(self, report: ConformityReport) -> str:
        """Generates an official EU AI Act Annex IV Technical Documentation report."""
        meta = report.system_metadata
        prov = report.provenance
        status_badge = "✅ CONFORMS (PASS)" if report.overall_conforms else "❌ NON-CONFORMANT (FAIL)"

        md = []
        md.append(f"# EU AI Act Conformity Assessment Report (Annex IV)")
        md.append(f"**Verification Engine:** ReguAI Neuro-Symbolic Governance Core v0.1.0  ")
        md.append(f"**Assessment Date (UTC):** {report.generated_at_utc}  ")
        md.append(f"**Certificate Token:** `{prov.digital_signature}`  ")
        md.append(f"**Status:** {status_badge}  ")
        md.append(f"**Conformity Index:** **{report.conformity_score:.1f}%** ({report.passed_requirements_count}/{report.total_requirements_evaluated} requirements satisfied)\n")
        md.append("---")

        # Executive Summary
        md.append("## 1. Executive Summary")
        md.append(report.executive_summary)
        md.append("")

        # Section 2: System Identification
        md.append("## 2. System Identification & Scope (Annex IV, Point 1)")
        md.append(f"- **System Name:** {meta.name}")
        md.append(f"- **System ID:** `{meta.system_id}`")
        md.append(f"- **Version:** {meta.version}")
        md.append(f"- **Developer:** {meta.developer_name}")
        md.append(f"- **Domain:** {meta.domain}")
        md.append(f"- **Intended Purpose:** {meta.intended_purpose}")
        md.append(f"- **EU AI Act Risk Classification:** **{meta.eu_risk_classification}**\n")

        # Section 3: Deterministic SHACL Verification Results
        md.append("## 3. Deterministic SHACL Normative Proofs (Chapter III)")
        if report.overall_conforms:
            md.append("All mandatory W3C SHACL shape constraints for Articles 9 through 15 were successfully satisfied with mathematical proof. No constraint violations found.\n")
        else:
            md.append(f"### Detected Legal Violations ({len(report.violations)})")
            md.append("| Legal Article | Normative Requirement | Severity | SHACL Path | Remediation Guidance |")
            md.append("|---|---|---|---|---|")
            for v in report.violations:
                md.append(f"| **{v.regulatory_article}** | {v.message} | `{v.severity}` | `{v.result_path}` | {v.remediation_guidance} |")
            md.append("")

        if report.warnings:
            md.append(f"### Advisory Warnings ({len(report.warnings)})")
            for w in report.warnings:
                md.append(f"- **{w.regulatory_article} ({w.source_constraint_component}):** {w.message}")
            md.append("")

        # Section 4: Regulatory Claim Inventory
        md.append("## 4. Extracted Regulatory Claims & Grounded Entities")
        md.append("| Claim ID | Entity Category | Assertion Status | Confidence | Legal Target | Evidence Span |")
        md.append("|---|---|---|---|---|---|")
        for c in report.claims_analyzed:
            status_emoji = "🟢" if c.assertion_status.value == "IMPLEMENTED" else ("🟡" if c.assertion_status.value == "PLANNED" else "🔴")
            md.append(f"| `{c.claim_id}` | `{c.category.value}` | {status_emoji} {c.assertion_status.value} | {c.confidence:.2f} | {c.normative_article} | *\"{c.evidence_quote[:75]}...\"* |")
        md.append("")

        # Section 5: Multi-Framework Regulatory Harmonization
        if report.harmonized_frameworks:
            md.append("## 5. Multi-Framework Regulatory Harmonization (NIST RMF / ISO 42001 / GDPR)")
            fw_data = report.harmonized_frameworks.get("frameworks", {})
            for fw_name, fw_summary in fw_data.items():
                pct = fw_summary.get("conformity_percentage", 100.0)
                sat = fw_summary.get("satisfied_controls_count", 0)
                tot = fw_summary.get("total_mapped_controls", 0)
                md.append(f"### {fw_name} (Alignment: {pct}% - {sat}/{tot} controls)")
                md.append("| Target Control | Control Name | Status | Linked AI Act Article | Audit Guidance |")
                md.append("|---|---|---|---|---|")
                for ctrl in fw_summary.get("controls", []):
                    c_badge = "🟢 SATISFIED" if ctrl.get("status") == "SATISFIED" else "🔴 NON-COMPLIANT"
                    md.append(f"| `{ctrl.get('control_id')}` | {ctrl.get('control_name')} | {c_badge} | **{ctrl.get('eu_ai_act_article')}** | {ctrl.get('audit_guidance')} |")
                md.append("")

        # Section 6: Statutory Fine Liability Analysis
        if report.fine_exposure:
            fine = report.fine_exposure
            md.append("## 6. Article 99 Statutory Fine & Financial Liability Audit")
            md.append(f"- **Highest Triggered Penalty Tier:** `{fine.get('highest_tier_triggered')}`")
            md.append(f"- **Legal Basis:** {fine.get('statutory_legal_basis')}")
            md.append(f"- **Maximum Statutory Ceiling:** **€{fine.get('applicable_ceiling_eur', 0):,.2f}**")
            md.append(f"- **Turnover Penalty Rate:** {fine.get('turnover_percentage', 0)}% of global annual turnover")
            md.append(f"- **SME Special Cap Applied:** {'Yes (Article 99(6))' if fine.get('is_sme_discount_applied') else 'No'}")
            md.append(f"- **Executive Liability Assessment:** {fine.get('executive_liability_summary')}\n")

        # Section 7: Cryptographic Provenance Ledger
        md.append("## 7. Cryptographic Provenance & Audit Ledger (W3C PROV-O)")
        md.append("Every artifact in this assessment is cryptographically anchored to prevent tampering and guarantee non-repudiation:")
        md.append(f"- **Source Specification SHA-256:** `{prov.input_doc_sha256}`")
        md.append(f"- **Normative RDF Knowledge Graph Canonical SHA-256:** `{prov.graph_triples_sha256}`")
        md.append(f"- **EU AI Act SHACL Ruleset SHA-256:** `{prov.ruleset_sha256}`")
        md.append(f"- **Conformity Certificate Digest:** `{prov.certificate_sha256}`")
        md.append(f"- **Immutable Token:** `{prov.digital_signature}`\n")

        md.append("### W3C PROV-O Turtle Graph")
        md.append("```turtle")
        md.append(prov.prov_o_rdf.strip())
        md.append("```\n")

        return "\n".join(md)

    def generate_json_ld(self, report: ConformityReport) -> Dict[str, Any]:
        """Generates machine-readable JSON-LD conformity certificate."""
        meta = report.system_metadata
        prov = report.provenance

        return {
            "@context": {
                "regu": "http://regu.ai/schema#",
                "eu": "http://data.europa.eu/eli/reg/2024/1689#",
                "prov": "http://www.w3.org/ns/prov#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "@id": f"http://regu.ai/certificates/{prov.digital_signature}",
            "@type": "regu:ConformityCertificate",
            "regu:systemId": meta.system_id,
            "regu:systemName": meta.name,
            "regu:conformityStatus": "PASS" if report.overall_conforms else "FAIL",
            "regu:conformityScore": report.conformity_score,
            "regu:timestampUtc": report.generated_at_utc,
            "regu:digitalSignature": prov.digital_signature,
            "regu:sourceDocHash": prov.input_doc_sha256,
            "regu:canonicalGraphHash": prov.graph_triples_sha256,
            "regu:violationsCount": len(report.violations),
            "regu:violations": [
                {
                    "article": v.regulatory_article,
                    "message": v.message,
                    "remediation": v.remediation_guidance,
                }
                for v in report.violations
            ],
        }

    def generate_html_certificate(self, report: ConformityReport) -> str:
        """Generates a formal, print-ready HTML Conformity Attestation Certificate."""
        meta = report.system_metadata
        prov = report.provenance
        is_pass = report.overall_conforms
        badge_bg = "#10b981" if is_pass else "#ef4444"
        badge_text = "CONFORMANT (APPROVED)" if is_pass else "NON-CONFORMANT (REJECTED)"

        violations_rows = ""
        if report.violations:
            for v in report.violations:
                violations_rows += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: 600; color: #b91c1c;">{v.regulatory_article}</td>
                    <td style="padding: 8px; border: 1px solid #e2e8f0; font-size: 13px;">{v.message}</td>
                    <td style="padding: 8px; border: 1px solid #e2e8f0; font-size: 13px; color: #475569;">{v.remediation_guidance}</td>
                </tr>
                """
        else:
            violations_rows = """
            <tr>
                <td colspan="3" style="padding: 12px; border: 1px solid #e2e8f0; text-align: center; color: #15803d; font-weight: 600;">
                    ✓ Zero non-conformities identified. All W3C SHACL Chapter III constraints satisfied.
                </td>
            </tr>
            """

        fine_box_html = ""
        if report.fine_exposure:
            fine = report.fine_exposure
            ceiling = fine.get("applicable_ceiling_eur", 0.0)
            f_tier = fine.get("highest_tier_triggered", "NONE")
            f_color = "#15803d" if ceiling == 0.0 else ("#b91c1c" if "PROHIBITED" in f_tier else "#c2410c")
            f_bg = "#f0fdf4" if ceiling == 0.0 else "#fff7ed"
            f_border = "#bbf7d0" if ceiling == 0.0 else "#fed7aa"

            fine_box_html = f"""
            <div style="background: {f_bg}; border: 1px solid {f_border}; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                <div style="font-size: 11px; font-weight: 700; color: {f_color}; text-transform: uppercase;">Article 99 Statutory Fine Liability Exposure</div>
                <div style="font-size: 18px; font-weight: 800; color: {f_color}; margin: 2px 0;">
                    €{ceiling:,.2f} <span style="font-size: 12px; font-weight: 500; color: #64748b;">({f_tier})</span>
                </div>
                <div style="font-size: 12px; color: #475569;">
                    {fine.get('executive_liability_summary', '')}
                </div>
            </div>
            """

        frameworks_html = ""
        if report.harmonized_frameworks:
            fw_data = report.harmonized_frameworks.get("frameworks", {})
            fw_badges = ""
            for fw_name, fw_info in fw_data.items():
                fw_pct = fw_info.get("conformity_percentage", 100.0)
                fw_sat = fw_info.get("satisfied_controls_count", 0)
                fw_tot = fw_info.get("total_mapped_controls", 0)
                b_color = "#15803d" if fw_pct == 100.0 else "#d97706"
                fw_badges += f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; flex: 1;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748b;">{fw_name}</div>
                    <div style="font-size: 16px; font-weight: 800; color: {b_color};">{fw_pct}%</div>
                    <div style="font-size: 11px; color: #94a3b8;">{fw_sat}/{fw_tot} controls compliant</div>
                </div>
                """
            frameworks_html = f"""
            <h3 style="font-size: 14px; text-transform: uppercase; margin: 20px 0 8px 0;">Multi-Framework Harmonization Crosswalk</h3>
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                {fw_badges}
            </div>
            """

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>EU AI Act Conformity Attestation - {meta.name}</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #1e293b;
            margin: 0;
            padding: 30px;
            background: #ffffff;
            line-height: 1.5;
        }}
        .certificate-container {{
            max-width: 860px;
            margin: 0 auto;
            border: 4px double #cbd5e1;
            padding: 40px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0f172a;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        .eu-stars {{
            font-size: 24px;
            color: #1d4ed8;
            letter-spacing: 2px;
        }}
        .title-block h1 {{
            margin: 0;
            font-size: 22px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #0f172a;
        }}
        .title-block p {{
            margin: 4px 0 0 0;
            font-size: 12px;
            color: #64748b;
        }}
        .status-seal {{
            background: {badge_bg};
            color: white;
            padding: 8px 18px;
            font-weight: 700;
            font-size: 14px;
            border-radius: 4px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
            background: #f8fafc;
            padding: 15px;
            border-radius: 6px;
            font-size: 13px;
        }}
        .info-item strong {{
            color: #475569;
            display: block;
            font-size: 11px;
            text-transform: uppercase;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0 25px 0;
        }}
        th {{
            background: #f1f5f9;
            padding: 8px;
            border: 1px solid #cbd5e1;
            font-size: 12px;
            text-transform: uppercase;
            text-align: left;
        }}
        .crypto-block {{
            background: #0f172a;
            color: #94a3b8;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 11px;
            margin-top: 20px;
        }}
        .crypto-block strong {{
            color: #38bdf8;
        }}
        .signature-block {{
            margin-top: 35px;
            display: flex;
            justify-content: space-between;
            padding-top: 20px;
            border-top: 1px dashed #cbd5e1;
            font-size: 12px;
        }}
        .sig-box {{
            width: 45%;
        }}
        .sig-line {{
            margin-top: 40px;
            border-bottom: 1px solid #475569;
        }}
        @media print {{
            body {{ padding: 0; background: white; }}
            .certificate-container {{ border: 2px solid #000; box-shadow: none; padding: 20px; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="certificate-container">
        <div class="header">
            <div class="title-block">
                <div class="eu-stars">🇪🇺 ★★★★★</div>
                <h1>EU AI Act Conformity Attestation</h1>
                <p>Formal Verification under Regulation (EU) 2024/1689 (Annex IV & Annex VII)</p>
            </div>
            <div class="status-seal">{badge_text}</div>
        </div>

        <div class="info-grid">
            <div class="info-item"><strong>AI System Name</strong> {meta.name} (v{meta.version})</div>
            <div class="info-item"><strong>Developer / Provider</strong> {meta.developer_name}</div>
            <div class="info-item"><strong>Risk Classification</strong> {meta.eu_risk_classification}</div>
            <div class="info-item"><strong>Application Domain</strong> {meta.domain}</div>
            <div class="info-item" style="grid-column: span 2;"><strong>Intended Purpose</strong> {meta.intended_purpose}</div>
            <div class="info-item"><strong>Verification Method</strong> Formal W3C SHACL Symbolic Constraint Solver</div>
            <div class="info-item"><strong>Conformity Score</strong> {report.conformity_score:.1f}% ({report.passed_requirements_count}/{report.total_requirements_evaluated} requirements passed)</div>
        </div>

        {fine_box_html}

        <h3 style="font-size: 14px; text-transform: uppercase; margin-bottom: 8px;">Deterministic Normative Evaluation Matrix</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 18%;">Legal Article</th>
                    <th>Normative SHACL Constraint</th>
                    <th style="width: 35%;">Remediation / Status</th>
                </tr>
            </thead>
            <tbody>
                {violations_rows}
            </tbody>
        </table>

        {frameworks_html}

        <div class="crypto-block">
            <strong>CRYPTOGRAPHIC PROVENANCE LEDGER (W3C PROV-O)</strong><br>
            Certificate Token: {prov.digital_signature}<br>
            Source Document Digest: {prov.input_doc_sha256}<br>
            Normative Graph Digest: {prov.graph_triples_sha256}<br>
            SHACL Ruleset Digest:   {prov.ruleset_sha256}<br>
            Assessment Timestamp:   {report.generated_at_utc}
        </div>

        <div class="signature-block">
            <div class="sig-box">
                <strong>Attesting Audit Agent:</strong> ReguAI Symbolic Governance Core v0.1.0<br>
                <div class="sig-line"></div>
                Automated Mathematical Attestation
            </div>
            <div class="sig-box">
                <strong>Lead Compliance Officer:</strong> Verified Human-in-the-Loop Sign-off<br>
                <div class="sig-line"></div>
                Authorized Signature & Date
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
