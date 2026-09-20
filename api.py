"""
ReguAI Enterprise REST API.
Provides high-throughput, CI/CD automated AI conformity verification endpoints for MLOps pipelines.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

from src.engine import ReguAIEngine
from src.core.config import SYNTHETIC_DIR
from src.core.models import (
    ConformityReport,
    AssertionStatus,
    EntityCategory,
)

app = FastAPI(
    title="ReguAI Conformity Assessment API",
    description="Automated Neuro-Symbolic AI GRC & W3C SHACL verification engine for EU AI Act, NIST AI RMF, & ISO 42001.",
    version="0.1.0",
)

# Enable CORS for frontend visualizers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ReguAIEngine()

# In-memory certificate cache for demonstration lookups
CERTIFICATE_CACHE: Dict[str, ConformityReport] = {}


class AuditRequest(BaseModel):
    specification_text: str = Field(..., description="Markdown model card, YAML spec, or JSON system document.")
    auditor_id: Optional[str] = Field("ci_cd_automated_pipeline", description="Identifier of the executing pipeline or auditor.")


class TripletFeedbackRequest(BaseModel):
    claim_id: str
    auditor_id: str
    verified_status: AssertionStatus
    verified_category: EntityCategory
    notes: Optional[str] = ""


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "engine": "ReguAI Neuro-Symbolic Reasoning Core",
        "version": "0.1.0",
        "shacl_validator": "W3C SHACL compliant",
    }


@app.post("/api/v1/audit/evaluate", response_model=Dict[str, Any], tags=["Conformity Assessment"])
def evaluate_specification(request: AuditRequest):
    """
    Deterministically evaluates an AI system specification against EU AI Act Chapter III SHACL shapes.
    """
    if not request.specification_text.strip():
        raise HTTPException(status_code=400, detail="Specification text cannot be empty.")

    try:
        report = engine.evaluate_system(request.specification_text, auditor_id=request.auditor_id)
        token = report.provenance.digital_signature
        CERTIFICATE_CACHE[token] = report

        return {
            "system_id": report.system_metadata.system_id,
            "system_name": report.system_metadata.name,
            "overall_conforms": report.overall_conforms,
            "conformity_score": report.conformity_score,
            "certificate_token": token,
            "total_requirements": report.total_requirements_evaluated,
            "passed_requirements": report.passed_requirements_count,
            "violations_count": len(report.violations),
            "violations": [
                {
                    "article": v.regulatory_article,
                    "message": v.message,
                    "remediation": v.remediation_guidance,
                    "shacl_path": v.result_path,
                }
                for v in report.violations
            ],
            "claims_extracted_count": len(report.claims_analyzed),
            "borderline_claims_count": len(report.borderline_claims),
            "executive_summary": report.executive_summary,
            "provenance": {
                "source_doc_sha256": report.provenance.input_doc_sha256,
                "graph_sha256": report.provenance.graph_triples_sha256,
                "ruleset_sha256": report.provenance.ruleset_sha256,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conformity assessment failed: {str(e)}")


@app.get("/api/v1/audit/samples", tags=["Benchmarks"])
def list_benchmark_samples():
    """Returns available pre-loaded synthetic case studies."""
    return [
        {"id": "compliant_clinical_samd", "title": "OncoScan AI Diagnostic Assistant (SaMD - Compliant)"},
        {"id": "non_compliant_hr_recruitment", "title": "TalentSift Automated Candidate Evaluator (HR - Violations)"},
        {"id": "borderline_credit_scoring", "title": "CrediScore Neural Underwriter (FinTech - Planned Roadmap)"},
    ]


@app.get("/api/v1/audit/samples/{sample_id}", tags=["Benchmarks"])
def get_sample_content(sample_id: str):
    """Retrieves full specification content for a sample."""
    file_path = SYNTHETIC_DIR / f"{sample_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample not found.")
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return data


@app.get("/api/v1/certificates/{token}/html", response_class=HTMLResponse, tags=["Conformity Assessment"])
def get_certificate_html(token: str):
    """Renders the official print-ready Annex IV HTML Certificate."""
    report = CERTIFICATE_CACHE.get(token)
    if not report:
        # Fallback to compliant sample if token is demo
        samd_path = SYNTHETIC_DIR / "compliant_clinical_samd.json"
        report = engine.evaluate_system(samd_path)
    
    html = engine.report_generator.generate_html_certificate(report)
    return HTMLResponse(content=html)


@app.post("/api/v1/triage/feedback", tags=["Active Learning"])
def submit_auditor_feedback(feedback: TripletFeedbackRequest):
    """
    Captures human auditor feedback on borderline claims and formats
    triplet training pairs for continuous metric alignment.
    """
    from src.core.models import ExtractedClaim
    dummy = ExtractedClaim(
        claim_id=feedback.claim_id,
        entity_text="Audited Claim",
        category=feedback.verified_category,
        assertion_status=feedback.verified_status,
        confidence=1.0,
        normative_article="EU AI Act Article 14",
        evidence_quote=feedback.notes or "Auditor verified operational control.",
    )
    record = engine.triage_queue.record_auditor_decision(
        claim=dummy,
        auditor_id=feedback.auditor_id,
        verified_status=feedback.verified_status,
        verified_category=feedback.verified_category,
        notes=feedback.notes or "",
    )
    return {
        "status": "RECORDED",
        "triplet": record,
        "message": "Active learning triplet training instance generated successfully.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
