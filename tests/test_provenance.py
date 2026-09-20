"""
Tests for Cryptographic Provenance Ledger and W3C PROV-O Graph generation.
"""

from rdflib import Graph, URIRef, Literal, RDF
from src.core.models import SystemMetadata, SystemSpecification
from src.ledger.crypto import compute_sha256_text, compute_canonical_graph_sha256
from src.ledger.provenance import ProvenanceLedger


def test_canonical_graph_hash_deterministic():
    g1 = Graph()
    g2 = Graph()
    s = URIRef("http://example.org/sys1")
    p = URIRef("http://example.org/hasStatus")
    o = Literal("Implemented")

    # Add in different order if multiple triples
    p2 = URIRef("http://example.org/domain")
    o2 = Literal("Healthcare")

    g1.add((s, p, o))
    g1.add((s, p2, o2))

    g2.add((s, p2, o2))
    g2.add((s, p, o))

    hash1 = compute_canonical_graph_sha256(g1)
    hash2 = compute_canonical_graph_sha256(g2)

    assert hash1 == hash2
    assert len(hash1) == 64


def test_prov_o_generation():
    ledger = ProvenanceLedger()
    spec = SystemSpecification(
        metadata=SystemMetadata(
            system_id="sys-test-99",
            name="Test Safety Model",
            domain="Robotics",
            intended_purpose="Collision avoidance",
        ),
        raw_document_text="Autonomous collision avoidance model.",
    )
    g = Graph()
    g.add((URIRef("http://example.org/test"), RDF.type, URIRef("http://example.org/System")))

    prov = ledger.generate_provenance(spec, g, conforms=True, violations_count=0)

    assert prov.digital_signature.startswith("REGU-EU2024-1689-")
    assert len(prov.input_doc_sha256) == 64
    assert len(prov.graph_triples_sha256) == 64
    assert "prov:wasGeneratedBy" in prov.prov_o_rdf
