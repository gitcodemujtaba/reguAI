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


def on_domain_change(selected_domain_name: str):
    cases = catalog.get_cases_for_domain(selected_domain_name)
    if not cases:
        return gr.update(choices=[], value=None), "", "", "<div style='padding:15px;'>No cases found.</div>"
    titles = [c["title"] for c in cases]
    first_title = titles[0]
    text = catalog.get_case_document_text(first_title)
    factsheet = catalog.render_factsheet_html(first_title)
    quick_bar = catalog.render_quick_bar(first_title)
    return gr.update(choices=titles, value=first_title), text, quick_bar, factsheet


def on_case_change(selected_case_title: str):
    if not selected_case_title:
        return "", "", "<div style='padding:15px;'>Select a case study.</div>"
    text = catalog.get_case_document_text(selected_case_title)
    factsheet = catalog.render_factsheet_html(selected_case_title)
    quick_bar = catalog.render_quick_bar(selected_case_title)
    return text, quick_bar, factsheet


def load_preset(domain_idx: int, case_idx: int = 0):
    domains = catalog.list_domains()
    if domain_idx >= len(domains):
        domain_idx = 0
    dom = domains[domain_idx]
    dom_name = dom["domain_name"]
    cases = dom.get("case_studies", [])
    if not cases:
        return gr.update(), gr.update(), "", "", ""
    case = cases[min(case_idx, len(cases) - 1)]
    case_title = case["title"]
    case_titles = [c["title"] for c in cases]
    text = catalog.get_case_document_text(case_title)
    factsheet = catalog.render_factsheet_html(case_title)
    quick_bar = catalog.render_quick_bar(case_title)
    return (
        gr.update(value=dom_name),
        gr.update(choices=case_titles, value=case_title),
        text,
        quick_bar,
        factsheet,
    )


def run_assessment(doc_text: str, auditor_id: str, annual_turnover: float = 50000000.0, is_sme: bool = False):
    if not doc_text or not doc_text.strip():
        return (
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
        )

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

    return (
        exec_html,
        violations_data,
        claims_data,
        graph_iframe_html,
        cert_token,
        hash_summary,
        json_ld_cert,
        md_report,
        cert_iframe_html,
        borderline_data,
        frameworks_data,
        fine_html,
    )


def load_preset_and_assess(domain_idx: int, case_idx: int, auditor_id: str, turnover: float, is_sme: bool):
    dom_update, case_update, text, quick_bar, factsheet = load_preset(domain_idx, case_idx)
    assessment_res = run_assessment(text, auditor_id, turnover, is_sme)
    return (dom_update, case_update, text, quick_bar, factsheet, *assessment_res)


# Pre-compute live initial evaluation for default case study so dashboard opens fully populated
DEFAULT_ASSESSMENT = run_assessment(DEFAULT_SPEC_TEXT, "lead_compliance_auditor_01", 50000000.0, False)


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


# Custom Theme and CSS for Dark & Light Mode Contrast
CUSTOM_CSS = """
/* Container */
.gradio-container {
    max-width: 1380px !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* -------------------------------------------------------------
   TABS STYLING (Dark & Light Mode High-Contrast)
------------------------------------------------------------- */
.tabs > .tab-nav button,
div[role="tablist"] button,
button[role="tab"],
.tab-nav button {
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 16px !important;
    border-radius: 6px 6px 0 0 !important;
    transition: all 0.15s ease-in-out !important;
}

.dark .tabs > .tab-nav button,
.dark div[role="tablist"] button,
.dark button[role="tab"],
.dark .tab-nav button {
    color: #cbd5e1 !important;
    background: transparent !important;
}

.tabs > .tab-nav button:hover,
div[role="tablist"] button:hover,
button[role="tab"]:hover {
    color: #0f172a !important;
    background: rgba(0, 0, 0, 0.04) !important;
}

.dark .tabs > .tab-nav button:hover,
.dark div[role="tablist"] button:hover,
.dark button[role="tab"]:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

.tabs > .tab-nav button.selected,
div[role="tablist"] button.selected,
button[role="tab"][aria-selected="true"],
button[role="tab"].selected {
    color: #2563eb !important;
    border-bottom: 3px solid #2563eb !important;
    font-weight: 700 !important;
}

.dark .tabs > .tab-nav button.selected,
.dark div[role="tablist"] button.selected,
.dark button[role="tab"][aria-selected="true"],
.dark button[role="tab"].selected {
    color: #60a5fa !important;
    border-bottom: 3px solid #60a5fa !important;
    background: rgba(96, 165, 250, 0.1) !important;
}

/* -------------------------------------------------------------
   BUTTONS STYLING (Dark & Light Mode High-Contrast)
------------------------------------------------------------- */
button.primary,
button[variant="primary"],
.gr-button-primary,
button.lg {
    background: #2563eb !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3) !important;
}

button.primary:hover,
button[variant="primary"]:hover,
button.lg:hover {
    background: #1d4ed8 !important;
    color: #ffffff !important;
}

.dark button.primary,
.dark button[variant="primary"],
.dark .gr-button-primary {
    background: #2563eb !important;
    color: #ffffff !important;
}

button:not(.primary):not([variant="primary"]) {
    color: #1e293b !important;
}

.dark button:not(.primary):not([variant="primary"]) {
    color: #f8fafc !important;
    background: #334155 !important;
    border-color: #475569 !important;
}

.dark button:not(.primary):not([variant="primary"]):hover {
    background: #475569 !important;
    color: #ffffff !important;
}

/* -------------------------------------------------------------
   SUMMARY CARD (Dark & Light Mode Dynamic Classes)
------------------------------------------------------------- */
.summary-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 15px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.dark .summary-card {
    background: #1e293b !important;
    border-color: #334155 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.summary-title {
    margin: 0;
    color: #0f172a;
    font-size: 20px;
    font-weight: 700;
}

.dark .summary-title {
    color: #f8fafc !important;
}

.status-pill {
    color: #ffffff !important;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
}

.summary-meta {
    margin: 4px 0;
    color: #475569;
    font-size: 14px;
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
    font-size: 14px;
    line-height: 1.6;
}

.dark .summary-desc {
    color: #cbd5e1 !important;
}

.metrics-grid {
    display: flex;
    gap: 16px;
    margin-top: 14px;
}

.metric-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    flex: 1;
}

.dark .metric-box {
    background: #0f172a !important;
    border-color: #334155 !important;
}

.metric-label {
    font-size: 11px;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.dark .metric-label {
    color: #94a3b8 !important;
}

.metric-val {
    font-size: 22px;
    font-weight: 700;
    margin-top: 4px;
}

.metric-val-main {
    color: #0f172a;
}

.dark .metric-val-main {
    color: #f8fafc !important;
}

/* -------------------------------------------------------------
   HEADER BADGES
------------------------------------------------------------- */
.header-badge {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    color: #334155;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

.dark .header-badge {
    background: #1e293b !important;
    border-color: #475569 !important;
    color: #e2e8f0 !important;
}

/* -------------------------------------------------------------
   FACTSHEET & PROVENANCE STYLING (Dark & Light Mode)
------------------------------------------------------------- */
.factsheet-container {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}

.dark .factsheet-container {
    background: #1e293b !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
}

.dark .factsheet-container h3 {
    color: #f8fafc !important;
}

.dark .factsheet-container div[style*="background:#f8fafc"] {
    background: #0f172a !important;
    border-color: #334155 !important;
    color: #cbd5e1 !important;
}

.dark .factsheet-container div[style*="background:#fffbeb"] {
    background: #451a03 !important;
    border-color: #78350f !important;
    color: #fef3c7 !important;
}

/* Quick Summary Bar */
.quick-summary-bar {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 6px !important;
}

.dark .quick-summary-bar {
    background: #0f172a !important;
    border-color: #334155 !important;
    color: #cbd5e1 !important;
}

/* -------------------------------------------------------------
   WORKFLOW STEPPER
------------------------------------------------------------- */
.workflow-stepper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 18px;
    margin: 12px 0 16px 0;
    gap: 8px;
    flex-wrap: wrap;
}

.dark .workflow-stepper {
    background: #0f172a !important;
    border-color: #334155 !important;
}

.step-card {
    display: flex;
    align-items: center;
    gap: 10px;
}

.step-num {
    background: #2563eb;
    color: #ffffff !important;
    font-weight: 800;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}

.step-text {
    font-size: 12px;
    color: #475569;
    line-height: 1.25;
}

.dark .step-text {
    color: #94a3b8 !important;
}

.step-text strong {
    display: block;
    color: #0f172a;
    font-size: 13px;
}

.dark .step-text strong {
    color: #f8fafc !important;
}

.step-arrow {
    color: #94a3b8;
    font-weight: 700;
    font-size: 15px;
}

/* -------------------------------------------------------------
   PRESET BUTTONS
------------------------------------------------------------- */
.preset-btn {
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #1e293b !important;
    transition: all 0.15s ease !important;
}

.preset-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.08) !important;
}

.dark .preset-btn {
    background: #1e293b !important;
    border-color: #334155 !important;
    color: #f8fafc !important;
}

.dark .preset-btn:hover {
    background: #334155 !important;
}

/* -------------------------------------------------------------
   FINE LIABILITY CARD DARK MODE
------------------------------------------------------------- */
.dark .fine-liability-card {
    background: #1e293b !important;
    border-color: #334155 !important;
}

.dark .fine-liability-card .fine-basis {
    background: #0f172a !important;
    color: #cbd5e1 !important;
    border-color: #334155 !important;
}
"""

with gr.Blocks(title="ReguAI: Neuro-Symbolic AI GRC Engine") as demo:
    gr.Markdown(
        """
        # 🏛️ ReguAI: Deterministic Neuro-Symbolic AI GRC & Conformity Engine
        ### Automated EU AI Act (Regulation (EU) 2024/1689), NIST AI RMF, & ISO/IEC 42001 Auditing
        Grounds enterprise model cards and technical documentation into an authoritative normative knowledge graph,
        applying **mathematically deterministic W3C SHACL shape constraints** backed by a **W3C PROV-O cryptographic audit ledger**.
        
        <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
            <span class="header-badge">🇪🇺 EU AI Act High-Risk (Arts. 9-15)</span>
            <span class="header-badge">📐 W3C SHACL Deterministic Proofs</span>
            <span class="header-badge">🌐 Multi-Framework Crosswalk (NIST & ISO)</span>
            <span class="header-badge">💰 Article 99 Statutory Fine Modeling</span>
            <span class="header-badge">🔗 W3C PROV-O Audit Ledger</span>
            <span class="header-badge">👤 Auditor-in-the-Loop Active Learning</span>
        </div>

        <div class="workflow-stepper">
            <div class="step-card">
                <span class="step-num">1</span>
                <div class="step-text">
                    <strong>Select AI Scenario</strong>
                    1-Click Preset or 11 EU Domains
                </div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="step-card">
                <span class="step-num">2</span>
                <div class="step-text">
                    <strong>Review Legal Grounding</strong>
                    EUR-Lex CELEX & W3C PROV-O
                </div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="step-card">
                <span class="step-num">3</span>
                <div class="step-text">
                    <strong>Run Deterministic Audit</strong>
                    W3C SHACL Mathematical Proofs
                </div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="step-card">
                <span class="step-num">4</span>
                <div class="step-text">
                    <strong>Export Findings & Cert</strong>
                    Annex IV Certificate, Fines & Graph
                </div>
            </div>
        </div>
        """
    )

    with gr.Row():
        with gr.Column(scale=5):
            gr.Markdown("**⚡ 1-Click Quick Scenarios (Click to Instantly Evaluate):**")
            with gr.Row():
                preset_samd = gr.Button("🏥 Compliant SaMD", size="sm", elem_classes=["preset-btn"])
                preset_hr = gr.Button("💼 Failed HR AI", size="sm", elem_classes=["preset-btn"])
                preset_prohibited = gr.Button("🚫 Prohibited AI", size="sm", elem_classes=["preset-btn"])
                preset_gpai = gr.Button("🌐 Frontier GPAI", size="sm", elem_classes=["preset-btn"])
                preset_grid = gr.Button("⚡ Critical Grid", size="sm", elem_classes=["preset-btn"])

            with gr.Row():
                domain_dropdown = gr.Dropdown(
                    label="🌐 1. Select Regulatory Domain",
                    choices=DOMAIN_OPTIONS,
                    value=DEFAULT_DOMAIN,
                    scale=6,
                    interactive=True,
                    info="11 statutory sectors under EU AI Act",
                )
                case_dropdown = gr.Dropdown(
                    label="📁 2. Select AI Benchmark Case Study",
                    choices=DEFAULT_CASE_TITLES,
                    value=DEFAULT_CASE_TITLE,
                    scale=6,
                    interactive=True,
                    info="Canonical legal scenarios with EUR-Lex provenance",
                )

            quick_bar_box = gr.HTML(
                value=DEFAULT_QUICK_BAR,
                label="Statutory Quick Summary",
            )

            with gr.Tabs():
                with gr.TabItem("📄 Technical Specification / Model Card"):
                    spec_input = gr.Textbox(
                        label="System Technical Specification (Markdown or JSON - Fully Editable)",
                        lines=12,
                        placeholder="Paste AI system architecture or model card text...",
                        value=DEFAULT_SPEC_TEXT,
                        info="Grounds natural language model cards into normative RDF knowledge graph",
                    )
                with gr.TabItem("📚 Statutory Factsheet & Cryptographic Provenance"):
                    factsheet_box = gr.HTML(
                        value=DEFAULT_FACTSHEET,
                        label="Full Regulatory Factsheet & EUR-Lex Provenance",
                    )

            with gr.Row():
                auditor_input = gr.Textbox(
                    label="Auditor Identifier",
                    value="lead_compliance_auditor_01",
                    scale=5,
                    info="Embedded in W3C PROV-O audit ledger",
                )
                turnover_input = gr.Number(
                    label="Annual Turnover (€)",
                    value=50000000.0,
                    step=5000000.0,
                    scale=4,
                    info="For Art. 99 administrative fine modeling",
                )
                is_sme_input = gr.Checkbox(
                    label="SME Status",
                    value=False,
                    scale=3,
                    info="Art. 99(6) reduced fine caps (whichever is lower)",
                )

            assess_btn = gr.Button("⚡ Run Deterministic Conformity Assessment", variant="primary", size="lg")

        with gr.Column(scale=7):
            exec_output = gr.HTML(value=DEFAULT_ASSESSMENT[0], label="Executive Conformity Summary")
            
            with gr.Tabs():
                with gr.TabItem("⚖️ SHACL Deterministic Violations"):
                    violations_table = gr.Dataframe(
                        headers=["Legal Article", "Normative Requirement", "Severity", "SHACL Path", "Remediation Guidance"],
                        datatype=["str", "str", "str", "str", "str"],
                        value=DEFAULT_ASSESSMENT[1],
                        label="Mathematical Proof: Non-Conformities Found",
                    )

                with gr.TabItem("📊 Multi-Framework Crosswalk"):
                    gr.Markdown("### 🇪🇺 EU AI Act ⟷ NIST AI RMF 1.0 ⟷ ISO/IEC 42001:2023 ⟷ GDPR")
                    frameworks_table = gr.Dataframe(
                        headers=["Target Framework", "Control ID", "Control Name", "Status", "Linked AI Act Article", "Audit Guidance"],
                        datatype=["str", "str", "str", "str", "str", "str"],
                        value=DEFAULT_ASSESSMENT[10],
                        label="Automated Cross-Regulatory Control Status",
                    )

                with gr.TabItem("💰 Article 99 Fine Liability"):
                    fine_liability_output = gr.HTML(value=DEFAULT_ASSESSMENT[11], label="Corporate Balance Sheet Exposure")

                with gr.TabItem("🕸️ Interactive Regulatory Graph"):
                    graph_output = gr.HTML(value=DEFAULT_ASSESSMENT[3], label="Force-Directed Regulatory Dependency Network")

                with gr.TabItem("🔍 Extracted Regulatory Claims"):
                    claims_table = gr.Dataframe(
                        headers=["Claim ID", "Category", "Status", "Confidence", "Target Article", "Evidence Span"],
                        datatype=["str", "str", "str", "str", "str", "str"],
                        value=DEFAULT_ASSESSMENT[2],
                        label="Domain-Adapted Claim Extraction & NegEx Grounding",
                    )

                with gr.TabItem("👤 Auditor Triage & Active Learning"):
                    gr.Markdown("### Borderline Claims Requiring Human Auditor Review")
                    borderline_table = gr.Dataframe(
                        headers=["Claim ID", "Category", "Status", "Confidence", "Evidence Quote"],
                        datatype=["str", "str", "str", "str", "str"],
                        value=DEFAULT_ASSESSMENT[9],
                    )
                    with gr.Row():
                        triage_claim_id = gr.Textbox(label="Claim ID to Triage", placeholder="e.g. clm_001")
                        triage_status = gr.Dropdown(label="Verified Assertion Status", choices=[s.value for s in AssertionStatus], value="IMPLEMENTED")
                        triage_cat = gr.Dropdown(label="Verified Normative Category", choices=[c.value for c in EntityCategory], value="HUMAN_OVERSIGHT")
                    triage_notes = gr.Textbox(label="Auditor Decision Rationale", placeholder="Explain reason for modification...")
                    triage_btn = gr.Button("Submit Auditor Triplet Feedback")
                    triage_result = gr.Markdown()

                with gr.TabItem("🔐 Cryptographic Audit Ledger"):
                    token_display = gr.Textbox(value=DEFAULT_ASSESSMENT[4], label="Official Digital Conformity Token", interactive=False)
                    ledger_display = gr.Markdown(value=DEFAULT_ASSESSMENT[5])

                with gr.TabItem("📑 Export Technical Documentation (Annex IV)"):
                    with gr.Tabs():
                        with gr.TabItem("📜 Official Print-Ready Certificate (HTML)"):
                            cert_html_output = gr.HTML(value=DEFAULT_ASSESSMENT[8])
                        with gr.TabItem("Annex IV Official Report (Markdown)"):
                            report_markdown = gr.Markdown(value=DEFAULT_ASSESSMENT[7])
                        with gr.TabItem("Machine-Readable JSON-LD"):
                            jsonld_display = gr.Code(value=DEFAULT_ASSESSMENT[6], language="json", label="W3C JSON-LD Digital Certificate")

    # Outputs list for 1-click preset execution (17 components)
    preset_outputs = [
        domain_dropdown,
        case_dropdown,
        spec_input,
        quick_bar_box,
        factsheet_box,
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
    ]

    # Wire 1-Click Preset Scenario Buttons
    preset_samd.click(
        fn=lambda a, t, s: load_preset_and_assess(0, 0, a, t, s),
        inputs=[auditor_input, turnover_input, is_sme_input],
        outputs=preset_outputs,
    )
    preset_hr.click(
        fn=lambda a, t, s: load_preset_and_assess(1, 0, a, t, s),
        inputs=[auditor_input, turnover_input, is_sme_input],
        outputs=preset_outputs,
    )
    preset_prohibited.click(
        fn=lambda a, t, s: load_preset_and_assess(8, 1, a, t, s),
        inputs=[auditor_input, turnover_input, is_sme_input],
        outputs=preset_outputs,
    )
    preset_gpai.click(
        fn=lambda a, t, s: load_preset_and_assess(7, 0, a, t, s),
        inputs=[auditor_input, turnover_input, is_sme_input],
        outputs=preset_outputs,
    )
    preset_grid.click(
        fn=lambda a, t, s: load_preset_and_assess(4, 0, a, t, s),
        inputs=[auditor_input, turnover_input, is_sme_input],
        outputs=preset_outputs,
    )

    # Wire cascading dropdown event handlers
    domain_dropdown.change(
        fn=on_domain_change,
        inputs=[domain_dropdown],
        outputs=[case_dropdown, spec_input, quick_bar_box, factsheet_box],
    )
    case_dropdown.change(
        fn=on_case_change,
        inputs=[case_dropdown],
        outputs=[spec_input, quick_bar_box, factsheet_box],
    )

    # Wire manual assessment button
    assess_btn.click(
        fn=run_assessment,
        inputs=[spec_input, auditor_input, turnover_input, is_sme_input],
        outputs=[
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
        ],
    )

    triage_btn.click(
        fn=record_triage,
        inputs=[triage_claim_id, triage_status, triage_cat, triage_notes, auditor_input],
        outputs=[triage_result],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, theme=gr.themes.Soft(), css=CUSTOM_CSS)

