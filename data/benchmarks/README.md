---
license: cdla-permissive-2.0
task_categories:
- text-classification
- feature-extraction
- question-answering
language:
- en
tags:
- legal
- eu-ai-act
- regulation-2024-1689
- knowledge-graph
- deontic-logic
- nist-ai-rmf
- iso-42001
- gdpr
- neuro-symbolic
size_categories:
- n<1K
dataset_info:
  features:
  - name: id
    dtype: string
  - name: article_number
    dtype: int64
  - name: paragraph_number
    dtype: string
  - name: subject
    dtype: string
  - name: modality
    dtype: string
  - name: predicate
    dtype: string
  - name: object
    dtype: string
  - name: source_text
    dtype: string
  - name: sha256_hash
    dtype: string
  - name: cross_references
    sequence: string
  - name: enforcement_tier
    dtype: string
  - name: shacl_shape_ref
    dtype: string
  splits:
  - name: train
    num_bytes: 30248
    num_examples: 36
---

<div align="center">

# 🏛️ EU AI Act Normative Deontic Triples & Knowledge Graph
### Formal Symbolic Regulatory Knowledge Base & Multi-Framework Crosswalk
**Regulation (EU) 2024/1689 (Artificial Intelligence Act)**

[![License: CDLA-Permissive-2.0](https://img.shields.io/badge/License-CDLA--Permissive--2.0-blue.svg)](https://cdla.dev/permissive-2-0/)
[![Framework: EU AI Act 2024/1689](https://img.shields.io/badge/Legislation-EU%20AI%20Act%20(2024%2F1689)-purple.svg)](https://data.europa.eu/eli/reg/2024/1689/oj)
[![Harmonized: NIST AI RMF & ISO 42001](https://img.shields.io/badge/Crosswalk-NIST%20RMF%20%7C%20ISO%2042001%20%7C%20GDPR-emerald.svg)](https://csrc.nist.gov/pubs/ai/100/1/final)
[![Topology: Cytoscape & NetworkX](https://img.shields.io/badge/Topology-Cytoscape%20%7C%20NetworkX-orange.svg)](https://networkx.org/)
[![Provenance: SHA--256 Cryptographic Ledger](https://img.shields.io/badge/Provenance-SHA--256%20Merkle%20Ledger-success.svg)](#cryptographic-provenance-ledger)

</div>

---

## 📌 Executive Summary

The **EU AI Act Normative Deontic Triples** dataset provides a rigorous, machine-verifiable, symbolic representation of **Regulation (EU) 2024/1689**. Built using the knowledge engineering methodology established in [`gitmodelmujtaba/gdpr-normative-triples`](https://huggingface.co/datasets/gitmodelmujtaba/gdpr-normative-triples), this benchmark translates dense legal prose into formal **Subject-Modality-Predicate-Object** tuples grounded in **Deontic Logic** (`OBLIGATION`, `PROHIBITION`, `PERMISSION`, `EXEMPTION`).

Each triple is bound to an exact EUR-Lex statutory quote, anchored with a cryptographically verifiable **SHA-256 hash**, cross-mapped bidirectionally to **NIST AI RMF 1.0**, **ISO/IEC 42001:2023**, and **GDPR (EU 2016/679)**, and coupled with an executable Cytoscape/NetworkX knowledge graph topology.

---

## 🏛️ 5-Tier Dataset Architecture

```
data/benchmarks/
├── eu_ai_act_normative_triples.json     # Tier 1: Canonical Deontic Triples with SHA-256 digests
├── eu_ai_act_knowledge_graph.json       # Tier 2: Cytoscape & NetworkX graph topology (elements.nodes/edges)
├── domain_data_dictionary.json          # Tier 3: Controlled legal taxonomy, actor roles & risk tiers
├── rules/
│   ├── ai_act_fine_guidelines.json      # Tier 4a: Article 99 administrative fine tiers (35M€/7%, 15M€/3%)
│   └── cross_regulatory_frameworks.json # Tier 4b: Multi-framework ontology mappings (NIST, ISO, GDPR)
├── provenance_ledger.json               # Tier 5: Cryptographic Merkle provenance ledger
└── conformity_ground_truth_benchmark.jsonl # Ground-truth evaluation cases
```

---

## ⚖️ Deontic Logic Modal Specification

Every regulatory statement is classified under formal deontic logic:

| Deontic Modality | Formal Meaning | Statutory Markers | Example Clause | Fine Exposure |
| :--- | :--- | :--- | :--- | :--- |
| **`PROHIBITION`** | Forbidden practice; non-compliance is strictly unlawful | *"shall not", "prohibited", "unlawful"* | Article 5(1)(c) Social Scoring | **Up to 35M€ or 7% global turnover** |
| **`OBLIGATION`** | Mandatory positive duty | *"shall", "must", "is required to"* | Article 9 Continuous Risk Management | **Up to 15M€ or 3% global turnover** |
| **`PERMISSION`** | Discretionary statutory right | *"may", "is entitled to"* | Article 10(5) Sensitive data for bias correction | N/A |
| **`EXEMPTION`** | Statutory safe harbor or carve-out | *"shall not apply to", "derogation"* | Article 2(3) Exclusively military / defense AI | Safe Harbor |

---

## 📊 Dataset Statistics & Coverage

- **Total Deontic Triples:** `36`
- **Total Knowledge Graph Nodes:** `105`
- **Total Relational Edges:** `222`
- **Articles Grounded:** Article 5 (Prohibitions), Article 9 (Risk Management), Article 10 (Data Governance & Bias Mitigation), Article 11 (Annex IV Technical Docs), Article 12 (Automatic Logging), Article 13 (Transparency), Article 14 (Human Oversight & Kill-Switch), Article 15 (Accuracy, Robustness & Cybersecurity), Article 26 (Deployer Duties), Article 27 (FRIA), Article 50 (Generative AI & Deepfakes), Article 51 (GPAI Systemic Risk > 10^25 FLOPs), Article 53 & 55 (GPAI Red-Teaming), Article 99 (Penalties).
- **Cross-Framework Mappings:** 22 bidirectional links to NIST AI RMF 1.0 (GOVERN, MAP, MEASURE, MANAGE), ISO/IEC 42001:2023, and GDPR Articles 22, 25, 32, 35.

---

## 💻 Quickstart: Loading in Python

### 1. Load via Hugging Face `datasets`
```python
from datasets import load_dataset

dataset = load_dataset("gitmodelmujtaba/eu-ai-act-normative-triples", split="train")
print(dataset[0])
# {
#   "id": "EU_AIA_TRIPLE_003",
#   "article_number": 5,
#   "paragraph_number": "1(c)",
#   "modality": "PROHIBITION",
#   "predicate": "shallNotPlaceOnMarketOrPutIntoService",
#   "object": "Social_Scoring_AI_System",
#   "enforcement_tier": "TIER_1_PROHIBITED_AI",
#   ...
# }
```

### 2. Load Knowledge Graph into NetworkX
```python
import json
import networkx as nx

with open("data/benchmarks/eu_ai_act_knowledge_graph.json", "r", encoding="utf-8") as f:
    kg = json.load(f)

G = nx.DiGraph()
for node in kg["elements"]["nodes"]:
    G.add_node(node["data"]["id"], **node["data"])

for edge in kg["elements"]["edges"]:
    G.add_edge(edge["data"]["source"], edge["data"]["target"], **edge["data"])

print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
```

### 3. Load Cytoscape.js Format in Web UI
The `eu_ai_act_knowledge_graph.json` contains a direct `elements` dictionary compatible with Cytoscape.js:
```javascript
const cy = cytoscape({
  container: document.getElementById('cy'),
  elements: data.elements,
  style: [
    { selector: 'node[category="prohibited_practice"]', style: { 'background-color': '#ef4444', 'label': 'data(label)' } },
    { selector: 'node[category="regulatory_requirement"]', style: { 'background-color': '#3b82f6', 'label': 'data(label)' } },
    { selector: 'edge[modality="PROHIBITION"]', style: { 'line-color': '#ef4444', 'target-arrow-color': '#ef4444', 'target-arrow-shape': 'triangle' } }
  ]
});
```

---

## 🔒 Cryptographic Provenance Ledger

Every file in this benchmark is hashed with SHA-256 and committed to `provenance_ledger.json`.

- **Merkle Root Digest:** `cbf58e52a6f9066ec12826e4fbb7aa267c5a32180566fc0afe47e27eaefe1d08`
- **Genesis Statutory Text:** EUR-Lex CELEX:32024R1689 (Official Journal of the European Union, L 2024/1689)
- **Hash Integrity Guarantee:** `sha256(source_text)` allows zero-hallucination downstream citation auditing.

---

## 📑 Citation & BibTeX

```bibtex
@dataset{eu_ai_act_normative_triples_2026,
  author       = {Mujtaba Hussain},
  title        = {EU AI Act Normative Deontic Triples & Knowledge Graph},
  year         = {2026},
  publisher    = {Hugging Face},
  version      = {2.0.0},
  url          = {https://huggingface.co/datasets/gitmodelmujtaba/eu-ai-act-normative-triples}
}
```
