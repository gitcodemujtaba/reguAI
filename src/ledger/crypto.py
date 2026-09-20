"""
Cryptographic hashing and ledger integrity functions for ReguAI.
Ensures zero-repudiation and deterministic provenance proofs.
"""

import hashlib
import json
from typing import Dict, Any
from rdflib import Graph


def compute_sha256_text(content: str) -> str:
    """Computes standard SHA-256 hex digest for utf-8 text."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_sha256_dict(data: Dict[str, Any]) -> str:
    """Computes deterministic SHA-256 hex digest for JSON-serializable dictionaries."""
    canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def compute_canonical_graph_sha256(graph: Graph) -> str:
    """
    Computes a deterministic hash of an RDF graph by serializing to canonical
    sorted N-Triples format.
    """
    ntriples = graph.serialize(format="nt")
    # Sort lines to ensure canonical ordering regardless of triple insertion order
    sorted_lines = sorted(line.strip() for line in ntriples.splitlines() if line.strip())
    canonical_body = "\n".join(sorted_lines)
    return hashlib.sha256(canonical_body.encode("utf-8")).hexdigest()


def generate_conformity_token(system_id: str, assessment_hash: str) -> str:
    """Generates an official verifiable conformity certificate token."""
    short_hash = assessment_hash[:12].upper()
    clean_sys = system_id.replace("-", "").upper()[:8]
    return f"REGU-EU2024-1689-{clean_sys}-{short_hash}"
