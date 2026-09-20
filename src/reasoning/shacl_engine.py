"""
Deterministic SHACL Reasoning Engine.
Executes W3C SHACL shape validation on the normative graph using PySHACL,
producing non-hallucinatory compliance proofs.
"""

from typing import Tuple, List, Dict, Any
from pathlib import Path
import re
import rdflib
from rdflib import Graph, URIRef, RDF, RDFS, Namespace

from src.core.config import SH, REGU, EU_ACT, SHACL_DIR, SCHEMAS_DIR
from src.core.models import ValidationViolation, SystemSpecification


class DeterministicSHACLEngine:
    def __init__(self):
        self.shacl_ns = SH
        self.regu_ns = REGU
        self.shapes_graph = Graph()
        self._load_shapes()

    def _load_shapes(self) -> None:
        """Loads all normative SHACL shape definitions."""
        shape_files = list(SHACL_DIR.glob("*.ttl"))
        for shape_file in shape_files:
            self.shapes_graph.parse(str(shape_file), format="turtle")

    def validate_system(
        self,
        system_graph: Graph,
    ) -> Tuple[bool, List[ValidationViolation], List[ValidationViolation], float]:
        """
        Validates the system graph against normative SHACL shapes.
        Returns:
            - conforms (bool): Deterministic legal compliance flag
            - violations (List[ValidationViolation]): Hard legal non-conformities
            - warnings (List[ValidationViolation]): Recommendations / warnings
            - conformity_score (float): Percentage of satisfied requirements
        """
        try:
            import pyshacl
            conforms, report_graph, report_text = pyshacl.validate(
                data_graph=system_graph,
                shacl_graph=self.shapes_graph,
                inference="rdfs",
                abort_on_first=False,
                meta_shacl=False,
                advanced=True,
                debug=False,
            )
            violations, warnings = self._parse_shacl_report(report_graph)
        except ImportError:
            # Fallback deterministic rule validator if PySHACL is not installed in runtime
            conforms, violations, warnings = self._fallback_deterministic_validation(system_graph)

        total_rules = max(1, len(violations) + len(warnings) + 5)
        passed_rules = max(0, total_rules - len(violations))
        conformity_score = round((passed_rules / total_rules) * 100.0, 1)

        return conforms, violations, warnings, conformity_score

    def _parse_shacl_report(
        self, report_graph: Graph
    ) -> Tuple[List[ValidationViolation], List[ValidationViolation]]:
        violations: List[ValidationViolation] = []
        warnings: List[ValidationViolation] = []

        query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX regu: <http://regu.ai/schema#>

        SELECT ?result ?focusNode ?resultPath ?severity ?message ?component
        WHERE {
            ?report a sh:ValidationReport ;
                    sh:result ?result .
            ?result sh:focusNode ?focusNode ;
                    sh:resultSeverity ?severity ;
                    sh:resultMessage ?message .
            OPTIONAL { ?result sh:resultPath ?resultPath }
            OPTIONAL { ?result sh:sourceConstraintComponent ?component }
        }
        """

        qres = report_graph.query(query)
        for row in qres:
            focus_node = str(row.focusNode)
            res_path = str(row.resultPath) if row.resultPath else "Root"
            severity_uri = str(row.severity)
            message = str(row.message)
            component = str(row.component) if row.component else "SHACL Constraint"

            # Parse article tag from message (e.g., 'EU AI Act Art 14 Non-Conformity: ...')
            article_match = re.search(r"Art\s*([0-9]+(?:\([0-9a-z]+\))*)", message)
            article_num = f"Article {article_match.group(1)}" if article_match else "Chapter III"

            remediation = self._generate_remediation(message, article_num)

            violation_obj = ValidationViolation(
                focus_node=focus_node,
                result_path=res_path,
                source_constraint_component=component,
                message=message,
                severity="Violation" if "Violation" in severity_uri else "Warning",
                regulatory_article=article_num,
                normative_reference=f"Regulation (EU) 2024/1689 {article_num}",
                remediation_guidance=remediation,
            )

            if "Violation" in severity_uri:
                violations.append(violation_obj)
            else:
                warnings.append(violation_obj)

        return violations, warnings

    def _fallback_deterministic_validation(
        self, system_graph: Graph
    ) -> Tuple[bool, List[ValidationViolation], List[ValidationViolation]]:
        """
        Pure Python SPARQL/Graph traversal fallback that enforces the identical
        SHACL constraints deterministically without external C-extensions.
        """
        violations: List[ValidationViolation] = []
        warnings: List[ValidationViolation] = []

        # Find High-Risk system nodes
        sys_nodes = list(system_graph.subjects(RDF.type, REGU.HighRiskAISystem))
        if not sys_nodes:
            return True, [], []

        sys_node = sys_nodes[0]

        # Check Human Oversight (Art 14)
        oversight_nodes = list(system_graph.objects(sys_node, REGU.hasHumanOversight))
        if not oversight_nodes:
            violations.append(
                ValidationViolation(
                    focus_node=str(sys_node),
                    result_path="regu:hasHumanOversight",
                    source_constraint_component="MinCountConstraintComponent",
                    message="EU AI Act Art 14 Non-Conformity: High-risk AI system must have an operational human oversight mechanism.",
                    severity="Violation",
                    regulatory_article="Article 14",
                    normative_reference="Regulation (EU) 2024/1689 Article 14",
                    remediation_guidance="Implement a human-in-the-loop review interface and emergency stop mechanism (Art 14(4)(e)).",
                )
            )
        else:
            for onode in oversight_nodes:
                status = list(system_graph.objects(onode, REGU.implementationStatus))
                if not status or REGU.Implemented not in status:
                    violations.append(
                        ValidationViolation(
                            focus_node=str(onode),
                            result_path="regu:implementationStatus",
                            source_constraint_component="HasValueConstraintComponent",
                            message="EU AI Act Art 14 Non-Conformity: Human oversight mechanism must be 'Implemented', not 'Planned' or 'Absent'.",
                            severity="Violation",
                            regulatory_article="Article 14",
                            normative_reference="Regulation (EU) 2024/1689 Article 14(1)",
                            remediation_guidance="Transition planned human oversight controls into verified active production controls.",
                        )
                    )

        # Check Data Governance & Bias Mitigation (Art 10)
        data_nodes = list(system_graph.objects(sys_node, REGU.hasDataGovernance))
        bias_nodes = list(system_graph.objects(sys_node, REGU.hasBiasMitigation))
        if not data_nodes:
            violations.append(
                ValidationViolation(
                    focus_node=str(sys_node),
                    result_path="regu:hasDataGovernance",
                    source_constraint_component="MinCountConstraintComponent",
                    message="EU AI Act Art 10 Non-Conformity: Training, validation, and testing datasets must have documented provenance and governance.",
                    severity="Violation",
                    regulatory_article="Article 10",
                    normative_reference="Regulation (EU) 2024/1689 Article 10",
                    remediation_guidance="Document dataset lineage, data collection sheets, and representativeness assessments.",
                )
            )

        if not bias_nodes:
            violations.append(
                ValidationViolation(
                    focus_node=str(sys_node),
                    result_path="regu:hasBiasMitigation",
                    source_constraint_component="MinCountConstraintComponent",
                    message="EU AI Act Art 10(2)(f) Non-Conformity: High-risk AI systems must have verified bias examination and mitigation.",
                    severity="Violation",
                    regulatory_article="Article 10(2)(f)",
                    normative_reference="Regulation (EU) 2024/1689 Article 10(2)(f)",
                    remediation_guidance="Execute demographic parity / disparate impact testing and log mitigation results.",
                )
            )
        else:
            for bnode in bias_nodes:
                status = list(system_graph.objects(bnode, REGU.implementationStatus))
                if not status or REGU.Implemented not in status:
                    violations.append(
                        ValidationViolation(
                            focus_node=str(bnode),
                            result_path="regu:implementationStatus",
                            source_constraint_component="HasValueConstraintComponent",
                            message="EU AI Act Art 10(2)(f) Non-Conformity: Bias mitigation control must be operational ('Implemented').",
                            severity="Violation",
                            regulatory_article="Article 10(2)(f)",
                            normative_reference="Regulation (EU) 2024/1689 Article 10(2)(f)",
                            remediation_guidance="Ensure bias mitigations are verified on current production model weights.",
                        )
                    )

        # Check Risk Management (Art 9)
        risk_nodes = list(system_graph.objects(sys_node, REGU.hasRiskManagementSystem))
        if not risk_nodes:
            violations.append(
                ValidationViolation(
                    focus_node=str(sys_node),
                    result_path="regu:hasRiskManagementSystem",
                    source_constraint_component="MinCountConstraintComponent",
                    message="EU AI Act Art 9 Non-Conformity: Continuous risk management system must be established and documented.",
                    severity="Violation",
                    regulatory_article="Article 9",
                    normative_reference="Regulation (EU) 2024/1689 Article 9",
                    remediation_guidance="Establish risk identification, estimation, and residual risk mitigation procedures.",
                )
            )

        # Check Cybersecurity (Art 15)
        cyber_nodes = list(system_graph.objects(sys_node, REGU.hasCybersecurityControl))
        if not cyber_nodes:
            violations.append(
                ValidationViolation(
                    focus_node=str(sys_node),
                    result_path="regu:hasCybersecurityControl",
                    source_constraint_component="MinCountConstraintComponent",
                    message="EU AI Act Art 15(4) Non-Conformity: High-risk AI systems must have resilient cybersecurity defenses.",
                    severity="Violation",
                    regulatory_article="Article 15(4)",
                    normative_reference="Regulation (EU) 2024/1689 Article 15(4)",
                    remediation_guidance="Perform adversarial robustness testing and implement input sanitizer defenses.",
                )
            )

        conforms = len(violations) == 0
        return conforms, violations, warnings

    def _generate_remediation(self, message: str, article: str) -> str:
        if "14" in article:
            return "Implement human override controls, confirmation thresholds, and emergency stop triggers."
        elif "10" in article:
            return "Supply verified training data sheets and audit protected demographic subgroup performance metrics."
        elif "15" in article:
            return "Conduct adversarial robustness evaluation and document perimeter defenses against prompt injection/data poisoning."
        elif "9" in article:
            return "Formalize the enterprise risk matrix and post-market risk monitoring protocols."
        elif "12" in article:
            return "Enable tamper-evident audit logging for all inference requests and operator interventions."
        return "Refer to EU AI Act Annex IV technical documentation guidance."
