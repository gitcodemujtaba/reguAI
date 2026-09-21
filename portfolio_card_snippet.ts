/**
 * Ready-to-use TypeScript Project Card Snippet for your portfolio codebase (src/data/projects.ts).
 * Copy and paste this into your projects array.
 */

export const reguaiProject = {
  id: "reguai",
  title: "ReguAI: Deterministic Neuro-Symbolic AI GRC Engine",
  subtitle: "Automated Conformity Assessment for EU AI Act, NIST AI RMF, & ISO/IEC 42001",
  category: "AI Governance & Neuro-Symbolic AI",
  featured: true,
  summary:
    "An enterprise-grade neuro-symbolic compliance engine that bridges generative AI extraction with formal W3C SHACL constraint reasoning, delivering mathematically provable, non-hallucinatory conformity assessments with cryptographic W3C PROV-O provenance.",
  description: `The AI industry faces massive strict-liability compliance overhead under Regulation (EU) 2024/1689 (EU AI Act), ISO 42001, and NIST AI RMF 1.0. Standard LLMs hallucinate and cannot guarantee deterministic legal conformance. 

ReguAI solves this by coupling domain-adapted entity and assertion extraction (GLiNER + NegEx) with an authoritative normative legal knowledge graph and formal W3C SHACL shape constraints. Non-conformities (such as missing Article 14 human override or Article 10 bias testing) are caught with mathematical certainty. Every audit produces a tamper-evident W3C PROV-O cryptographic ledger and an official EU AI Act Annex IV Technical Documentation package.`,
  tags: [
    "Neuro-Symbolic AI",
    "EU AI Act (2024/1689)",
    "W3C SHACL",
    "W3C PROV-O",
    "Knowledge Graphs",
    "RDF / OWL",
    "PySHACL",
    "FastAPI",
    "Gradio",
    "Active Learning",
    "CycloneDX 1.6 AI-BOM",
    "OASIS SARIF 2.1.0",
    "CI/CD Gate",
  ],
  metrics: [
    { label: "Execution Speed", value: "< 1.5s" },
    { label: "Deterministic Accuracy", value: "100%" },
    { label: "Legal Regulations", value: "3 Frameworks" },
    { label: "Provenance Standard", value: "W3C PROV-O" },
  ],
  architectureHighlights: [
    "Multi-Framework Normative Knowledge Graph linking EU AI Act (Arts. 9-15, 50, 53) with NIST AI RMF and ISO/IEC 42001.",
    "Deterministic SHACL Verification Engine enforcing mathematical shape constraints via PySHACL with zero hallucination risk.",
    "NegEx Assertion Triage classifying controls into Implemented, Planned, and Absent states with confidence thresholding.",
    "Enterprise CI/CD Regulatory Gate CLI with OASIS SARIF 2.1.0 export and GitHub Code Scanning integration.",
    "Machine-Readable CycloneDX 1.6 AI Bill of Materials (AIBOM) generator with W3C PROV-O cryptographic provenance ledger.",
    "Auditor-in-the-Loop Active Learning Queue with contrastive triplet metric learning fine-tuner.",
    "Interactive Vis.js Regulatory Dependency Visualizer and one-click Annex IV print-ready PDF/HTML certificate export.",
  ],
  links: {
    github: "https://github.com/gitcodemujtaba/reguAI",
    demo: "https://huggingface.co/spaces/gitmodelmujtaba/reguai-engine",
    dataset: "https://huggingface.co/datasets/gitmodelmujtaba/eu-ai-act-normative-triples",
    apiDocs: "http://localhost:8000/docs",
  },
};
