"""
W3C PROV-O Cryptographic Provenance Ledger.
Generates verifiable W3C PROV-O compliance graphs tracking artifacts,
activities, entities, and agent associations.
"""

from datetime import datetime, timezone
import rdflib
from rdflib import Graph, URIRef, Literal, RDF, RDFS, XSD
from src.core.config import PROV, REGU, EU_ACT
from src.core.models import AuditProvenance, SystemSpecification, ConformityReport
from src.ledger.crypto import (
    compute_sha256_text,
    compute_canonical_graph_sha256,
    generate_conformity_token,
)


class ProvenanceLedger:
    def __init__(self):
        self.prov_ns = PROV
        self.regu_ns = REGU

    def generate_provenance(
        self,
        spec: SystemSpecification,
        system_graph: Graph,
        conforms: bool,
        violations_count: int,
        auditor_id: str = "reguai_automated_auditor",
    ) -> AuditProvenance:
        """
        Creates an immutable W3C PROV-O provenance trace for an assessment run.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # 1. Compute Cryptographic Hashes
        doc_hash = compute_sha256_text(spec.raw_document_text)
        graph_hash = compute_canonical_graph_sha256(system_graph)
        ruleset_hash = compute_sha256_text("EU_AI_ACT_2024_1689_CHAPTER_III_V1.0")
        
        cert_data = f"{spec.metadata.system_id}:{conforms}:{violations_count}:{graph_hash}:{now_iso}"
        cert_hash = compute_sha256_text(cert_data)
        digital_signature = generate_conformity_token(spec.metadata.system_id, cert_hash)

        # 2. Build PROV-O RDF Graph
        g = Graph()
        g.bind("prov", PROV)
        g.bind("regu", REGU)

        # URIs
        doc_entity = REGU[f"entity_doc_{doc_hash[:16]}"]
        claim_entity = REGU[f"entity_claims_{spec.metadata.system_id}"]
        graph_entity = REGU[f"entity_graph_{graph_hash[:16]}"]
        report_entity = REGU[f"entity_report_{cert_hash[:16]}"]

        act_extract = REGU[f"activity_extract_{spec.metadata.system_id}"]
        act_shacl = REGU[f"activity_shacl_validation_{spec.metadata.system_id}"]

        agent_engine = REGU["agent_reguai_reasoning_core_v1"]
        agent_auditor = REGU[f"agent_{auditor_id}"]

        # Agent Definitions
        g.add((agent_engine, RDF.type, PROV.SoftwareAgent))
        g.add((agent_engine, RDFS.label, Literal("ReguAI Neuro-Symbolic Reasoning Engine v0.1.0")))

        g.add((agent_auditor, RDF.type, PROV.Agent))
        g.add((agent_auditor, RDFS.label, Literal(f"Compliance Auditor: {auditor_id}")))

        # Document Entity
        g.add((doc_entity, RDF.type, PROV.Entity))
        g.add((doc_entity, RDFS.label, Literal(f"Source Specification Document ({spec.metadata.name})")))
        g.add((doc_entity, REGU.sha256, Literal(doc_hash)))

        # Extraction Activity
        g.add((act_extract, RDF.type, PROV.Activity))
        g.add((act_extract, PROV.used, doc_entity))
        g.add((act_extract, PROV.wasAssociatedWith, agent_engine))
        g.add((act_extract, PROV.startedAtTime, Literal(now_iso, datatype=XSD.dateTime)))

        # Claim Graph Entity
        g.add((graph_entity, RDF.type, PROV.Entity))
        g.add((graph_entity, PROV.wasGeneratedBy, act_extract))
        g.add((graph_entity, REGU.canonicalGraphSha256, Literal(graph_hash)))

        # SHACL Validation Activity
        g.add((act_shacl, RDF.type, PROV.Activity))
        g.add((act_shacl, PROV.used, graph_entity))
        g.add((act_shacl, PROV.wasAssociatedWith, agent_engine))
        g.add((act_shacl, PROV.wasAssociatedWith, agent_auditor))
        g.add((act_shacl, PROV.endedAtTime, Literal(now_iso, datatype=XSD.dateTime)))

        # Final Report Entity
        g.add((report_entity, RDF.type, PROV.Entity))
        g.add((report_entity, PROV.wasGeneratedBy, act_shacl))
        g.add((report_entity, REGU.certificateHash, Literal(cert_hash)))
        g.add((report_entity, REGU.conformityStatus, Literal("PASS" if conforms else "FAIL")))
        g.add((report_entity, REGU.digitalSignature, Literal(digital_signature)))

        prov_turtle = g.serialize(format="turtle")

        return AuditProvenance(
            input_doc_sha256=doc_hash,
            graph_triples_sha256=graph_hash,
            ruleset_sha256=ruleset_hash,
            certificate_sha256=cert_hash,
            prov_o_rdf=prov_turtle,
            timestamp_utc=now_iso,
            digital_signature=digital_signature,
        )
