"""
Domain-Driven Regulatory Case Study Catalog & Cryptographic Provenance Provider.
Provides authoritative benchmark use cases, statutory reference guides, and SHA-256/W3C PROV-O anchors.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from src.core.config import PROJECT_ROOT, BENCHMARKS_DIR, SYNTHETIC_DIR

CATALOG_PATH = BENCHMARKS_DIR / "case_studies_catalog.json"


class CaseStudyCatalog:
    def __init__(self, catalog_path: Path = CATALOG_PATH):
        self.catalog_path = catalog_path
        self._data: Dict[str, Any] = {}
        self._domains_by_id: Dict[str, Dict[str, Any]] = {}
        self._cases_by_id: Dict[str, Dict[str, Any]] = {}
        self._cases_by_title: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Case studies catalog not found at {self.catalog_path}")
        
        self._data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        self._domains_by_id.clear()
        self._cases_by_id.clear()
        self._cases_by_title.clear()

        for domain in self._data.get("domains", []):
            dom_id = domain["domain_id"]
            self._domains_by_id[dom_id] = domain
            for case in domain.get("case_studies", []):
                case["domain_id"] = dom_id
                case["domain_name"] = domain["domain_name"]
                self._cases_by_id[case["case_id"]] = case
                self._cases_by_title[case["title"]] = case

    @property
    def raw_data(self) -> Dict[str, Any]:
        return self._data

    def list_domains(self) -> List[Dict[str, Any]]:
        return self._data.get("domains", [])

    def get_domain(self, domain_id: str) -> Optional[Dict[str, Any]]:
        return self._domains_by_id.get(domain_id)

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        return self._cases_by_id.get(case_id)

    def get_case_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        return self._cases_by_title.get(title)

    def get_cases_for_domain(self, domain_id_or_name: str) -> List[Dict[str, Any]]:
        for dom in self._data.get("domains", []):
            if dom["domain_id"] == domain_id_or_name or dom["domain_name"] == domain_id_or_name:
                return dom.get("case_studies", [])
        return []

    def get_case_document_text(self, case_id_or_title: str) -> str:
        case = self.get_case(case_id_or_title) or self.get_case_by_title(case_id_or_title)
        if not case:
            return ""
        
        rel_path = case.get("file_path", "")
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            data = json.loads(full_path.read_text(encoding="utf-8"))
            return data.get("raw_document_text", "")
        return ""

    def render_factsheet_html(self, case_id_or_title: str) -> str:
        case = self.get_case(case_id_or_title) or self.get_case_by_title(case_id_or_title)
        if not case:
            return "<div style='padding:15px; color:#64748b;'>Select a case study to display statutory reference factsheet.</div>"

        prov = case.get("provenance", {})
        reqs = case.get("regulatory_requirements", {})
        guidance = case.get("auditor_guidance", {})
        frameworks = reqs.get("harmonized_frameworks", {})
        expected = case.get("expected_conformity", "UNKNOWN")

        # Color coding status pill
        if "PASSED" in expected or "CONFORMANT" in expected:
            pill_color = "#10b981"
            pill_bg = "#ecfdf5"
            pill_border = "#a7f3d0"
        elif "PROHIBITED" in expected:
            pill_color = "#7f1d1d"
            pill_bg = "#fee2e2"
            pill_border = "#f87171"
        elif "FAILED" in expected or "NON-CONFORMANT" in expected:
            pill_color = "#b91c1c"
            pill_bg = "#fef2f2"
            pill_border = "#fca5a5"
        else:
            pill_color = "#d97706"
            pill_bg = "#fffbeb"
            pill_border = "#fde68a"

        # Mandatory articles tags
        articles_html = " ".join([
            f"<span style='background:#e2e8f0; color:#334155; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600;'>{a}</span>"
            for a in reqs.get("mandatory_articles", [])
        ])

        # NIST tags
        nist_html = " ".join([
            f"<span style='background:#dbeafe; color:#1e40af; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:500;'>{n}</span>"
            for n in frameworks.get("nist_ai_rmf", [])
        ])

        # ISO tags
        iso_html = " ".join([
            f"<span style='background:#f3e8ff; color:#6b21a8; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:500;'>{i}</span>"
            for i in frameworks.get("iso_42001", [])
        ])

        # GDPR tags
        gdpr_html = " ".join([
            f"<span style='background:#e0e7ff; color:#3730a3; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:500;'>{g}</span>"
            for g in frameworks.get("gdpr", [])
        ])

        html = f"""
        <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.05); font-family:-apple-system,BlinkMacSystemFont,sans-serif;" class="factsheet-container">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
                <div>
                    <span style="background:#0284c7; color:#ffffff; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">
                        {case.get('domain_name', 'Domain')}
                    </span>
                    <h3 style="margin:6px 0 2px 0; font-size:16px; font-weight:700; color:#0f172a;">
                        {case.get('title')}
                    </h3>
                    <div style="font-size:12px; color:#64748b;">
                        <strong>Legal Basis:</strong> <span style="color:#2563eb;">{case.get('legal_basis')}</span>
                    </div>
                </div>
                <div>
                    <span style="background:{pill_bg}; color:{pill_color}; border:1px solid {pill_border}; padding:4px 12px; border-radius:6px; font-size:12px; font-weight:700;">
                        {expected}
                    </span>
                </div>
            </div>

            <div style="background:#f8fafc; border-left:4px solid #3b82f6; padding:10px 12px; border-radius:4px; margin-bottom:12px; font-size:13px; color:#334155; line-height:1.5;">
                <strong>🎯 Statutory Intended Purpose:</strong> {guidance.get('intended_purpose', '')}
            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:12px; margin-bottom:12px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; margin-bottom:4px;">Mandatory EU AI Act Requirements</div>
                    <div style="display:flex; flex-wrap:wrap; gap:4px; margin-top:4px;">{articles_html or 'N/A'}</div>
                    <div style="margin-top:8px; font-size:11px; color:#475569;">
                        <strong>Conformity Procedure:</strong> {reqs.get('conformity_procedure', 'N/A')}
                    </div>
                    <div style="margin-top:4px; font-size:11px; color:#b91c1c; font-weight:600;">
                        <strong>Statutory Fine Ceiling:</strong> {reqs.get('fine_exposure_tier', 'N/A')}
                    </div>
                </div>

                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                    <div style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; margin-bottom:4px;">Harmonized Framework Crosswalk</div>
                    <div style="margin-bottom:4px; font-size:11px;"><strong>NIST AI RMF:</strong> {nist_html or 'None'}</div>
                    <div style="margin-bottom:4px; font-size:11px;"><strong>ISO/IEC 42001:</strong> {iso_html or 'None'}</div>
                    <div style="font-size:11px;"><strong>GDPR:</strong> {gdpr_html or 'None'}</div>
                </div>
            </div>

            <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:6px; padding:10px 12px; margin-bottom:12px; font-size:12px; color:#92400e; line-height:1.5;">
                <strong>⚠️ Auditor Pitfall & Common Failure Mode:</strong> {guidance.get('common_pitfalls', '')}
            </div>

            <!-- Cryptographic Provenance Block -->
            <div style="background:#0f172a; color:#cbd5e1; border-radius:6px; padding:12px; font-size:11px; line-height:1.6;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:6px; margin-bottom:6px;">
                    <span style="font-weight:700; color:#38bdf8; display:flex; align-items:center; gap:4px;">
                        🔐 Cryptographic Provenance & Legal Anchor (EUR-Lex)
                    </span>
                    <a href="{prov.get('eli_uri', 'http://data.europa.eu/eli/reg/2024/1689/oj')}" target="_blank" style="color:#60a5fa; text-decoration:none; font-weight:600;">
                        CELEX:{prov.get('celex', '32024R1689')} ↗
                    </a>
                </div>
                <div style="font-style:italic; color:#94a3b8; margin-bottom:6px; font-size:11px; border-left:2px solid #38bdf8; padding-left:8px;">
                    "{prov.get('statutory_quote', '')[:220]}..."
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-family:monospace; font-size:10px;">
                    <div><span style="color:#64748b;">Statutory Quote SHA-256:</span> <span style="color:#a7f3d0;">{prov.get('statutory_quote_sha256', '')[:16]}...</span></div>
                    <div><span style="color:#64748b;">Model Spec SHA-256:</span> <span style="color:#a7f3d0;">{prov.get('spec_file_sha256', '')[:16]}...</span></div>
                    <div style="grid-column: span 2;"><span style="color:#64748b;">W3C PROV-O Entity:</span> <span style="color:#bae6fd;">{prov.get('prov_o_entity', '')}</span></div>
                </div>
            </div>
        </div>
        """
        return html
