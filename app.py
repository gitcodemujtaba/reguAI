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

# Initialize ReguAI Engine & Graph Visualizer
engine = ReguAIEngine()
graph_viewer = RegulatoryGraphView()

# Pre-load sample specifications
SAMPLE_PATHS = {
    "Healthcare / Medical AI (Compliant SaMD - Articles 9-15 Passed)": SYNTHETIC_DIR / "compliant_clinical_samd.json",
    "HR / Recruitment AI (High-Risk - Human Oversight & Bias Non-Conformities)": SYNTHETIC_DIR / "non_compliant_hr_recruitment.json",
    "FinTech / Credit Underwriting (Borderline - Planned Roadmap & Auditor Review)": SYNTHETIC_DIR / "borderline_credit_scoring.json",
    "EdTech / Surveillance AI (Prohibited - Article 5(1)(f) Emotion Recognition)": SYNTHETIC_DIR / "prohibited_emotion_recognition_workplace.json",
    "GPAI Foundation LLM (Systemic Risk - Articles 51-55 Compute > 10^25 FLOPs)": SYNTHETIC_DIR / "gpai_foundation_llm.json",
}

def load_sample_content(sample_name: str) -> str:
    path = SAMPLE_PATHS.get(sample_name)
    if path and path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("raw_document_text", "")
    return ""


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
    <div style="background: {bg}; border: 1px solid {border}; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
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
        <div style="font-size: 13px; color: #1e293b; line-height: 1.6; background: rgba(255,255,255,0.85); padding: 12px 16px; border-radius: 6px; border: 1px solid #e2e8f0;">
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
        """
    )

    with gr.Row():
        with gr.Column(scale=5):
            sample_dropdown = gr.Dropdown(
                label="📁 Select Pre-loaded High-Risk AI Benchmark Case Study",
                choices=list(SAMPLE_PATHS.keys()),
                value=list(SAMPLE_PATHS.keys())[0],
            )
            spec_input = gr.Textbox(
                label="📄 System Technical Specification / Model Card (Markdown or JSON)",
                lines=14,
                placeholder="Paste AI system architecture or model card text...",
                value=load_sample_content(list(SAMPLE_PATHS.keys())[0]),
            )
            auditor_input = gr.Textbox(
                label="Auditor Credential Identifier",
                value="lead_compliance_auditor_01",
                placeholder="e.g. auditor@enterprise.org",
            )
            with gr.Accordion("💰 Article 99 Corporate Fine Modeling", open=False):
                turnover_input = gr.Number(
                    label="Worldwide Annual Turnover (EUR)",
                    value=50000000.0,
                    step=5000000.0,
                    info="Used to calculate maximum turnover percentage ceilings under Article 99"
                )
                is_sme_input = gr.Checkbox(
                    label="SME / Startup Status (Article 99(6) Special Ceiling)",
                    value=False,
                    info="Applies lower of fixed amount or turnover percentage"
                )
            assess_btn = gr.Button("⚡ Run Deterministic Conformity Assessment", variant="primary", size="lg")

        with gr.Column(scale=7):
            exec_output = gr.HTML(label="Executive Conformity Summary")
            
            with gr.Tabs():
                with gr.TabItem("🌐 Interactive Regulatory Graph"):
                    graph_output = gr.HTML(label="Force-Directed Regulatory Dependency Network")

                with gr.TabItem("⚖️ SHACL Deterministic Violations"):
                    violations_table = gr.Dataframe(
                        headers=["Legal Article", "Normative Requirement", "Severity", "SHACL Path", "Remediation Guidance"],
                        datatype=["str", "str", "str", "str", "str"],
                        label="Mathematical Proof: Non-Conformities Found",
                    )

                with gr.TabItem("🌐 Multi-Framework Crosswalk"):
                    gr.Markdown("### 🇪🇺 EU AI Act ⟷ NIST AI RMF 1.0 ⟷ ISO/IEC 42001:2023 ⟷ GDPR")
                    frameworks_table = gr.Dataframe(
                        headers=["Target Framework", "Control ID", "Control Name", "Status", "Linked AI Act Article", "Audit Guidance"],
                        datatype=["str", "str", "str", "str", "str", "str"],
                        label="Automated Cross-Regulatory Control Status",
                    )

                with gr.TabItem("💰 Article 99 Fine Liability"):
                    fine_liability_output = gr.HTML(label="Corporate Balance Sheet Exposure")

                with gr.TabItem("🔍 Extracted Regulatory Claims"):
                    claims_table = gr.Dataframe(
                        headers=["Claim ID", "Category", "Status", "Confidence", "Target Article", "Evidence Span"],
                        datatype=["str", "str", "str", "str", "str", "str"],
                        label="Domain-Adapted Claim Extraction & NegEx Grounding",
                    )

                with gr.TabItem("👤 Auditor Triage & Active Learning"):
                    gr.Markdown("### Borderline Claims Requiring Human Auditor Review")
                    borderline_table = gr.Dataframe(
                        headers=["Claim ID", "Category", "Status", "Confidence", "Evidence Quote"],
                        datatype=["str", "str", "str", "str", "str"],
                    )
                    with gr.Row():
                        triage_claim_id = gr.Textbox(label="Claim ID to Triage", placeholder="e.g. clm_001")
                        triage_status = gr.Dropdown(label="Verified Assertion Status", choices=[s.value for s in AssertionStatus], value="IMPLEMENTED")
                        triage_cat = gr.Dropdown(label="Verified Normative Category", choices=[c.value for c in EntityCategory], value="HUMAN_OVERSIGHT")
                    triage_notes = gr.Textbox(label="Auditor Decision Rationale", placeholder="Explain reason for modification...")
                    triage_btn = gr.Button("Submit Auditor Triplet Feedback")
                    triage_result = gr.Markdown()

                with gr.TabItem("🔐 Cryptographic Audit Ledger"):
                    token_display = gr.Textbox(label="Official Digital Conformity Token", interactive=False)
                    ledger_display = gr.Markdown()

                with gr.TabItem("📑 Export Technical Documentation (Annex IV)"):
                    with gr.Tabs():
                        with gr.TabItem("📜 Official Print-Ready Certificate (HTML)"):
                            cert_html_output = gr.HTML()
                        with gr.TabItem("Annex IV Official Report (Markdown)"):
                            report_markdown = gr.Markdown()
                        with gr.TabItem("Machine-Readable JSON-LD"):
                            jsonld_display = gr.Code(language="json", label="W3C JSON-LD Digital Certificate")

    # Wire event handlers
    sample_dropdown.change(
        fn=load_sample_content,
        inputs=[sample_dropdown],
        outputs=[spec_input],
    )

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
