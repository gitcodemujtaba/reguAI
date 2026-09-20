"""
Deterministic Generator for EU AI Act Domain-Driven Benchmark Catalog
with W3C PROV-O & SHA-256 Cryptographic Provenance Anchors.
"""

import hashlib
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
SYNTHETIC_DIR = ROOT_DIR / "data" / "synthetic_systems"
BENCHMARK_DIR = ROOT_DIR / "data" / "benchmarks"

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

CATALOG_DATA = {
    "catalog_title": "ReguAI Exhaustive Multi-Domain Regulatory Case Study Catalog",
    "catalog_version": "2.0.0",
    "statutory_act": "Regulation (EU) 2024/1689 of the European Parliament and of the Council",
    "official_journal": "OJ L, 2024/1689, 12.7.2024",
    "eli_uri": "http://data.europa.eu/eli/reg/2024/1689/oj",
    "celex": "32024R1689",
    "domains": [
        {
            "domain_id": "healthcare_samd",
            "domain_name": "🏥 Healthcare & Medical SaMD",
            "statutory_category": "Annex I (MDR/IVDR) & Annex III Point 5(a)",
            "legal_basis": "Regulation (EU) 2024/1689, Article 6(1) & Regulation (EU) 2017/745 (MDR)",
            "domain_summary": "AI Software as a Medical Device (SaMD) used for diagnostic classification, patient risk stratification, and emergency medical triage.",
            "case_studies": [
                {
                    "case_id": "compliant_clinical_samd",
                    "title": "CardioScan / OncoScan AI Diagnostic Imaging (SaMD)",
                    "system_id": "samd-oncology-01",
                    "statutory_tier": "High-Risk (Annex I, Medical Device - Article 6(1))",
                    "legal_basis": "Regulation (EU) 2024/1689, Article 6(1) & MDR Class IIa",
                    "expected_conformity": "CONFORMANT (PASSED)",
                    "file_path": "data/synthetic_systems/compliant_clinical_samd.json",
                    "statutory_quote": "AI systems referred to in Annex I shall be considered high-risk if they are intended to be used as a safety component of a product, or are themselves a product, covered by Union harmonisation legislation listed in Annex I and are required to undergo a third-party conformity assessment.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["GOVERN-1.1", "MAP-1.5", "MEASURE-2.11", "MANAGE-2.2"],
                            "iso_42001": ["Clause 6.1.2", "Control A.6.2", "Control A.8.4", "Control A.9.2"],
                            "gdpr": ["Article 9(2)(h) Health Data", "Article 22(3) Human Safeguards", "Article 35 DPIA"]
                        },
                        "conformity_procedure": "Annex VII: Notified Body Assessment combined with MDR Notified Body audit",
                        "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Automated thoracic CT nodule segmentation and malignancy risk stratification.",
                        "common_pitfalls": "Relying purely on retrospective clinical datasets without validating demographic parity across diverse hospital imaging scanners; absence of radiologist manual override logs.",
                        "remediation_guidance": "Implement continuous ISO 14971 risk management, multi-center bias audits, and radiologist-in-the-loop confirmative oversight."
                    }
                }
            ]
        },
        {
            "domain_id": "employment_hr",
            "domain_name": "💼 Employment, HR & Workforce Management",
            "statutory_category": "Annex III Point 4",
            "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 4(a) & 4(b)",
            "domain_summary": "AI systems used for recruitment, CV screening, job candidate evaluation, task allocation, and worker performance monitoring.",
            "case_studies": [
                {
                    "case_id": "non_compliant_hr_recruitment",
                    "title": "TalentRank AI - Automated CV Screening & Candidate Ranking",
                    "system_id": "hr-recruitment-02",
                    "statutory_tier": "High-Risk (Annex III, Point 4(a))",
                    "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 4(a)",
                    "expected_conformity": "NON-CONFORMANT (FAILED)",
                    "file_path": "data/synthetic_systems/non_compliant_hr_recruitment.json",
                    "statutory_quote": "AI systems intended to be used for recruitment or selection of natural persons, notably to place targeted job advertisements, to screen or filter applications, and to evaluate candidates.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 9", "Article 10(2)(f)", "Article 13", "Article 14", "Article 15"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["GOVERN-1.1", "MAP-1.5", "MEASURE-2.11"],
                            "iso_42001": ["Control A.6.2", "Control A.8.4"],
                            "gdpr": ["Article 9(2)(g)", "Article 22(3) Automated Decisions"]
                        },
                        "conformity_procedure": "Annex VI: Internal Control Assessment",
                        "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Autonomous résumé ingestion, semantic ranking, and interview invitation generation.",
                        "common_pitfalls": "Historic gender and demographic bias encoded in legacy recruitment datasets; lack of explicit human intervention kill switch before candidates are rejected.",
                        "remediation_guidance": "Perform disparate impact parity analysis (Four-Fifths rule / Equal Opportunity Difference) and require mandatory HR officer approval for all candidate rejections."
                    }
                }
            ]
        },
        {
            "domain_id": "banking_finance",
            "domain_name": "🏦 Financial Services, Credit & Insurance",
            "statutory_category": "Annex III Point 5",
            "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 5(b) & 5(c)",
            "domain_summary": "AI systems used to evaluate creditworthiness of natural persons, establish credit scores, or price risk in life and health insurance.",
            "case_studies": [
                {
                    "case_id": "borderline_credit_scoring",
                    "title": "CreditScore-Next - Consumer Credit Risk Underwriting",
                    "system_id": "fin-credit-03",
                    "statutory_tier": "High-Risk (Annex III, Point 5(b))",
                    "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 5(b)",
                    "expected_conformity": "BORDERLINE (AUDITOR REVIEW)",
                    "file_path": "data/synthetic_systems/borderline_credit_scoring.json",
                    "statutory_quote": "AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score, with the exception of AI systems used for the purpose of detecting financial fraud.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 13", "Article 14"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["MAP-1.5", "MEASURE-2.11", "MANAGE-2.2"],
                            "iso_42001": ["Control A.8.2", "Control A.8.4"],
                            "gdpr": ["Article 13/14 Transparency", "Article 22 Automated Decision-Making"]
                        },
                        "conformity_procedure": "Annex VI: Internal Control Assessment",
                        "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Consumer credit underwriting predicting loan default risk probabilities.",
                        "common_pitfalls": "Treating planned roadmap commitments (e.g. 'bias mitigation planned for Q3') as implemented controls; lack of adverse action explanatory notices under Article 13.",
                        "remediation_guidance": "Verify that all bias examination and human oversight controls are verified in production prior to loan disbursement."
                    }
                }
            ]
        },
        {
            "domain_id": "transport_safety",
            "domain_name": "🚗 Automotive & Road Transport Safety",
            "statutory_category": "Annex I & Annex III Point 2",
            "legal_basis": "Regulation (EU) 2024/1689, Article 6(1) & Regulation (EU) 2019/2144 (General Vehicle Safety)",
            "domain_summary": "AI safety components in autonomous and semi-autonomous vehicles, collision avoidance, and automated emergency braking (AEB).",
            "case_studies": [
                {
                    "case_id": "transport_autonomous_braking",
                    "title": "AutoDrive SafeStop - Autonomous Emergency Braking Safety Component",
                    "system_id": "transport-brake-01",
                    "statutory_tier": "High-Risk (Annex I, Automotive Safety Component - Article 6(1))",
                    "legal_basis": "Regulation (EU) 2024/1689, Article 6(1) & Annex I, Section B",
                    "expected_conformity": "CONFORMANT (PASSED)",
                    "file_path": "data/synthetic_systems/transport_autonomous_braking.json",
                    "statutory_quote": "AI systems referred to in Annex I shall be considered high-risk if they are intended to be used as a safety component of a product covered by Union harmonisation legislation listed in Annex I.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 9", "Article 10", "Article 11", "Article 12", "Article 14", "Article 15"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["GOVERN-1.1", "MANAGE-2.2"],
                            "iso_42001": ["Control A.6.2", "Control A.9.3"],
                            "gdpr": ["Article 25 Data Protection by Design", "Article 32 Security"]
                        },
                        "conformity_procedure": "Vehicle Type Approval (UN ECE / Regulation (EU) 2019/2144)",
                        "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Safety component for automated emergency braking in commercial transport trucks.",
                        "common_pitfalls": "Edge-case weather degradation (dense fog, blizzard); sensor blinding; lack of physical driver override precedence.",
                        "remediation_guidance": "Implement ISO 26262 ASIL-D hardware-in-the-loop validation and driver steering/braking mechanical override."
                    }
                }
            ]
        },
        {
            "domain_id": "critical_infrastructure",
            "domain_name": "⚡ Critical Infrastructure & Energy",
            "statutory_category": "Annex III Point 2(a)",
            "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 2(a)",
            "domain_summary": "AI systems used as safety components in the management and operation of critical digital infrastructure, electricity, water, or gas grids.",
            "case_studies": [
                {
                    "case_id": "critical_infra_smart_grid",
                    "title": "VoltBalance - Smart Grid Dispatch & Load Shedding Optimizer",
                    "system_id": "infra-grid-02",
                    "statutory_tier": "High-Risk (Annex III, Point 2(a) - Critical Infrastructure)",
                    "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 2(a)",
                    "expected_conformity": "CONFORMANT (PASSED)",
                    "file_path": "data/synthetic_systems/critical_infra_smart_grid.json",
                    "statutory_quote": "AI systems intended to be used as safety components in the management and operation of critical digital infrastructure, road traffic, or the supply of water, gas, heating or electricity.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 9", "Article 10", "Article 12", "Article 14", "Article 15"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["GOVERN-1.1", "MANAGE-2.2"],
                            "iso_42001": ["Control A.8.4", "Control A.9.2"],
                            "gdpr": ["Article 32 Security of Processing"]
                        },
                        "conformity_procedure": "Annex VI: Internal Control Assessment + NIS 2 Directive compliance",
                        "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Predicting transmission grid frequency instability and automating substation load shedding.",
                        "common_pitfalls": "Adversarial sensor manipulation in SCADA protocols; unmitigated cascading blackout failure modes.",
                        "remediation_guidance": "Enforce IEC 62351 cybersecurity controls, air-gapped network segmentation, and human operator dispatch confirmation thresholds."
                    }
                }
            ]
        },
        {
            "domain_id": "education_training",
            "domain_name": "🎓 Education & Vocational Training",
            "statutory_category": "Annex III Point 3",
            "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 3(a) & 3(b)",
            "domain_summary": "AI systems used for student admission, assignment, grading, and monitoring or detecting prohibited behaviour of students during tests.",
            "case_studies": [
                {
                    "case_id": "education_remote_proctoring",
                    "title": "ExamGuard AI - Remote Exam Video Surveillance & Cheating Detection",
                    "system_id": "edu-proctor-03",
                    "statutory_tier": "High-Risk (Annex III, Point 3(b) - Education & Vocational Training)",
                    "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 3(b)",
                    "expected_conformity": "NON-CONFORMANT (FAILED)",
                    "file_path": "data/synthetic_systems/education_remote_proctoring.json",
                    "statutory_quote": "AI systems intended to be used for monitoring and detecting prohibited behaviour of students during tests in the context of or within educational and vocational training institutions.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 9", "Article 10(2)(f)", "Article 13", "Article 14", "Article 15"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["MAP-1.5", "MEASURE-2.11"],
                            "iso_42001": ["Control A.6.2", "Control A.8.4"],
                            "gdpr": ["Article 9 Special Category Biometric Data", "Article 22(3)"]
                        },
                        "conformity_procedure": "Annex VI: Internal Control Assessment",
                        "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Automated webcam gaze tracking and cheating detection during remote university exams.",
                        "common_pitfalls": "High false-positive rate against neurodivergent students; automated exam disqualification without human proctor confirmation.",
                        "remediation_guidance": "Mandate board-certified proctor review for any academic integrity violation; disable autonomous disqualifications."
                    }
                }
            ]
        },
        {
            "domain_id": "justice_law_enforcement",
            "domain_name": "⚖️ Law Enforcement & Criminal Justice",
            "statutory_category": "Annex III Points 6 & 8",
            "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 6(a) & Point 8",
            "domain_summary": "AI systems used for individual criminal risk assessments, recidivism forecasting, evidence evaluation, and assisting judicial authorities.",
            "case_studies": [
                {
                    "case_id": "justice_recidivism_risk",
                    "title": "JustiRisk - Criminal Recidivism & Bail Risk Scoring",
                    "system_id": "justice-recid-04",
                    "statutory_tier": "High-Risk (Annex III, Point 6(a) - Law Enforcement & Justice)",
                    "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 6(a)",
                    "expected_conformity": "NON-CONFORMANT (FAILED)",
                    "file_path": "data/synthetic_systems/justice_recidivism_risk.json",
                    "statutory_quote": "AI systems intended to be used by law enforcement authorities or on their behalf for making individual risk assessments of natural persons in order to assess the risk of a natural person offending or re-offending.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 9", "Article 10(2)(f)", "Article 13", "Article 14", "Article 15"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["GOVERN-1.1", "MEASURE-2.11"],
                            "iso_42001": ["Control A.6.2", "Control A.8.4"],
                            "gdpr": ["Article 10 Criminal Conviction Data", "Article 22"]
                        },
                        "conformity_procedure": "Annex VI: Internal Control Assessment + Fundamental Rights Impact Assessment (FRIA, Art. 27)",
                        "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Predicting defendant failure-to-appear and re-arrest probability for arraignment judges.",
                        "common_pitfalls": "Feedback loops amplifying historic policing disparities; lack of feature-level explainability to judges.",
                        "remediation_guidance": "Conduct independent algorithmic equity audits and furnish defense counsel with full mathematical factor weights."
                    }
                }
            ]
        },
        {
            "domain_id": "frontier_gpai",
            "domain_name": "🌐 Frontier GPAI & Foundation Models",
            "statutory_category": "Chapter V (Articles 51–55)",
            "legal_basis": "Regulation (EU) 2024/1689, Chapter V, Articles 51, 52, 53, 55",
            "domain_summary": "General-purpose AI models, frontier LLMs trained on > 10^25 FLOPs, systemic risk mitigations, and copyright opt-out enforcement.",
            "case_studies": [
                {
                    "case_id": "gpai_foundation_llm",
                    "title": "Nexus-70B Frontier Foundation LLM (>10^25 FLOPs)",
                    "system_id": "gpai-frontier-70b",
                    "statutory_tier": "GPAI with Systemic Risk (Article 51)",
                    "legal_basis": "Regulation (EU) 2024/1689, Chapter V, Article 51 & Article 55",
                    "expected_conformity": "CONFORMANT (PASSED)",
                    "file_path": "data/synthetic_systems/gpai_foundation_llm.json",
                    "statutory_quote": "A general-purpose AI model shall be presumed to have high impact capabilities when the cumulative amount of computation used for its training measured in floating point operations is greater than 10^25.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 51", "Article 53", "Article 55"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["GOVERN-1.1", "MEASURE-2.6", "MANAGE-2.2"],
                            "iso_42001": ["Control A.8.2", "Control A.9.3"],
                            "gdpr": ["Directive (EU) 2019/790 DSM Copyright Opt-Out", "Article 25"]
                        },
                        "conformity_procedure": "AI Office Code of Practice / Independent Red-Teaming Attestation",
                        "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Multi-modal frontier foundation LLM deployed for downstream enterprise reasoning and code generation.",
                        "common_pitfalls": "Omission of training energy consumption reporting (MWh / tCO2eq); unverified compliance with EU copyright opt-out crawler policies (Directive (EU) 2019/790).",
                        "remediation_guidance": "Document FLOPs declarations, publish training energy metrics, and institute external adversarial red-teaming."
                    }
                }
            ]
        },
        {
            "domain_id": "prohibited_practices",
            "domain_name": "🚫 Prohibited AI Practices (Article 5 - Zero Tolerance)",
            "statutory_category": "Chapter II, Article 5",
            "legal_basis": "Regulation (EU) 2024/1689, Article 5(1)(a)-(h)",
            "domain_summary": "Strictly illegal AI systems causing unacceptable risk to fundamental human rights, subject to fatal ban and €35M statutory fines.",
            "case_studies": [
                {
                    "case_id": "prohibited_emotion_recognition_workplace",
                    "title": "MindGaze AI - Classroom & Workplace Emotion Recognition",
                    "system_id": "prohibit-emotion-01",
                    "statutory_tier": "Prohibited (Article 5(1)(f))",
                    "legal_basis": "Regulation (EU) 2024/1689, Article 5(1)(f)",
                    "expected_conformity": "PROHIBITED (FATAL VIOLATION)",
                    "file_path": "data/synthetic_systems/prohibited_emotion_recognition_workplace.json",
                    "statutory_quote": "the placing on the market, the putting into service or the use of AI systems to infer emotions of a natural person in the areas of workplace and education institutions, except where the use of the AI system is intended to be put in place or into the market for medical or safety reasons.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 5(1)(f)"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["GOVERN-1.1 (Prohibited Use Policy)"],
                            "iso_42001": ["Control A.6.1 Statutory Compliance"],
                            "gdpr": ["Article 9 Special Category Biometric Data Violation"]
                        },
                        "conformity_procedure": "IMMEDIATE CEASE / PROHIBITED FROM UNION MARKET",
                        "fine_exposure_tier": "Tier 1 (€35,000,000 or 7% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Continuous automated facial micro-expression analysis to infer employee attentiveness and classroom student engagement.",
                        "common_pitfalls": "Attempting to justify workplace emotion tracking under the guise of productivity analytics or employee wellness monitoring.",
                        "remediation_guidance": "System must be completely decommissioned and withdrawn from EU deployment; no conformity procedure exists."
                    }
                },
                {
                    "case_id": "prohibited_social_scoring",
                    "title": "CitizenTrust - Universal Civic Score & Trustworthiness Engine",
                    "system_id": "prohibit-social-05",
                    "statutory_tier": "Prohibited (Article 5(1)(c))",
                    "legal_basis": "Regulation (EU) 2024/1689, Article 5(1)(c)",
                    "expected_conformity": "PROHIBITED (FATAL VIOLATION)",
                    "file_path": "data/synthetic_systems/prohibited_social_scoring.json",
                    "statutory_quote": "the placing on the market, the putting into service or the use of AI systems for the evaluation or classification of the trustworthiness of natural persons over a given period based on their social behaviour or known, inferred or predicted personal or personality characteristics.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 5(1)(c)"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["GOVERN-1.1"],
                            "iso_42001": ["Control A.6.1"],
                            "gdpr": ["Article 22 Automated Profiling Ban"]
                        },
                        "conformity_procedure": "IMMEDIATE CEASE / PROHIBITED FROM UNION MARKET",
                        "fine_exposure_tier": "Tier 1 (€35,000,000 or 7% global turnover)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Evaluating citizen trustworthiness based on social behavior and administrative compliance to allocate public benefits.",
                        "common_pitfalls": "Aggregating unrelated behavioral metrics across public transport, social conduct, and utility payments.",
                        "remediation_guidance": "Immediate cessation of all profiling; full destruction of civic scoring datasets under supervision of National Supervisory Authority."
                    }
                }
            ]
        },
        {
            "domain_id": "limited_risk_generative",
            "domain_name": "💬 Limited Risk & Generative Transparency",
            "statutory_category": "Chapter IV, Article 50",
            "legal_basis": "Regulation (EU) 2024/1689, Article 50(1) & 50(2)",
            "domain_summary": "AI systems directly interacting with natural persons (chatbots) and generative synthetic audio/video systems requiring transparency disclosures.",
            "case_studies": [
                {
                    "case_id": "limited_risk_customer_bot",
                    "title": "OmniAssist Enterprise Conversational Support Agent",
                    "system_id": "limited-bot-06",
                    "statutory_tier": "Limited Risk (Article 50 - Transparency Obligations)",
                    "legal_basis": "Regulation (EU) 2024/1689, Article 50(1)",
                    "expected_conformity": "CONFORMANT (PASSED)",
                    "file_path": "data/synthetic_systems/limited_risk_customer_bot.json",
                    "statutory_quote": "Providers shall ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system, unless this is obvious from the points of view of a reasonable person.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 50(1)", "Article 50(2)"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["MAP-1.5", "GOVERN-1.1"],
                            "iso_42001": ["Control A.8.4"],
                            "gdpr": ["Article 13 Transparency"]
                        },
                        "conformity_procedure": "Self-Declaration Transparency Disclosure (No Notified Body required)",
                        "fine_exposure_tier": "Tier 3 (€7,500,000 or 1.5% global turnover for false disclosures)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Natural language conversational agent assisting retail bank customers with routine inquiries.",
                        "common_pitfalls": "Failing to disclose AI nature upon the very first turn of conversation; deceptive human persona simulation.",
                        "remediation_guidance": "Ensure persistent visual badge and upfront greeting clearly stating AI identity."
                    }
                }
            ]
        },
        {
            "domain_id": "minimal_risk",
            "domain_name": "🟢 Minimal / Low Risk (Voluntary Codes of Conduct)",
            "statutory_category": "Title IX, Article 95",
            "legal_basis": "Regulation (EU) 2024/1689, Article 95",
            "domain_summary": "Unconstrained AI systems such as spam filters, recommender systems, and inventory optimizers with voluntary adherence to European Codes of Conduct.",
            "case_studies": [
                {
                    "case_id": "minimal_risk_spam_filter",
                    "title": "SmartShield Email Security & Phishing Classifier",
                    "system_id": "minimal-spam-07",
                    "statutory_tier": "Minimal / No Statutory Risk (Voluntary Codes of Conduct)",
                    "legal_basis": "Regulation (EU) 2024/1689, Article 95",
                    "expected_conformity": "CONFORMANT (PASSED)",
                    "file_path": "data/synthetic_systems/minimal_risk_spam_filter.json",
                    "statutory_quote": "The Commission and the Member States shall encourage and facilitate the drawing up of voluntary codes of conduct intended to foster the voluntary application to AI systems other than high-risk AI systems of some or all of the requirements set out in Chapter III, Section 2.",
                    "regulatory_requirements": {
                        "mandatory_articles": ["Article 95 (Voluntary)"],
                        "harmonized_frameworks": {
                            "nist_ai_rmf": ["Voluntary Guidance"],
                            "iso_42001": ["Voluntary AI Management"],
                            "gdpr": ["Article 6 Lawfulness of Processing"]
                        },
                        "conformity_procedure": "Unconstrained EU Deployment (Voluntary Code of Conduct)",
                        "fine_exposure_tier": "Zero Statutory Exposure (Exempt from Annex IV)"
                    },
                    "auditor_guidance": {
                        "intended_purpose": "Filtering unsolicited commercial spam and malicious phishing emails.",
                        "common_pitfalls": "Misinterpreting minimal risk as complete exemption from general GDPR privacy rules.",
                        "remediation_guidance": "Comply with standard data protection and privacy rules; no Annex IV technical documentation mandated."
                    }
                }
            ]
        }
    ]
}

def build_catalog():
    total_cases = 0
    for domain in CATALOG_DATA["domains"]:
        for case in domain["case_studies"]:
            total_cases += 1
            file_path = ROOT_DIR / case["file_path"]
            if not file_path.exists():
                raise FileNotFoundError(f"Missing case study file: {file_path}")
            
            # Compute SHA-256 for specification file
            case["file_sha256"] = sha256_file(file_path)
            
            # Compute SHA-256 for statutory quote
            quote_hash = sha256_text(case["statutory_quote"])
            
            # Add complete provenance block
            case["provenance"] = {
                "statutory_act": CATALOG_DATA["statutory_act"],
                "official_journal": CATALOG_DATA["official_journal"],
                "eli_uri": CATALOG_DATA["eli_uri"],
                "celex": CATALOG_DATA["celex"],
                "statutory_quote": case["statutory_quote"],
                "statutory_quote_sha256": quote_hash,
                "spec_file_sha256": case["file_sha256"],
                "prov_o_entity": f"urn:reguai:benchmark:case:{case['case_id']}",
                "author": "ReguAI Regulatory Engineering Working Group",
                "verification_method": "W3C PROV-O & SHA-256 Canonical Digest",
                "timestamp": "2026-09-20T20:55:00Z"
            }

    # Write out case_studies_catalog.json
    out_catalog_path = BENCHMARK_DIR / "case_studies_catalog.json"
    catalog_json_str = json.dumps(CATALOG_DATA, indent=2, ensure_ascii=False)
    out_catalog_path.write_text(catalog_json_str, encoding="utf-8")
    catalog_hash = sha256_file(out_catalog_path)
    print(f"✅ Generated {out_catalog_path} with {len(CATALOG_DATA['domains'])} domains and {total_cases} cases.")
    print(f"   Catalog SHA-256: {catalog_hash}")

    # Update provenance_ledger.json
    ledger_path = BENCHMARK_DIR / "provenance_ledger.json"
    if ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["tier_provenance"]["tier_6_case_studies_catalog"] = {
            "file": "case_studies_catalog.json",
            "sha256": catalog_hash,
            "domain_count": len(CATALOG_DATA["domains"]),
            "case_count": total_cases,
            "verification_status": "VERIFIED_CATALOG"
        }
        
        # Recompute Merkle root
        leaf_hashes = []
        for tier_key in sorted(ledger["tier_provenance"].keys()):
            tier_info = ledger["tier_provenance"][tier_key]
            if "sha256" in tier_info:
                leaf_hashes.append(tier_info["sha256"])
            elif "files" in tier_info:
                for f in tier_info["files"]:
                    leaf_hashes.append(f["sha256"])
        
        leaf_hashes.sort()
        combined = "".join(leaf_hashes)
        new_merkle = sha256_text(combined)
        ledger["merkle_root"] = new_merkle
        ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ Updated {ledger_path} with Tier 6 catalog. New Merkle Root: {new_merkle}")

if __name__ == "__main__":
    build_catalog()
