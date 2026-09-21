"""
ReguAI: Deterministic Neuro-Symbolic AI GRC & Automated Conformity Assessment Engine.
Full-stack interactive Hugging Face Space application with Vis.js Regulatory Graph Explorer
and Official Annex IV Print-Ready Attestation Certificate.
"""

import os
import sys
from pathlib import Path
import json

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gradio as gr
from src.engine import ReguAIEngine
from src.core.config import SYNTHETIC_DIR
from src.core.models import AssertionStatus, EntityCategory
from src.ui.graph_view import RegulatoryGraphView

from src.core.case_catalog import CaseStudyCatalog
from src.triage.sarif_exporter import SarifExporter

# Initialize ReguAI Engine & Graph Visualizer & Case Study Catalog
engine = ReguAIEngine()
graph_viewer = RegulatoryGraphView()
catalog = CaseStudyCatalog()

# Pre-load domains and cases
DOMAIN_OPTIONS = [d["domain_name"] for d in catalog.list_domains()]
DEFAULT_DOMAIN = DOMAIN_OPTIONS[0]
DEFAULT_CASES = catalog.get_cases_for_domain(DEFAULT_DOMAIN)
DEFAULT_CASE_TITLES = [c["title"] for c in DEFAULT_CASES]
DEFAULT_CASE_TITLE = DEFAULT_CASE_TITLES[0]
DEFAULT_SPEC_TEXT = catalog.get_case_document_text(DEFAULT_CASE_TITLE)
DEFAULT_FACTSHEET = catalog.render_factsheet_html(DEFAULT_CASE_TITLE)
DEFAULT_QUICK_BAR = catalog.render_quick_bar(DEFAULT_CASE_TITLE)


READY_BANNER_HTML = """
<div style="margin-top: 12px; padding: 12px 16px; border-radius: 8px; background: #f8fafc; border: 1px dashed #cbd5e1; font-size: 13px; color: #64748b; display: flex; align-items: center; gap: 8px;">
    <span>ℹ️</span>
    <span>Ready to evaluate. Click <strong>⚡ Run Assessment & Review Grounding (Step 2)</strong> to execute SHACL verification and advance in sequence to Step 2: Review Grounding.</span>
</div>
"""


def on_domain_change(selected_domain_name: str):
    cases = catalog.get_cases_for_domain(selected_domain_name)
    banner = """
    <div style="margin-top: 12px; padding: 12px 16px; border-radius: 8px; background: #f8fafc; border: 1px dashed #cbd5e1; font-size: 13px; color: #64748b; display: flex; align-items: center; gap: 8px;">
        <span>ℹ️</span>
        <span>New regulatory sector selected. Click <strong>⚡ Run Deterministic Conformity Assessment</strong> below to evaluate.</span>
    </div>
    """
    if not cases:
        return gr.update(choices=[], value=None), "", "", "<div style='padding:15px;'>No cases found.</div>", banner
    titles = [c["title"] for c in cases]
    first_title = titles[0]
    text = catalog.get_case_document_text(first_title)
    factsheet = catalog.render_factsheet_html(first_title)
    quick_bar = catalog.render_quick_bar(first_title)
    return gr.update(choices=titles, value=first_title), text, quick_bar, factsheet, banner


def on_case_change(selected_case_title: str):
    banner = """
    <div style="margin-top: 12px; padding: 12px 16px; border-radius: 8px; background: #f8fafc; border: 1px dashed #cbd5e1; font-size: 13px; color: #64748b; display: flex; align-items: center; gap: 8px;">
        <span>ℹ️</span>
        <span>Case study loaded. Click <strong>⚡ Run Deterministic Conformity Assessment</strong> below to execute deterministic SHACL verification.</span>
    </div>
    """
    if not selected_case_title:
        return "", "", "<div style='padding:15px;'>Select a case study.</div>", banner
    text = catalog.get_case_document_text(selected_case_title)
    factsheet = catalog.render_factsheet_html(selected_case_title)
    quick_bar = catalog.render_quick_bar(selected_case_title)
    return text, quick_bar, factsheet, banner


def compute_assessment_data(doc_text: str, auditor_id: str, annual_turnover: float = 50000000.0, is_sme: bool = False):
    report = engine.evaluate_system(
        doc_text,
        auditor_id=auditor_id or "auditor_01",
        annual_turnover_eur=float(annual_turnover or 0.0),
        is_sme=bool(is_sme),
    )
    
    # 1. Executive Summary HTML
    status_color = "#10b981" if report.overall_conforms else "#ef4444"
    status_text = "CONFORMS (PASSED)" if report.overall_conforms else "NON-CONFORMANT (FAILED)"
    
    exec_html = f"""
    <div class="summary-card" style="border-left: 6px solid {status_color};">
        <div class="summary-header">
            <h2 class="summary-title">System: {report.system_metadata.name} (v{report.system_metadata.version})</h2>
            <span class="status-pill" style="background: {status_color};">
                {status_text}
            </span>
        </div>
        <p class="summary-meta"><strong>Domain:</strong> {report.system_metadata.domain} &nbsp;|&nbsp; <strong>Risk Class:</strong> {report.system_metadata.eu_risk_classification}</p>
        <p class="summary-desc">{report.executive_summary}</p>
        <div class="metrics-grid">
            <div class="metric-box">
                <div class="metric-label">Conformity Index</div>
                <div class="metric-val" style="color: {status_color};">{report.conformity_score:.1f}%</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Requirements Evaluated</div>
                <div class="metric-val metric-val-main">{report.passed_requirements_count} / {report.total_requirements_evaluated} Passed</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Deterministic Violations</div>
                <div class="metric-val" style="color: {'#ef4444' if report.violations else '#10b981'};">{len(report.violations)}</div>
            </div>
        </div>
    </div>
    """

    # 2. SHACL Violations Data Table
    violations_data = []
    for v in report.violations:
        violations_data.append([
            v.regulatory_article,
            v.message,
            v.severity,
            v.result_path,
            v.remediation_guidance,
        ])

    # 3. Extracted Claims Table
    claims_data = []
    for c in report.claims_analyzed:
        status_tag = f"🟢 {c.assertion_status.value}" if c.assertion_status.value == "IMPLEMENTED" else (
            f"🟡 {c.assertion_status.value}" if c.assertion_status.value == "PLANNED" else f"🔴 {c.assertion_status.value}"
        )
        claims_data.append([
            c.claim_id,
            c.category.value,
            status_tag,
            f"{c.confidence:.2f}",
            c.normative_article,
            c.evidence_quote[:90] + "...",
        ])

    # 4. Interactive Graph View (Vis.js iframe wrapper)
    raw_graph_html = graph_viewer.generate_html_graph(report)
    escaped_graph = raw_graph_html.replace('"', '&quot;').replace("'", "&#39;")
    graph_iframe_html = f"""
    <iframe srcdoc="{escaped_graph}" style="width: 100%; height: 560px; border: 1px solid #e2e8f0; border-radius: 8px;" frameborder="0"></iframe>
    """

    # 5. Borderline Review Queue Table
    borderline_data = []
    for b in report.borderline_claims:
        borderline_data.append([
            b.claim_id,
            b.category.value,
            b.assertion_status.value,
            f"{b.confidence:.2f}",
            b.evidence_quote[:100],
        ])

    # 6. Multi-Framework Harmonization Data Table
    frameworks_data = []
    if report.harmonized_frameworks:
        fw_dict = report.harmonized_frameworks.get("frameworks", {})
        for fw_name, fw_info in fw_dict.items():
            for ctrl in fw_info.get("controls", []):
                stat_badge = "🟢 SATISFIED" if ctrl.get("status") == "SATISFIED" else "🔴 NON-COMPLIANT"
                frameworks_data.append([
                    fw_name,
                    ctrl.get("control_id"),
                    ctrl.get("control_name"),
                    stat_badge,
                    ctrl.get("eu_ai_act_article"),
                    ctrl.get("audit_guidance"),
                ])

    # 7. Article 99 Fine Liability Scorecard HTML
    fine = report.fine_exposure or {}
    ceiling = fine.get("applicable_ceiling_eur", 0.0)
    tier_name = fine.get("highest_tier_triggered", "NONE")
    color = "#10b981" if ceiling == 0.0 else ("#ef4444" if "PROHIBITED" in tier_name else "#f59e0b")
    bg = "#f0fdf4" if ceiling == 0.0 else "#fff7ed"
    border = "#bbf7d0" if ceiling == 0.0 else "#fed7aa"

    fine_html = f"""
    <div class="fine-liability-card" style="background: {bg}; border: 1px solid {border}; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
        <div style="font-size: 13px; font-weight: 700; color: {color}; text-transform: uppercase; letter-spacing: 0.5px;">Regulation (EU) 2024/1689 Article 99 Corporate Fine Exposure</div>
        <div style="font-size: 32px; font-weight: 800; color: {color}; margin: 8px 0;">
            €{ceiling:,.2f}
        </div>
        <div style="display: flex; gap: 25px; font-size: 13px; color: #475569; margin-bottom: 14px; flex-wrap: wrap;">
            <div><strong>Penalty Tier:</strong> <code>{tier_name}</code></div>
            <div><strong>Turnover Percentage:</strong> {fine.get('turnover_percentage', 0)}% of global annual turnover</div>
            <div><strong>SME Discount (Art. 99(6)):</strong> {'✓ Active' if fine.get('is_sme_discount_applied') else '✗ Inactive (Standard Enterprise)'}</div>
            <div><strong>Simulated Turnover:</strong> €{float(annual_turnover):,.2f}</div>
        </div>
        <div class="fine-basis" style="font-size: 13px; color: #1e293b; line-height: 1.6; background: rgba(255,255,255,0.85); padding: 12px 16px; border-radius: 6px; border: 1px solid #e2e8f0;">
            <strong>Statutory Basis & Remediations:</strong> {fine.get('executive_liability_summary', '')}
        </div>
    </div>
    """

    # 8. Cryptographic Ledger Proofs
    prov = report.provenance
    cert_token = prov.digital_signature
    hash_summary = (
        f"**Conformity Certificate Token:** `{cert_token}`\n\n"
        f"| Ledger Artifact | Cryptographic Hash (SHA-256) |\n"
        f"|---|---|\n"
        f"| Source Document Snapshot | `{prov.input_doc_sha256}` |\n"
        f"| Normative RDF Knowledge Graph | `{prov.graph_triples_sha256}` |\n"
        f"| EU AI Act Normative Ruleset | `{prov.ruleset_sha256}` |\n"
        f"| Conformity Assessment Digest | `{prov.certificate_sha256}` |\n"
    )

    # 9. Annex IV Markdown, JSON-LD & Styled HTML Certificate
    md_report = engine.report_generator.generate_markdown_report(report)
    json_ld_cert = json.dumps(engine.report_generator.generate_json_ld(report), indent=2)
    raw_cert_html = engine.report_generator.generate_html_certificate(report)
    escaped_cert = raw_cert_html.replace('"', '&quot;').replace("'", "&#39;")
    cert_iframe_html = f"""
    <iframe srcdoc="{escaped_cert}" style="width: 100%; height: 680px; border: 1px solid #e2e8f0; border-radius: 8px;" frameborder="0"></iframe>
    """
    bom_json = json.dumps(engine.report_generator.generate_cyclonedx_bom(report), indent=2)
    sarif_json = SarifExporter.export_sarif_json(report, indent=2)

    return {
        "report": report,
        "overall_conforms": report.overall_conforms,
        "score": report.conformity_score,
        "system_name": report.system_metadata.name,
        "violations_count": len(report.violations),
        "passed_count": report.passed_requirements_count,
        "total_count": report.total_requirements_evaluated,
        "exec_html": exec_html,
        "violations_data": violations_data,
        "claims_data": claims_data,
        "graph_iframe_html": graph_iframe_html,
        "cert_token": cert_token,
        "hash_summary": hash_summary,
        "json_ld_cert": json_ld_cert,
        "md_report": md_report,
        "cert_iframe_html": cert_iframe_html,
        "borderline_data": borderline_data,
        "frameworks_data": frameworks_data,
        "fine_html": fine_html,
        "bom_json": bom_json,
        "sarif_json": sarif_json,
    }


def run_assessment(doc_text: str, auditor_id: str, annual_turnover: float = 50000000.0, is_sme: bool = False, target_tab: str = "tab_review_grounding"):
    if not doc_text or not doc_text.strip():
        gr.Warning("Please select or enter a system technical specification.")
        empty_banner = """
        <div style="margin-top: 14px; padding: 14px 18px; border-radius: 8px; background: #fef2f2; border: 1.5px solid #fca5a5; color: #991b1b;">
            ⚠️ Please enter or select a system technical specification before running assessment.
        </div>
        """
        return (
            gr.update(),
            empty_banner,
            "⚠️ Please enter model card text or select a pre-loaded sample.",
            [],
            [],
            "<div style='padding:20px;text-align:center;'>No graph generated.</div>",
            "N/A",
            "N/A",
            "{}",
            "",
            "<div>No certificate generated.</div>",
            [],
            [],
            "<div style='padding:15px;'>No fine liability evaluated.</div>",
            "{}",
            "{}",
        )

    data = compute_assessment_data(doc_text, auditor_id, annual_turnover, is_sme)

    dest_step_name = "Step 2: Review Grounding" if target_tab == "tab_review_grounding" else "Step 3: Run SHACL Proofs"
    status_tag = "PASSED (100%)" if data["overall_conforms"] else f"FAILED ({data['violations_count']} VIOLATIONS)"
    gr.Info(f"Conformity Assessment: {data['system_name']} — {status_tag}. Navigating to {dest_step_name}.")

    if data["overall_conforms"]:
        banner_html = f"""
        <div style="margin-top: 14px; padding: 14px 18px; border-radius: 8px; background: #f0fdf4; border: 1.5px solid #86efac; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.04); flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 24px;">✅</span>
                <div>
                    <div style="font-weight: 700; color: #166534; font-size: 15px;">Conformity Assessment Passed (100.0% Index)</div>
                    <div style="font-size: 13px; color: #15803d; margin-top: 2px;">
                        System: <strong>{data['system_name']}</strong> — All {data['passed_count']} normative requirements satisfied with zero SHACL violations.
                    </div>
                </div>
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #166534; background: #dcfce7; padding: 6px 12px; border-radius: 6px;">
                ➔ Auto-navigated to {dest_step_name}
            </div>
        </div>
        """
    else:
        banner_html = f"""
        <div style="margin-top: 14px; padding: 14px 18px; border-radius: 8px; background: #fef2f2; border: 1.5px solid #fca5a5; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.04); flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 24px;">❌</span>
                <div>
                    <div style="font-weight: 700; color: #991b1b; font-size: 15px;">Non-Conformities Detected ({data['violations_count']} SHACL Violations Found)</div>
                    <div style="font-size: 13px; color: #b91c1c; margin-top: 2px;">
                        System: <strong>{data['system_name']}</strong> — Conformity score: {data['score']:.1f}%. Immediate statutory remediation required.
                    </div>
                </div>
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #991b1b; background: #fee2e2; padding: 6px 12px; border-radius: 6px;">
                ➔ Auto-navigated to {dest_step_name}
            </div>
        </div>
        """

    return (
        gr.update(selected=target_tab),
        banner_html,
        data["exec_html"],
        data["violations_data"],
        data["claims_data"],
        data["graph_iframe_html"],
        data["cert_token"],
        data["hash_summary"],
        data["json_ld_cert"],
        data["md_report"],
        data["cert_iframe_html"],
        data["borderline_data"],
        data["frameworks_data"],
        data["fine_html"],
        data["bom_json"],
        data["sarif_json"],
    )


def run_assessment_to_step2(doc_text: str, auditor_id: str, annual_turnover: float = 50000000.0, is_sme: bool = False):
    return run_assessment(doc_text, auditor_id, annual_turnover, is_sme, target_tab="tab_review_grounding")


def run_assessment_to_step3(doc_text: str, auditor_id: str, annual_turnover: float = 50000000.0, is_sme: bool = False):
    return run_assessment(doc_text, auditor_id, annual_turnover, is_sme, target_tab="tab_run_shacl_proofs")


# Pre-compute live initial evaluation for default case study so dashboard opens fully populated
DEFAULT_ASSESSMENT = compute_assessment_data(DEFAULT_SPEC_TEXT, "lead_compliance_auditor_01", 50000000.0, False)



def record_triage(claim_id: str, new_status: str, new_category: str, notes: str, auditor_id: str):
    if not claim_id:
        return "⚠️ Please select a Claim ID to triage."
    
    from src.core.models import ExtractedClaim
    target_claim = ExtractedClaim(
        claim_id=claim_id,
        entity_text="Audited Claim",
        category=EntityCategory(new_category),
        assertion_status=AssertionStatus(new_status),
        confidence=0.99,
        normative_article="EU AI Act Article 14",
        evidence_quote=notes or "Auditor confirmed operational control.",
    )
    
    record = engine.triage_queue.record_auditor_decision(
        claim=target_claim,
        auditor_id=auditor_id or "lead_auditor",
        verified_status=AssertionStatus(new_status),
        verified_category=EntityCategory(new_category),
        notes=notes,
    )

    return f"✅ Triplet sample created and recorded into active learning repository! Anchor: '{record['anchor_text'][:50]}...' -> Label: {record['positive_label']}"


# Custom Theme and CSS for Modern, Uncluttered Executive UI
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* -------------------------------------------------------------
   UNIVERSAL TYPOGRAPHY & ANTI-ALIASING
   Crafted with 'Inter' for optimal screen legibility & eye comfort
------------------------------------------------------------- */
*, *::before, *::after {
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    text-rendering: optimizeLegibility !important;
}

.gradio-container {
    max-width: 1440px !important;
    margin: 0 auto !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #1e293b;
    font-size: 13.5px !important;
    line-height: 1.6 !important;
    letter-spacing: -0.01em !important;
}

.dark .gradio-container {
    color: #f1f5f9;
}

/* -------------------------------------------------------------
   EXECUTIVE HERO BANNER
------------------------------------------------------------- */
.hero-header {
    background: linear-gradient(135deg, rgba(248, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.9) 100%);
    border: 1px solid rgba(226, 232, 240, 0.9);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px -4px rgba(0, 0, 0, 0.04);
}

.dark .hero-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%) !important;
    border-color: rgba(51, 65, 85, 0.9) !important;
    box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.4) !important;
}

.hero-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}

.hero-title-group h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    margin: 0 !important;
    letter-spacing: -0.02em !important;
    background: linear-gradient(135deg, #1e293b 0%, #2563eb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
    gap: 10px;
}

.dark .hero-title-group h1 {
    background: linear-gradient(135deg, #f8fafc 0%, #60a5fa 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}

.hero-subtitle {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    color: #64748b !important;
    margin-top: 4px !important;
    font-weight: 500 !important;
    letter-spacing: -0.01em !important;
}

.dark .hero-subtitle {
    color: #94a3b8 !important;
}

.hero-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.hero-pill {
    font-family: 'Inter', sans-serif !important;
    font-size: 11.5px;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 9999px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid #cbd5e1;
    color: #334155;
    letter-spacing: 0.2px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.dark .hero-pill {
    background: rgba(30, 41, 59, 0.85);
    border-color: #475569;
    color: #cbd5e1;
}

/* -------------------------------------------------------------
   SYMMETRIC FORM CONTROLS, LABELS & INPUTS
------------------------------------------------------------- */
label, .gr-form label, .block label, .gr-input-label, span.text-sm {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #334155 !important;
    line-height: 1.4 !important;
    letter-spacing: -0.01em !important;
    margin-bottom: 5px !important;
}

.dark label, .dark .gr-form label, .dark .block label, .dark .gr-input-label, .dark span.text-sm {
    color: #cbd5e1 !important;
}

input, select, .gr-input, .gr-dropdown input {
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    line-height: 1.5 !important;
    color: #0f172a !important;
}

.dark input, .dark select, .dark .gr-input, .dark .gr-dropdown input {
    color: #f8fafc !important;
}

/* Technical Specification Editor with Clean JetBrains Mono */
textarea[placeholder*="system architecture"], textarea[placeholder*="model card"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
    letter-spacing: 0px !important;
}

/* -------------------------------------------------------------
   WORKFLOW TABS (Top-Level & Sub-Tabs)
------------------------------------------------------------- */
#main-tabs > div[role="tablist"],
.main-workflow-tabs > div[role="tablist"] {
    display: flex !important;
    gap: 8px !important;
    background: #f1f5f9 !important;
    padding: 6px !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    margin-bottom: 20px !important;
}

.dark #main-tabs > div[role="tablist"],
.dark .main-workflow-tabs > div[role="tablist"] {
    background: #0f172a !important;
    border-color: #334155 !important;
}

#main-tabs > div[role="tablist"] > button[role="tab"],
.main-workflow-tabs > div[role="tablist"] > button[role="tab"] {
    flex: 1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    padding: 11px 16px !important;
    border-radius: 8px !important;
    color: #475569 !important;
    border: none !important;
    text-align: center !important;
    background: transparent !important;
    letter-spacing: -0.01em !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.dark #main-tabs > div[role="tablist"] > button[role="tab"],
.dark .main-workflow-tabs > div[role="tablist"] > button[role="tab"] {
    color: #94a3b8 !important;
}

#main-tabs > div[role="tablist"] > button[role="tab"]:hover,
.main-workflow-tabs > div[role="tablist"] > button[role="tab"]:hover {
    color: #0f172a !important;
    background: rgba(255, 255, 255, 0.7) !important;
}

.dark #main-tabs > div[role="tablist"] > button[role="tab"]:hover,
.dark .main-workflow-tabs > div[role="tablist"] > button[role="tab"]:hover {
    color: #f8fafc !important;
    background: rgba(30, 41, 59, 0.8) !important;
}

#main-tabs > div[role="tablist"] > button[role="tab"][aria-selected="true"],
#main-tabs > div[role="tablist"] > button[role="tab"].selected,
.main-workflow-tabs > div[role="tablist"] > button[role="tab"][aria-selected="true"],
.main-workflow-tabs > div[role="tablist"] > button[role="tab"].selected {
    background: #ffffff !important;
    color: #2563eb !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    border-bottom: none !important;
}

.dark #main-tabs > div[role="tablist"] > button[role="tab"][aria-selected="true"],
.dark #main-tabs > div[role="tablist"] > button[role="tab"].selected,
.dark .main-workflow-tabs > div[role="tablist"] > button[role="tab"][aria-selected="true"],
.dark .main-workflow-tabs > div[role="tablist"] > button[role="tab"].selected {
    background: #1e293b !important;
    color: #60a5fa !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
}

/* Sub-Tab Navigation */
div[role="tablist"] {
    gap: 6px !important;
    border-bottom: 2px solid #e2e8f0 !important;
    padding-bottom: 2px !important;
    margin-bottom: 14px !important;
}

.dark div[role="tablist"] {
    border-bottom-color: #334155 !important;
}

button[role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    border-radius: 8px 8px 0 0 !important;
    color: #64748b !important;
    border: none !important;
    letter-spacing: -0.01em !important;
    transition: all 0.15s ease !important;
}

.dark button[role="tab"] {
    color: #94a3b8 !important;
}

button[role="tab"]:hover {
    color: #0f172a !important;
    background: rgba(0, 0, 0, 0.03) !important;
}

.dark button[role="tab"]:hover {
    color: #f8fafc !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

button[role="tab"][aria-selected="true"],
button[role="tab"].selected {
    color: #2563eb !important;
    border-bottom: 3px solid #2563eb !important;
    background: transparent !important;
    font-weight: 700 !important;
}

.dark button[role="tab"][aria-selected="true"],
.dark button[role="tab"].selected {
    color: #60a5fa !important;
    border-bottom-color: #60a5fa !important;
}

/* -------------------------------------------------------------
   BUTTONS (Symmetric Typography & Proportions)
------------------------------------------------------------- */
button, .gr-button {
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    line-height: 1.4 !important;
    border-radius: 8px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

button.primary,
button[variant="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 9px !important;
    padding: 11px 20px !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
}

button.primary:hover,
button[variant="primary"]:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px) !important;
}

button.secondary,
button[variant="secondary"] {
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #334155 !important;
}

.dark button.secondary,
.dark button[variant="secondary"] {
    background: #1e293b !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
}

button.secondary:hover,
button[variant="secondary"]:hover {
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}

.dark button.secondary:hover,
.dark button[variant="secondary"]:hover {
    border-color: #60a5fa !important;
    color: #ffffff !important;
}

/* -------------------------------------------------------------
   SYMMETRIC DATA TABLES ACROSS ALL TABS
------------------------------------------------------------- */
table, .gr-dataframe table {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    width: 100% !important;
}

table th, .gr-dataframe th {
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #475569 !important;
    background: #f8fafc !important;
    padding: 10px 14px !important;
    border-bottom: 1.5px solid #e2e8f0 !important;
}

.dark table th, .dark .gr-dataframe th {
    background: #0f172a !important;
    color: #94a3b8 !important;
    border-bottom-color: #334155 !important;
}

table td, .gr-dataframe td {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
    padding: 10px 14px !important;
    color: #334155 !important;
    border-bottom: 1px solid #f1f5f9 !important;
}

.dark table td, .dark .gr-dataframe td {
    color: #cbd5e1 !important;
    border-bottom-color: #1e293b !important;
}

/* -------------------------------------------------------------
   EXECUTIVE SUMMARY & METRIC CARDS
------------------------------------------------------------- */
.summary-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.dark .summary-card {
    background: #1e293b !important;
    border-color: #334155 !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 10px;
}

.summary-title {
    margin: 0;
    color: #0f172a;
    font-family: 'Inter', sans-serif !important;
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.01em;
}

.dark .summary-title {
    color: #f8fafc !important;
}

.status-pill {
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 12.5px;
    letter-spacing: 0.3px;
}

.summary-meta {
    margin: 4px 0;
    color: #475569;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px;
}

.dark .summary-meta {
    color: #94a3b8 !important;
}

.dark .summary-meta strong {
    color: #e2e8f0 !important;
}

.summary-desc {
    margin: 10px 0;
    color: #334155;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px;
    line-height: 1.6;
}

.dark .summary-desc {
    color: #cbd5e1 !important;
}

.metrics-grid {
    display: flex;
    gap: 14px;
    margin-top: 14px;
    flex-wrap: wrap;
}

.metric-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 18px;
    flex: 1;
    min-width: 140px;
}

.dark .metric-box {
    background: #0f172a !important;
    border-color: #334155 !important;
}

.metric-label {
    font-family: 'Inter', sans-serif !important;
    font-size: 11px;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.dark .metric-label {
    color: #94a3b8 !important;
}

.metric-val {
    font-family: 'Inter', sans-serif !important;
    font-size: 22px;
    font-weight: 800;
    margin-top: 4px;
    letter-spacing: -0.02em;
}

.metric-val-main {
    color: #0f172a;
}

.dark .metric-val-main {
    color: #f8fafc !important;
}

/* -------------------------------------------------------------
   ACCORDION & CARDS
------------------------------------------------------------- */
.gr-accordion {
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    background: #f8fafc !important;
    margin: 12px 0 !important;
}

.dark .gr-accordion {
    border-color: #334155 !important;
    background: #0f172a !important;
}

/* Fine Exposure Card */
.fine-liability-card {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
}

.dark .fine-liability-card {
    background: #1e293b !important;
    border-color: #334155 !important;
}

.dark .fine-liability-card .fine-basis {
    background: #0f172a !important;
    color: #cbd5e1 !important;
    border-color: #334155 !important;
}

/* Code & Pre Blocks */
pre, code, .gr-code pre, .gr-code code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
    line-height: 1.55 !important;
}

/* Workflow Step Navigation Footers */
.tab-nav-footer {
    margin-top: 24px !important;
    padding-top: 16px !important;
    border-top: 1px solid #e2e8f0 !important;
}

.dark .tab-nav-footer {
    border-top-color: #334155 !important;
}

.tab1-nav-row {
    margin-top: 12px !important;
}
"""

with gr.Blocks(title="ReguAI: Neuro-Symbolic AI GRC Engine") as demo:
    # 1. Executive Hero Header (Streamlined & Compact)
    gr.HTML(
        """
        <div class="hero-header">
            <div class="hero-title-row">
                <div class="hero-title-group">
                    <h1>🏛️ ReguAI</h1>
                    <div class="hero-subtitle">Deterministic Neuro-Symbolic AI GRC & Automated Conformity Assessment Engine</div>
                </div>
                <div class="hero-badges">
                    <span class="hero-pill">🇪🇺 EU AI Act (2024/1689)</span>
                    <span class="hero-pill">📐 W3C SHACL Deterministic</span>
                    <span class="hero-pill">🔐 W3C PROV-O</span>
                    <span class="hero-pill">📦 CycloneDX 1.6 AI-BOM</span>
                    <span class="hero-pill">🛡️ OASIS SARIF 2.1.0</span>
                </div>
            </div>
        </div>
        """
    )

    with gr.Tabs(elem_id="main-tabs", elem_classes=["main-workflow-tabs"]) as main_tabs:
        # =============================================================
        # TAB 1: 1️⃣ Select Scenario
        # =============================================================
        with gr.TabItem("1️⃣ Select Scenario", id="tab_select_scenario"):
            with gr.Row():
                domain_dropdown = gr.Dropdown(
                    label="🌐 Regulatory Sector",
                    choices=DOMAIN_OPTIONS,
                    value=DEFAULT_DOMAIN,
                    scale=6,
                    interactive=True,
                )
                case_dropdown = gr.Dropdown(
                    label="📁 AI Benchmark Case Study",
                    choices=DEFAULT_CASE_TITLES,
                    value=DEFAULT_CASE_TITLE,
                    scale=6,
                    interactive=True,
                )

            quick_bar_box = gr.HTML(
                value=DEFAULT_QUICK_BAR,
                label="Statutory Summary",
            )

            spec_input = gr.Textbox(
                label="System Technical Specification (Markdown or JSON - Fully Editable)",
                lines=14,
                placeholder="Paste AI system architecture or model card text...",
                value=DEFAULT_SPEC_TEXT,
            )

            with gr.Accordion("⚙️ Corporate Exposure & Auditor Settings (Optional)", open=False):
                with gr.Row():
                    turnover_input = gr.Number(
                        label="Annual Worldwide Turnover (€)",
                        value=50000000.0,
                        step=5000000.0,
                        scale=4,
                        info="Art. 99 administrative fine base",
                    )
                    is_sme_input = gr.Checkbox(
                        label="SME Status",
                        value=False,
                        scale=3,
                        info="Art. 99(6) reduced caps",
                    )
                auditor_input = gr.Textbox(
                    label="Auditor Identifier",
                    value="lead_compliance_auditor_01",
                    info="Embedded into W3C PROV-O digital ledger",
                )

            with gr.Row():
                assess_btn = gr.Button("⚡ Run Assessment & Review Grounding (Step 2) ➔", variant="primary", size="lg", scale=7)
                assess_btn_direct = gr.Button("⚡ Direct to SHACL Proofs (Step 3) ➔", variant="secondary", size="lg", scale=5)

            status_banner_box = gr.HTML(
                value=READY_BANNER_HTML,
                label="Assessment Execution Status",
            )

            with gr.Row(elem_classes=["tab1-nav-row"]):
                jump_to_tab2_btn = gr.Button("🔍 Step 2: Review Grounding & Graph ➔", variant="secondary", size="sm")
                jump_to_tab3_btn = gr.Button("📐 Step 3: View SHACL Proofs & Scorecard ➔", variant="secondary", size="sm")
                jump_to_tab4_btn = gr.Button("📦 Step 4: Export Annex IV Package ➔", variant="secondary", size="sm")

        # =============================================================
        # TAB 2: 2️⃣ Review Grounding
        # =============================================================
        with gr.TabItem("2️⃣ Review Grounding", id="tab_review_grounding"):
            with gr.Tabs():
                with gr.TabItem("🕸️ Knowledge Graph & Ontology"):
                    graph_output = gr.HTML(value=DEFAULT_ASSESSMENT["graph_iframe_html"], label="Force-Directed Knowledge Graph")
                with gr.TabItem("📚 EUR-Lex Legal Factsheet"):
                    factsheet_box = gr.HTML(
                        value=DEFAULT_FACTSHEET,
                        label="Regulatory Factsheet & Provenance",
                    )
                with gr.TabItem("🔍 Extracted Claims"):
                    claims_table = gr.Dataframe(
                        headers=["Claim ID", "Category", "Status", "Confidence", "Target Article", "Evidence Span"],
                        datatype=["str", "str", "str", "str", "str", "str"],
                        value=DEFAULT_ASSESSMENT["claims_data"],
                        label="Extracted Regulatory Claims",
                    )
                with gr.TabItem("👤 Active Learning Triage Queue"):
                    gr.Markdown("### 👤 Borderline Claims Requiring Human Auditor Review")
                    borderline_table = gr.Dataframe(
                        headers=["Claim ID", "Category", "Status", "Confidence", "Evidence Quote"],
                        datatype=["str", "str", "str", "str", "str"],
                        value=DEFAULT_ASSESSMENT["borderline_data"],
                    )
                    with gr.Row():
                        triage_claim_id = gr.Textbox(label="Claim ID", placeholder="e.g. clm_001", scale=3)
                        triage_status = gr.Dropdown(label="Verified Status", choices=[s.value for s in AssertionStatus], value="IMPLEMENTED", scale=4)
                        triage_cat = gr.Dropdown(label="Verified Category", choices=[c.value for c in EntityCategory], value="HUMAN_OVERSIGHT", scale=5)
                    with gr.Row():
                        triage_notes = gr.Textbox(label="Auditor Rationale", placeholder="Explain reason for modification...", scale=8)
                        triage_btn = gr.Button("Submit Triplet", scale=4)
                    triage_result = gr.Markdown()
                with gr.TabItem("🌐 Multi-Framework Crosswalk"):
                    gr.Markdown("### 🇪🇺 EU AI Act ⟷ NIST AI RMF 1.0 ⟷ ISO/IEC 42001:2023 ⟷ GDPR Crosswalk")
                    frameworks_table = gr.Dataframe(
                        headers=["Target Framework", "Control ID", "Control Name", "Status", "Linked AI Act Article", "Audit Guidance"],
                        datatype=["str", "str", "str", "str", "str", "str"],
                        value=DEFAULT_ASSESSMENT["frameworks_data"],
                        label="Harmonized Multi-Framework Controls",
                    )

            with gr.Row(elem_classes=["tab-nav-footer"]):
                nav_tab2_to_tab1 = gr.Button("⬅️ Back to Step 1: Select Scenario", variant="secondary")
                nav_tab2_to_tab3 = gr.Button("Continue to Step 3: Run SHACL Proofs ➔", variant="primary")

        # =============================================================
        # TAB 3: 3️⃣ Run SHACL Proofs
        # =============================================================
        with gr.TabItem("3️⃣ Run SHACL Proofs", id="tab_run_shacl_proofs"):
            with gr.Row():
                assess_btn_tab3 = gr.Button("⚡ Re-Run Deterministic Conformity Proofs", variant="primary", size="md")
            exec_output = gr.HTML(value=DEFAULT_ASSESSMENT["exec_html"], label="Executive Summary")
            fine_liability_output = gr.HTML(value=DEFAULT_ASSESSMENT["fine_html"], label="Article 99 Fine Liability")
            violations_table = gr.Dataframe(
                headers=["Legal Article", "Normative Requirement", "Severity", "SHACL Path", "Remediation Guidance"],
                datatype=["str", "str", "str", "str", "str"],
                value=DEFAULT_ASSESSMENT["violations_data"],
                label="Mathematical Proof: Non-Conformities Found",
            )

            with gr.Row(elem_classes=["tab-nav-footer"]):
                nav_tab3_to_tab2 = gr.Button("⬅️ Back to Step 2: Review Grounding", variant="secondary")
                nav_tab3_to_tab4 = gr.Button("Continue to Step 4: Export Annex IV Package ➔", variant="primary")

        # =============================================================
        # TAB 4: 4️⃣ Export Annex IV Package
        # =============================================================
        with gr.TabItem("4️⃣ Export Annex IV Package", id="tab_export_annex_iv"):
            with gr.Tabs():
                with gr.TabItem("📜 Attestation Certificate (HTML)"):
                    cert_html_output = gr.HTML(value=DEFAULT_ASSESSMENT["cert_iframe_html"])
                with gr.TabItem("📦 CycloneDX 1.6 AI-BOM"):
                    bom_display = gr.Code(value=DEFAULT_ASSESSMENT["bom_json"], language="json", label="CycloneDX 1.6 Machine-Readable AI-BOM")
                with gr.TabItem("🛡️ OASIS SARIF 2.1.0 Report"):
                    sarif_display = gr.Code(value=DEFAULT_ASSESSMENT["sarif_json"], language="json", label="OASIS SARIF 2.1.0 Static Analysis Report")
                with gr.TabItem("📄 Annex IV Report (Markdown)"):
                    report_markdown = gr.Markdown(value=DEFAULT_ASSESSMENT["md_report"])
                with gr.TabItem("🌐 Machine-Readable JSON-LD"):
                    jsonld_display = gr.Code(value=DEFAULT_ASSESSMENT["json_ld_cert"], language="json", label="W3C JSON-LD Digital Certificate")
                with gr.TabItem("🔐 W3C PROV-O Ledger"):
                    token_display = gr.Textbox(value=DEFAULT_ASSESSMENT["cert_token"], label="Official Digital Conformity Token", interactive=False)
                    ledger_display = gr.Markdown(value=DEFAULT_ASSESSMENT["hash_summary"])

            with gr.Row(elem_classes=["tab-nav-footer"]):
                nav_tab4_to_tab3 = gr.Button("⬅️ Back to Step 3: Review Proofs", variant="secondary")
                nav_tab4_to_tab1 = gr.Button("🔄 Start New Scenario (Step 1)", variant="secondary")

    # Assessment outputs list (16 components: main_tabs + status_banner_box + 14 metrics/deliverables)
    assessment_inputs = [spec_input, auditor_input, turnover_input, is_sme_input]
    assessment_outputs = [
        main_tabs,
        status_banner_box,
        exec_output,
        violations_table,
        claims_table,
        graph_output,
        token_display,
        ledger_display,
        jsonld_display,
        report_markdown,
        cert_html_output,
        borderline_table,
        frameworks_table,
        fine_liability_output,
        bom_display,
        sarif_display,
    ]

    # Wire cascading dropdown event handlers
    domain_dropdown.change(
        fn=on_domain_change,
        inputs=[domain_dropdown],
        outputs=[case_dropdown, spec_input, quick_bar_box, factsheet_box, status_banner_box],
    )
    case_dropdown.change(
        fn=on_case_change,
        inputs=[case_dropdown],
        outputs=[spec_input, quick_bar_box, factsheet_box, status_banner_box],
    )

    # Wire assessment buttons (Tab 1 primary to Step 2, direct to Step 3, and Tab 3 re-run)
    assess_btn.click(
        fn=run_assessment_to_step2,
        inputs=assessment_inputs,
        outputs=assessment_outputs,
    )
    assess_btn_direct.click(
        fn=run_assessment_to_step3,
        inputs=assessment_inputs,
        outputs=assessment_outputs,
    )
    assess_btn_tab3.click(
        fn=run_assessment_to_step3,
        inputs=assessment_inputs,
        outputs=assessment_outputs,
    )

    # Workflow step navigation clicks
    jump_to_tab2_btn.click(fn=lambda: gr.update(selected="tab_review_grounding"), outputs=[main_tabs])
    jump_to_tab3_btn.click(fn=lambda: gr.update(selected="tab_run_shacl_proofs"), outputs=[main_tabs])
    jump_to_tab4_btn.click(fn=lambda: gr.update(selected="tab_export_annex_iv"), outputs=[main_tabs])

    nav_tab2_to_tab1.click(fn=lambda: gr.update(selected="tab_select_scenario"), outputs=[main_tabs])
    nav_tab2_to_tab3.click(fn=lambda: gr.update(selected="tab_run_shacl_proofs"), outputs=[main_tabs])

    nav_tab3_to_tab2.click(fn=lambda: gr.update(selected="tab_review_grounding"), outputs=[main_tabs])
    nav_tab3_to_tab4.click(fn=lambda: gr.update(selected="tab_export_annex_iv"), outputs=[main_tabs])

    nav_tab4_to_tab3.click(fn=lambda: gr.update(selected="tab_run_shacl_proofs"), outputs=[main_tabs])
    nav_tab4_to_tab1.click(fn=lambda: gr.update(selected="tab_select_scenario"), outputs=[main_tabs])

    triage_btn.click(
        fn=record_triage,
        inputs=[triage_claim_id, triage_status, triage_cat, triage_notes, auditor_input],
        outputs=[triage_result],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, theme=gr.themes.Soft(), css=CUSTOM_CSS)


