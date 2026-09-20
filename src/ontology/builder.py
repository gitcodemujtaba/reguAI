"""
RDF Knowledge Graph Builder.
Constructs RDFLib graphs from system specifications and extracted claims,
binding them to formal legal ontologies.
"""

from typing import Tuple, Dict, Any, List
import re
import rdflib
from rdflib import Graph, URIRef, Literal, RDF, RDFS, XSD

from src.core.config import REGU, EU_ACT, NIST, ISO, PROV, SH, SCHEMAS_DIR
from src.core.models import (
    SystemSpecification,
    ExtractedClaim,
    EntityCategory,
    AssertionStatus,
)


class NormativeGraphBuilder:
    def __init__(self):
        self.category_predicate_map = {
            EntityCategory.RISK_MANAGEMENT: (REGU.hasRiskManagementSystem, REGU.RiskManagementSystem),
            EntityCategory.DATA_GOVERNANCE: (REGU.hasDataGovernance, REGU.DataGovernanceProcess),
            EntityCategory.BIAS_MITIGATION: (REGU.hasBiasMitigation, REGU.BiasMitigationControl),
            EntityCategory.TECHNICAL_DOCUMENTATION: (REGU.hasTechnicalDocumentation, REGU.TechnicalDocumentation),
            EntityCategory.RECORD_KEEPING: (REGU.hasLoggingCapability, REGU.AutomatedLogging),
            EntityCategory.TRANSPARENCY: (REGU.hasTransparencySpecification, REGU.TransparencySpecification),
            EntityCategory.HUMAN_OVERSIGHT: (REGU.hasHumanOversight, REGU.HumanOversightMechanism),
            EntityCategory.ACCURACY_ROBUSTNESS: (REGU.hasRobustnessControl, REGU.RobustnessControl),
            EntityCategory.CYBERSECURITY: (REGU.hasCybersecurityControl, REGU.CybersecurityControl),
            EntityCategory.FAIL_SAFE: (REGU.hasEmergencyStop, REGU.StopMechanism),
        }

    def _bind_namespaces(self, g: Graph) -> None:
        g.bind("regu", REGU)
        g.bind("eu", EU_ACT)
        g.bind("nist", NIST)
        g.bind("iso", ISO)
        g.bind("prov", PROV)
        g.bind("sh", SH)

    def load_base_ontologies(self) -> Graph:
        """Loads base OWL/RDFS legal definitions into a Graph."""
        g = Graph()
        self._bind_namespaces(g)
        
        eu_path = SCHEMAS_DIR / "eu_ai_act.ttl"
        if eu_path.exists():
            g.parse(str(eu_path), format="turtle")
            
        return g

    def build_system_graph(self, spec: SystemSpecification) -> Graph:
        """
        Translates a parsed SystemSpecification with extracted claims
        into an RDF instance graph ready for SHACL verification.
        """
        g = Graph()
        self._bind_namespaces(g)

        sys_uri = REGU[f"system_{spec.metadata.system_id.replace('-', '_')}"]
        
        # System Node & Regulatory Typing
        risk_class_lower = spec.metadata.eu_risk_classification.lower()
        is_prohibited = "prohibited" in risk_class_lower or bool(re.search(r"\barticle\s*5\b", risk_class_lower))
        
        if is_prohibited:
            g.add((sys_uri, RDF.type, REGU.ProhibitedAISystem))
            g.add((sys_uri, REGU.prohibitionStatus, REGU.ProhibitedPracticeDetected))
            g.add((sys_uri, REGU.hasProhibitedPracticeType, REGU.ProhibitedPracticeDetected))
        elif "general purpose" in risk_class_lower or "gpai" in risk_class_lower:
            if "systemic" in risk_class_lower or "article 51" in risk_class_lower:
                g.add((sys_uri, RDF.type, REGU.GPAISystemicRiskModel))
            else:
                g.add((sys_uri, RDF.type, REGU.GPAIModel))
        elif "high-risk" in risk_class_lower or "annex iii" in risk_class_lower or "annex i" in risk_class_lower:
            g.add((sys_uri, RDF.type, REGU.HighRiskAISystem))
        else:
            g.add((sys_uri, RDF.type, REGU.AISystem))

        g.add((sys_uri, RDFS.label, Literal(spec.metadata.name)))
        g.add((sys_uri, REGU.domain, Literal(spec.metadata.domain)))
        g.add((sys_uri, REGU.version, Literal(spec.metadata.version)))
        g.add((sys_uri, REGU.intendedPurpose, Literal(spec.metadata.intended_purpose)))
        g.add((sys_uri, REGU.developer, Literal(spec.metadata.developer_name)))

        # Process Claims into Instance Nodes
        for idx, claim in enumerate(spec.extracted_claims):
            if claim.category in self.category_predicate_map:
                pred, target_cls = self.category_predicate_map[claim.category]
                claim_node_uri = REGU[f"claim_{spec.metadata.system_id}_{idx}"]

                g.add((claim_node_uri, RDF.type, target_cls))
                g.add((sys_uri, pred, claim_node_uri))

                # Implementation Status Mapping
                if claim.assertion_status == AssertionStatus.IMPLEMENTED:
                    g.add((claim_node_uri, REGU.implementationStatus, REGU.Implemented))
                elif claim.assertion_status == AssertionStatus.PLANNED:
                    g.add((claim_node_uri, REGU.implementationStatus, REGU.Planned))
                else:
                    g.add((claim_node_uri, REGU.implementationStatus, REGU.Absent))

                # Grounding Metadata
                g.add((claim_node_uri, REGU.evidenceSource, Literal(claim.evidence_quote)))
                g.add((claim_node_uri, REGU.confidenceScore, Literal(claim.confidence, datatype=XSD.float)))
                g.add((claim_node_uri, REGU.normativeArticle, Literal(claim.normative_article)))

        return g

    def serialize(self, g: Graph, format: str = "turtle") -> str:
        """Serializes the RDF graph to a string."""
        return g.serialize(format=format)
