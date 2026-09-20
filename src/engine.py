"""
ReguAI Unified Neuro-Symbolic Engine.
Orchestrates ingestion, extraction, graph building, deterministic SHACL reasoning,
provenance generation, and reporting.
"""

from pathlib import Path
from typing import Union, Dict, Any
from datetime import datetime, timezone

from src.core.models import (
    SystemSpecification,
    ConformityReport,
)
from src.extraction.parser import SpecificationParser
from src.extraction.gliner_extractor import RegulatoryClaimExtractor
from src.ontology.builder import NormativeGraphBuilder
from src.reasoning.shacl_engine import DeterministicSHACLEngine
from src.ledger.provenance import ProvenanceLedger
from src.triage.active_learning import ActiveLearningTriageQueue
from src.triage.report_generator import ConformityReportGenerator
from src.reasoning.framework_crosswalk import MultiFrameworkCrosswalk
from src.reasoning.fine_calculator import FineLiabilityCalculator


class ReguAIEngine:
    def __init__(self):
        self.parser = SpecificationParser()
        self.extractor = RegulatoryClaimExtractor()
        self.graph_builder = NormativeGraphBuilder()
        self.shacl_engine = DeterministicSHACLEngine()
        self.ledger = ProvenanceLedger()
        self.triage_queue = ActiveLearningTriageQueue()
        self.report_generator = ConformityReportGenerator()
        self.crosswalk = MultiFrameworkCrosswalk()
        self.fine_calculator = FineLiabilityCalculator()

    def evaluate_system(
        self,
        input_data: Union[str, Path, Dict[str, Any]],
        auditor_id: str = "reguai_lead_auditor",
        annual_turnover_eur: float = 0.0,
        is_sme: bool = False,
    ) -> ConformityReport:
        """
        Executes full deterministic conformity assessment pipeline:
        1. Parse document or JSON
        2. Extract regulatory claims & evaluate assertions (GLiNER + NegEx)
        3. Construct RDF normative graph
        4. Run deterministic W3C SHACL shape validation
        5. Generate cryptographic W3C PROV-O audit ledger
        6. Compute Multi-Framework Harmonization Crosswalk (NIST / ISO / GDPR)
        7. Calculate Article 99 Statutory Fine Liability
        8. Generate comprehensive ConformityReport
        """
        # 1. Parsing
        if isinstance(input_data, Path):
            spec = self.parser.parse_file(input_data)
        elif isinstance(input_data, dict):
            import json
            spec = self.parser.parse_json(json.dumps(input_data))
        else:
            text = str(input_data).strip()
            if text.startswith("{") and text.endswith("}"):
                spec = self.parser.parse_json(text)
            else:
                spec = self.parser.parse_markdown(text)

        # 2. Extract Claims & ground
        spec = self.extractor.enrich_system_specification(spec)
        borderline_claims = self.triage_queue.filter_borderline_claims(spec.extracted_claims)

        # 3. Construct Knowledge Graph
        system_graph = self.graph_builder.build_system_graph(spec)

        # 4. Deterministic SHACL Reasoning
        conforms, violations, warnings, score = self.shacl_engine.validate_system(system_graph)

        # 5. Cryptographic Provenance Ledger
        provenance = self.ledger.generate_provenance(
            spec=spec,
            system_graph=system_graph,
            conforms=conforms,
            violations_count=len(violations),
            auditor_id=auditor_id,
        )

        # 6. Multi-Framework Harmonization & Article 99 Liability
        crosswalk_res = self.crosswalk.harmonize(violations=violations)
        fine_res = self.fine_calculator.calculate_exposure(
            violations=violations,
            annual_turnover_eur=annual_turnover_eur,
            is_sme=is_sme,
        )

        # 7. Build Conformity Report
        total_reqs = len(violations) + len(warnings) + 6
        passed_reqs = max(0, total_reqs - len(violations))
        now_utc = datetime.now(timezone.utc).isoformat()

        if conforms:
            summary = (
                f"The AI system '{spec.metadata.name}' (Version {spec.metadata.version}) satisfies all mandatory "
                f"EU AI Act Chapter III high-risk requirements based on formal W3C SHACL constraint validation. "
                f"Operational controls for Articles 9 (Risk Management), 10 (Data Governance & Bias Mitigation), "
                f"12 (Logging), 14 (Human Oversight), and 15 (Cybersecurity & Robustness) are verified."
            )
        else:
            violation_articles = ", ".join(sorted(set(v.regulatory_article for v in violations)))
            summary = (
                f"The AI system '{spec.metadata.name}' fails mandatory EU AI Act Chapter III high-risk requirements. "
                f"Formal W3C SHACL constraint validation discovered {len(violations)} non-conformities affecting {violation_articles}. "
                f"Remediation is required before deployment into high-impact environments. "
                f"{fine_res.executive_liability_summary}"
            )

        report = ConformityReport(
            report_id=f"rep_{spec.metadata.system_id}_{provenance.certificate_sha256[:8]}",
            system_metadata=spec.metadata,
            overall_conforms=conforms,
            conformity_score=score,
            total_requirements_evaluated=total_reqs,
            passed_requirements_count=passed_reqs,
            violations=violations,
            warnings=warnings,
            claims_analyzed=spec.extracted_claims,
            borderline_claims=borderline_claims,
            provenance=provenance,
            generated_at_utc=now_utc,
            executive_summary=summary,
            fine_exposure=fine_res.model_dump(),
            harmonized_frameworks=crosswalk_res.model_dump(),
        )

        return report
