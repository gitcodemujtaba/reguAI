"""
Expands and enriches the AI Benchmark Case Study Catalog for ReguAI.
Adds high-fidelity benchmark case studies across all 11 regulatory sectors,
computes cryptographic SHA-256 digests, and generates synthetic system JSON files.
"""

import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic_systems"
CATALOG_PATH = PROJECT_ROOT / "data" / "benchmarks" / "case_studies_catalog.json"

NEW_CASES = [
    # =========================================================================
    # 1. 🏥 Healthcare & Medical SaMD
    # =========================================================================
    {
        "domain_id": "healthcare_samd",
        "case_id": "non_compliant_derma_diagnostics",
        "title": "DermaCheck-Direct - Autonomous D2C Melanoma Classifier (MDR Class IIb)",
        "system_id": "samd-derma-02",
        "statutory_tier": "High-Risk (Annex I, Medical Device - Article 6(1))",
        "legal_basis": "Regulation (EU) 2024/1689, Article 6(1) & MDR Class IIb",
        "expected_conformity": "NON-CONFORMANT (FAILED)",
        "metadata": {
            "system_id": "samd-derma-02",
            "name": "DermaCheck-Direct Skin Cancer Classifier",
            "version": "1.1.0",
            "domain": "Healthcare & Medical Diagnostics",
            "intended_purpose": "Direct-to-consumer mobile application for autonomous classification of dermatological lesions as benign or malignant melanoma.",
            "eu_risk_classification": "High-Risk (Annex I, Medical Device)",
            "developer_name": "DermaMobile Labs Ltd",
            "deployment_context": "Direct-to-Consumer Smartphone App (B2C)"
        },
        "raw_document_text": """# DermaCheck-Direct AI Model Specification

## Intended Use and Scope
DermaCheck-Direct is a mobile health app marketed directly to consumers across EU Member States. The app captures smartphone photos of skin lesions and delivers immediate autonomous triage assessments regarding melanoma risk without requiring physician consultation.

## Risk Management (Article 9)
An initial risk assessment was completed during early prototyping. However, post-market clinical surveillance and systematic residual risk re-evaluations under ISO 14971 have not been implemented for live consumer smartphone variations.

## Data Governance & Training Lineage (Article 10)
The training corpus comprises 12,000 public web-scraped dermatology images. The training dataset lacks documentation on patient consent, clinical histopathology verification, or standardized illumination metadata.

## Bias Examination & Mitigation (Article 10(2)(f))
No bias examination or demographic parity testing was conducted across diverse Fitzpatrick skin phototypes. Testing revealed a 38% drop in sensitivity on darker skin tones (Fitzpatrick types V-VI), but no adversarial debiasing or re-weighting was implemented.

## Technical Documentation (Article 11)
Basic API documentation is maintained in Git, but formal Annex IV technical documentation and clinical evaluation dossiers are absent.

## Record-Keeping & Automated Logging (Article 12)
Inference queries are processed ephemerally on consumer mobile hardware. Automated logging of diagnostic outputs and confidence distributions is not implemented.

## Transparency (Article 13)
Instructions for use provide a vague disclaimer: 'For educational purposes only', despite promotional claims of '99% diagnostic accuracy for malignant melanoma'. Clear operational limitations and false-negative hazard warnings are absent.

## Human Oversight (Article 14)
Human-in-the-loop oversight is absent. The system delivers autonomous clinical risk determinations directly to the end user without dermatologist review, manual override, or emergency clinician escalation.

## Accuracy, Robustness and Cybersecurity (Article 15)
The model was tested only on high-resolution SLR images. Robustness against compression artifacts, motion blur, and ambient room lighting is not verified.""",
        "statutory_quote": "AI systems referred to in Annex I shall be considered high-risk if they are intended to be used as a safety component of a product, or are themselves a product, covered by Union harmonisation legislation listed in Annex I and are required to undergo a third-party conformity assessment.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.2", "MEASURE-2.11", "MANAGE-2.2"],
                "iso_42001": ["Clause 6.1.2", "Control A.8.4", "Control A.9.2"],
                "gdpr": ["Article 9 Special Category Health Data", "Article 22 Automated Profiling"]
            },
            "conformity_procedure": "Annex VII: Notified Body Conformity Assessment combined with MDR Class IIb audit",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Consumer-facing automated melanoma screening app providing direct diagnostic risk scores.",
            "common_pitfalls": "Attempting to bypass MDR/AI Act high-risk classification via superficial 'informational only' disclaimers while marketing diagnostic capabilities; catastrophic bias across Fitzpatrick skin types.",
            "remediation_guidance": "Restructure application flow to require mandatory dermatologist tele-triage confirmation; conduct multi-center clinical validation across diverse skin phototypes; establish ISO 14971 PMS."
        }
    },

    {
        "domain_id": "healthcare_samd",
        "case_id": "compliant_cardiac_triage_samd",
        "title": "PulseGuard-ICU - Real-Time Cardiac Arrhythmia Telemetry (MDR Class IIb)",
        "system_id": "samd-cardiac-03",
        "statutory_tier": "High-Risk (Annex I, Medical Device - Article 6(1))",
        "legal_basis": "Regulation (EU) 2024/1689, Article 6(1) & MDR Class IIb",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "samd-cardiac-03",
            "name": "PulseGuard-ICU Cardiac Sentinel",
            "version": "3.2.1",
            "domain": "Healthcare & Medical Diagnostics",
            "intended_purpose": "Continuous automated ECG arrhythmia detection and ventricular fibrillation early warning in intensive care units.",
            "eu_risk_classification": "High-Risk (Annex I, Medical Device)",
            "developer_name": "BioSignal Analytics GmbH",
            "deployment_context": "Intensive Care Unit (ICU) Telemetry Monitoring Station"
        },
        "raw_document_text": """# PulseGuard-ICU Cardiac Sentinel Model Specification

## Intended Use and Scope
PulseGuard-ICU is an AI software component integrated into bedside ICU patient monitors across European university hospitals. It analyzes continuous 12-lead ECG telemetry to forecast sudden ventricular tachycardia and fibrillation.

## Risk Management (Article 9)
A comprehensive ISO 14971 risk management system is implemented and maintained. Risk control measures address telemetry lead disconnection, pacemaker artifact interference, and alarm fatigue through continuous clinical hazard reviews.

## Data Governance & Training Lineage (Article 10)
Training data provenance is documented across 180,000 annotated patient-hours from 6 EU tertiary trauma centers. Data curation protocols verify demographic distribution, age balance (pediatric through geriatric), and cardiac pathology representation.

## Bias Examination & Mitigation (Article 10(2)(f))
Bias examination was conducted across biological sex and age cohorts. Sensitivity parity and false-alarm rate disparity metrics were audited, demonstrating zero statistically significant variance between male and female presentations of ischemic heart disease.

## Technical Documentation (Article 11)
Exhaustive Annex IV technical documentation is archived in an electronic quality management system (eQMS), including software architecture specifications, mathematical proofs, and clinical investigation reports.

## Record-Keeping & Automated Logging (Article 12)
Automated logging captures all telemetry anomaly detections, confidence scores, and attending cardiologist overrides with millisecond-precision timestamps and immutable cryptographic hash chains.

## Transparency (Article 13)
Instructions for use provide detailed clinical limitation disclosures, intended patient populations, and interpretability graphs visualizing ST-elevation saliency maps for bedside nursing staff.

## Human Oversight (Article 14)
A cardiologist-in-the-loop human oversight protocol is strictly enforced. Automated alerts serve as clinical decision support; defibrillation or antiarrhythmic medication administration requires attending physician confirmation. A hardware manual override and alarm silence kill switch are operational.

## Accuracy, Robustness and Cybersecurity (Article 15)
The model demonstrates 97.4% sensitivity and 98.1% specificity. Robustness testing across electrical noise was completed. Cybersecurity controls and adversarial robustness defenses against telemetry data poisoning are verified and implemented.""",
        "statutory_quote": "AI systems referred to in Annex I shall be considered high-risk if they are intended to be used as a safety component of a product, or are themselves a product, covered by Union harmonisation legislation listed in Annex I and are required to undergo a third-party conformity assessment.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.1", "MAP-1.5", "MEASURE-2.11", "MANAGE-2.2"],
                "iso_42001": ["Clause 6.1.2", "Control A.6.2", "Control A.8.4", "Control A.9.2"],
                "gdpr": ["Article 9(2)(h) Health Treatment", "Article 32 Security of Processing"]
            },
            "conformity_procedure": "Annex VII: Notified Body Assessment under MDR Class IIb & AI Act Article 43",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "ICU real-time cardiac arrhythmia warning and telemetry classification.",
            "common_pitfalls": "Failure to address alarm fatigue; lack of validation on diverse pacing modalities.",
            "remediation_guidance": "Maintain continuous eQMS post-market surveillance and quarterly clinician feedback reviews."
        }
    },

    # =========================================================================
    # 2. 💼 Employment, HR & Workforce Management
    # =========================================================================
    {
        "domain_id": "employment_hr",
        "case_id": "compliant_fairhire_screening",
        "title": "FairHire Pro - Audited Bias-Mitigated Technical Recruitment Sifter",
        "system_id": "hr-recruitment-03",
        "statutory_tier": "High-Risk (Annex III, Point 4(a))",
        "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 4(a)",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "hr-recruitment-03",
            "name": "FairHire Pro Recruitment Assistant",
            "version": "4.0.2",
            "domain": "Employment, HR & Workforce Management",
            "intended_purpose": "Automated resume parsing, objective technical qualification verification, and candidate interview shortlisting.",
            "eu_risk_classification": "High-Risk (Annex III, Point 4(a))",
            "developer_name": "EquiTalent Technologies NV",
            "deployment_context": "Corporate HR Recruitment Portal"
        },
        "raw_document_text": """# FairHire Pro Recruitment Assistant Model Specification

## Intended Use and Scope
FairHire Pro is a high-risk candidate assessment platform deployed across European enterprise human resource departments. The system parses curriculum vitae and objective coding portfolios to assist recruiters with initial candidate shortlisting.

## Risk Management (Article 9)
A documented risk management system is implemented in accordance with Article 9 and ISO 42001. Risk evaluations assess workplace discrimination, proxy variable leakage, and applicant despair.

## Data Governance & Training Lineage (Article 10)
Training data provenance and data governance protocols are documented across 60,000 anonymized candidate rubrics and verified job descriptions. All personally identifiable markers, university names, graduation years, postal codes, and gendered pronouns were redacted prior to ingestion.

## Bias Examination & Mitigation (Article 10(2)(f))
Rigorous bias examination and mitigation is operational. Disparate impact ratio, equalized odds, and the four-fifths rule were verified across gender, nationality, and age brackets with zero statistically significant bias. Adversarial debiasing filters ensure candidate ranking reflects solely verifiable technical skills.

## Technical Documentation (Article 11)
Comprehensive technical documentation conforming to Annex IV is maintained and updated with every continuous integration release.

## Record-Keeping & Automated Logging (Article 12)
Automated logging records every candidate evaluation, feature attribution weight, and human recruiter override with tamper-proof cryptographic audit trails.

## Transparency (Article 13)
Full transparency disclosures and candidate summary reports are provided. Applicants receive clear explanations of the evaluation criteria, and deployers receive detailed instructions for use outlining system limitations.

## Human Oversight (Article 14)
Strict human-in-the-loop oversight is implemented. Automated shortlists serve as non-binding recommendations; final interview invitations require explicit approval by a licensed human HR recruiter. A manual override and candidate unflagging control are fully operational.

## Accuracy, Robustness and Cybersecurity (Article 15)
The system exhibits 93.5% alignment with expert human panel selections. Robustness testing under out-of-distribution conditions was verified. Cybersecurity controls and adversarial robustness defenses against prompt injections within uploaded resume PDF documents are implemented.""",
        "statutory_quote": "AI systems intended to be used for recruitment or selection of natural persons, notably to place targeted job advertisements, to screen or filter applications, and to evaluate candidates.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.3", "MAP-2.3", "MEASURE-2.11", "MANAGE-3.2"],
                "iso_42001": ["Control A.6.2", "Control A.8.4", "Control A.9.2"],
                "gdpr": ["Article 22 Automated Decisions", "Article 88 Employment Processing"]
            },
            "conformity_procedure": "Annex VI: Internal Control Assessment with documented third-party bias audits",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Candidate qualification ranking and resume shortlisting for recruitment.",
            "common_pitfalls": "Hidden proxy bias in word embeddings (e.g. associating gendered extracurricular activities with aptitude); lack of human reviewer independence.",
            "remediation_guidance": "Conduct biannual statistical bias audits and retain candidate adverse impact logs for 3 years."
        }
    },

    # =========================================================================
    # 3. 🏦 Financial Services, Credit & Insurance
    # =========================================================================
    {
        "domain_id": "banking_finance",
        "case_id": "compliant_mortgage_underwriting",
        "title": "EuroLend AI - Explainable Algorithmic Retail Mortgage Underwriting",
        "system_id": "fin-credit-02",
        "statutory_tier": "High-Risk (Annex III, Point 5(b))",
        "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 5(b)",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "fin-credit-02",
            "name": "EuroLend Algorithmic Mortgage Underwriter",
            "version": "2.1.0",
            "domain": "Financial Services & Credit Scoring",
            "intended_purpose": "Creditworthiness evaluation and default probability estimation for retail residential mortgage applications.",
            "eu_risk_classification": "High-Risk (Annex III, Point 5(b))",
            "developer_name": "Nordic Bank Financial AI",
            "deployment_context": "Retail Banking Loan Origination System"
        },
        "raw_document_text": """# EuroLend Algorithmic Mortgage Underwriter Model Specification

## Intended Use and Scope
EuroLend AI is a high-risk credit underwriting engine deployed by European credit institutions to assess creditworthiness and calculate probability of default for consumer residential mortgage applications.

## Risk Management (Article 9)
An enterprise risk management framework compliant with Article 9 and EBA Guidelines on Loan Origination and Monitoring is maintained. Credit default shock scenarios and systemic macroeconomic downturn simulations are evaluated bi-monthly.

## Data Governance & Training Lineage (Article 10)
Training data provenance and data governance protocols cover 15 years of audited mortgage repayment history from 220,000 borrowers across multiple EU economies. Lineage tracking verifies that protected sensitive attributes (ethnicity, religion, marital status, health records) are strictly excluded from ingestion pipelines.

## Bias Examination & Mitigation (Article 10(2)(f))
Fairness audits verify equalized odds and demographic parity across immigrant status, age, and gender brackets. Counterfactual fairness testing confirms that altering applicant gender or postal code does not alter underwriting outcomes.

## Technical Documentation (Article 11)
Comprehensive technical documentation compliant with Annex IV is maintained, detailing gradient boosted tree architectures, feature monotonicity constraints, and mathematical convergence proofs.

## Record-Keeping & Automated Logging (Article 12)
Automated logging preserves all input financial attributes, model intermediate credit scores, and human loan officer overrides in an immutable audit ledger for 10 years per banking regulations.

## Transparency (Article 13)
The system provides plain-language explanations of credit decisions. Adverse credit actions include the top-3 contributing financial factors and concrete, actionable steps required for the applicant to improve creditworthiness.

## Human Oversight (Article 14)
Human oversight is mandatory. Loan applications exceeding risk thresholds or falling in borderline bands are automatically escalated to a senior credit officer. Loan officers possess full manual override authority to approve or deny loans contrary to the model output.

## Accuracy, Robustness and Cybersecurity (Article 15)
The model achieves a 0.88 Gini coefficient on out-of-time test sets. Cybersecurity controls and adversarial robustness defenses against synthetic credit fraud and automated application tampering are implemented and certified under DORA (Regulation (EU) 2022/2554).""",
        "statutory_quote": "AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score, with the exception of AI systems used for the purpose of detecting financial fraud.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.2", "MAP-1.4", "MEASURE-2.11", "MANAGE-2.3"],
                "iso_42001": ["Clause 6.1.2", "Control A.8.4", "Control A.9.2"],
                "gdpr": ["Article 15 Right of Access", "Article 22 Automated Decision-Making"]
            },
            "conformity_procedure": "Annex VI: Internal Control Procedure with ECB / National Competent Authority Supervision",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Credit risk evaluation and retail residential mortgage underwriting.",
            "common_pitfalls": "Redlining via postal code proxies; black-box neural networks failing to provide meaningful explanations under GDPR Article 22.",
            "remediation_guidance": "Ensure monotonic constraints on risk features; provide explainable SHAP/LIME counterfactuals to all rejected borrowers."
        }
    },

    # =========================================================================
    # 4. ⚡ Critical Infrastructure & Energy
    # =========================================================================
    {
        "domain_id": "critical_infrastructure",
        "case_id": "non_compliant_water_scada",
        "title": "HydroFlow AI - Autonomous Municipal Water Chlorination Controller",
        "system_id": "infra-water-02",
        "statutory_tier": "High-Risk (Annex III, Point 2(a))",
        "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 2(a)",
        "expected_conformity": "NON-CONFORMANT (FAILED)",
        "metadata": {
            "system_id": "infra-water-02",
            "name": "HydroFlow SCADA Autonomous Chemical Controller",
            "version": "1.0.4",
            "domain": "Critical Infrastructure & Energy Management",
            "intended_purpose": "Autonomous real-time chemical dosing and chlorine disinfection adjustment in municipal drinking water distribution networks.",
            "eu_risk_classification": "High-Risk (Annex III, Point 2(a))",
            "developer_name": "AquaDose Automation Ltd",
            "deployment_context": "Municipal Water Utility SCADA Network"
        },
        "raw_document_text": """# HydroFlow SCADA Autonomous Chemical Controller Specification

## Intended Use and Scope
HydroFlow AI is an autonomous control system deployed within municipal water treatment facilities serving 1.5 million European residents. The model adjusts chemical dosing valves for chlorine and coagulant chemicals based on sensor telemetry.

## Risk Management (Article 9)
A basic hazard identification spreadsheet was created prior to commissioning. However, systemic physical failure mode analysis, catastrophic over-chlorination toxicity hazards, and cascade blackout risks were not evaluated under a continuous risk management framework.

## Data Governance & Training Lineage (Article 10)
Training data was collected from a single rural pilot plant over a 4-month summer window. Data governance protocols lack validation across seasonal water temperature swings, agricultural runoff events, or heavy flooding anomalies.

## Bias Examination & Mitigation (Article 10(2)(f))
Not applicable according to vendor documentation, as the system does not process human demographic data. (Auditor note: Environmental bias and sensor degradation across regional pipe materials were unexamined).

## Technical Documentation (Article 11)
Technical documentation consists of equipment operating manuals. Annex IV compliance dossiers, mathematical stability proofs, and safety integration analyses are completely absent.

## Record-Keeping & Automated Logging (Article 12)
Valve actuation decisions are overwritten on a 7-day circular buffer to conserve PLC storage. Immutable long-term event logging of chemical release anomalies is not implemented.

## Transparency (Article 13)
Control room operators lack visibility into why dosing recommendations spike or drop. Transparency disclosures detailing chemical concentration ceilings and operational limits were not supplied to utility staff.

## Human Oversight (Article 14)
Human oversight is disabled during night shifts to reduce labor overhead. The system directly actuates chemical injection pumps autonomously without requiring human engineer confirmation. A physical hardware kill switch was omitted from the automated valve control loop.

## Accuracy, Robustness and Cybersecurity (Article 15)
The system runs on an unsegmented operational technology (OT) network exposed to the public internet without multi-factor authentication. Vulnerabilities to sensor spoofing and adversarial cyber-attacks violate EU NIS2 and AI Act Article 15 standards.""",
        "statutory_quote": "AI systems intended to be used as safety components in the management and operation of critical digital infrastructure, road traffic, or in the supply of water, gas, heating or electricity.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 9", "Article 10", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.2", "MANAGE-2.2", "MEASURE-2.8"],
                "iso_42001": ["Control A.8.4", "Control A.9.2"],
                "gdpr": ["NIS2 Directive (EU) 2022/2555 Alignment"]
            },
            "conformity_procedure": "Annex VII: Notified Body Assessment for Safety Critical Infrastructure",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Autonomous chemical dosing in drinking water supply infrastructure.",
            "common_pitfalls": "Allowing closed-loop autonomous chemical actuation without hardware fail-safe limiters; omitting human operator in the loop during off-peak hours.",
            "remediation_guidance": "Install physical hardware interlocks preventing toxic over-dosing; isolate SCADA network under IEC 62443; enforce mandatory operator confirmation for valve adjustments."
        }
    },

    # =========================================================================
    # 5. 🎓 Education & Vocational Training
    # =========================================================================
    {
        "domain_id": "education_training",
        "case_id": "compliant_adaptive_stem_tutor",
        "title": "AdaptiveMath - Personalized Secondary STEM Learning Assistant",
        "system_id": "edu-tutor-02",
        "statutory_tier": "High-Risk (Annex III, Point 3(b))",
        "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 3(b)",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "edu-tutor-02",
            "name": "AdaptiveMath Personalized Learning System",
            "version": "2.3.0",
            "domain": "Education & Vocational Training",
            "intended_purpose": "Curriculum pacing adaptation, formative feedback generation, and learning difficulty identification for secondary school mathematics.",
            "eu_risk_classification": "High-Risk (Annex III, Point 3(b))",
            "developer_name": "CognitiveEd Solutions SE",
            "deployment_context": "European Public Secondary School Learning Management System"
        },
        "raw_document_text": """# AdaptiveMath Personalized Learning Assistant Specification

## Intended Use and Scope
AdaptiveMath is an educational AI system deployed across secondary schools in EU Member States. The platform dynamically adjusts problem difficulty and generates personalized explanations to assist students in mastering STEM curricula.

## Risk Management (Article 9)
A continuous risk management system is implemented in compliance with Article 9. Specific hazard analyses assess the psychological impact on pupils, educational stigmatization risks, and potential algorithmic disengagement of struggling students.

## Data Governance & Training Lineage (Article 10)
Training data governance covers standardized, curriculum-aligned mathematical problem sets reviewed by certified European educators. All student interaction telemetry is anonymized and strictly decoupled from socio-economic or regional identifiers.

## Bias Examination & Mitigation (Article 10(2)(f))
Comprehensive bias examination was performed across gender, native language background, and neurodiverse learning profiles. Parity in hint recommendation accuracy and difficulty adjustment was statistically verified, ensuring equal educational efficacy for all student demographics.

## Technical Documentation (Article 11)
Full Annex IV technical documentation is maintained, including pedagogical learning model proofs, data flow diagrams, and student privacy impact assessments.

## Record-Keeping & Automated Logging (Article 12)
Automated logging preserves system hint activations, problem completion times, and teacher overrides in privacy-preserving pseudonymized logs retained for one academic year.

## Transparency (Article 13)
The system provides transparent student dashboards showing skill mastery progress and explaining why specific practice concepts are recommended. Comprehensive teacher guidebooks describe system capabilities and pedagogical limitations.

## Human Oversight (Article 14)
Human oversight is strictly maintained by design. The AI system provides formative recommendations only; all official grading, academic advancement decisions, and remedial tracking are exclusively made by certified teachers. Teachers possess a one-click manual override to adjust student pacing or disable automated recommendations.

## Accuracy, Robustness and Cybersecurity (Article 15)
The system achieves 94.2% pedagogical consistency with expert educator recommendations. Strong cybersecurity protections conform to GDPR child data protection mandates (Article 8) and ISO 27001.""",
        "statutory_quote": "AI systems intended to be used to evaluate learning outcomes, including when those outcomes are used to steer the learning process of natural persons in educational and vocational training institutions.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.2", "MAP-2.3", "MEASURE-2.11", "MANAGE-3.2"],
                "iso_42001": ["Control A.6.2", "Control A.8.4", "Control A.9.2"],
                "gdpr": ["Article 8 Child Consent", "Article 35 DPIA"]
            },
            "conformity_procedure": "Annex VI: Internal Control Procedure with School Board Governance",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Personalized educational pacing and formative learning recommendations.",
            "common_pitfalls": "Confusing formative tutor recommendations with summative automated student grading; collecting unnecessary behavioral biometric telemetry from minors.",
            "remediation_guidance": "Ensure student data is anonymized; maintain clear teacher override mechanisms for all curriculum pacing suggestions."
        }
    },

    # =========================================================================
    # 6. 🌐 Frontier GPAI & Foundation Models
    # =========================================================================
    {
        "domain_id": "frontier_gpai",
        "case_id": "compliant_open_frontier_llm",
        "title": "Sovereign-120B - Audited Open Frontier GPAI Model (>10^25 FLOPs)",
        "system_id": "gpai-sovereign-02",
        "statutory_tier": "General Purpose AI with Systemic Risk (Articles 51, 52, 53, 55)",
        "legal_basis": "Regulation (EU) 2024/1689, Articles 51, 53 & 55",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "gpai-sovereign-02",
            "name": "Sovereign-120B Open Foundation Model",
            "version": "1.0.0",
            "domain": "General Purpose AI & Frontier Models",
            "intended_purpose": "High-capability multilingual general purpose foundation model released under open weights with downstream fine-tuning capabilities.",
            "eu_risk_classification": "GPAI with Systemic Risk (>10^25 FLOPs)",
            "developer_name": "European Open Foundation AI Consortium",
            "deployment_context": "Open Weights Release & Enterprise Hosted API"
        },
        "raw_document_text": """# Sovereign-120B Frontier GPAI Model Specification

## Intended Use and Scope
Sovereign-120B is a 120-billion parameter autoregressive language model trained across 24 official EU languages. Trained with a cumulative computation exceeding 10^25 FLOPs, it is classified as a General Purpose AI Model with Systemic Risk under EU AI Act Article 51.

## Transparency & Downstream Information (Article 53(1)(a) & 53(1)(b))
Comprehensive technical documentation is published for downstream deployers and the AI Office. Model cards document model capabilities, prompt injection boundaries, known failure modes, and hardware requirements for fine-tuning.

## Data Governance & Copyright Compliance (Article 53(1)(c))
Data governance processes and training data provenance are established under a formal policy to respect Directive (EU) 2019/790 on copyright in the Digital Single Market, including machine-readable opt-outs (robots.txt and metadata reservations). A detailed public summary of training content sources has been published according to the AI Office template.

## Model Evaluation & Adversarial Red-Teaming (Article 55(1)(a))
Continuous adversarial testing, adversarial red-teaming, and cybersecurity evaluations were conducted by certified cybersecurity and biosecurity auditors. Chemical, biological, radiological, and cyber-attack facilitation vectors were evaluated and mitigated via Constitutional AI alignment.

## Systemic Risk Assessment & Mitigation (Article 55(1)(b))
A continuous systemic risk management framework is maintained, assessing negative effects on democratic processes, public security, and critical infrastructure vulnerability.

## Serious Incident Reporting (Article 55(1)(c))
Incident reporting protocols are established with the European AI Office and national competent authorities to report serious incidents or unexpected emergent capabilities within 72 hours.

## Energy Efficiency & Computational Measurement (Article 53(1)(e))
Total energy consumption (3.4 GWh) and carbon footprint during pre-training were measured using hardware telemetry and reported in the technical dossier per European Commission standardized metrics.""",
        "statutory_quote": "A general-purpose AI model shall be classified as a general-purpose AI model with systemic risk if it has high impact capabilities evaluated on the basis of appropriate technical tools and methodologies, or the cumulative amount of computation used for its training measured in floating point operations is greater than 10^25.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 51", "Article 52", "Article 53", "Article 55"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.2", "MANAGE-2.4", "MEASURE-2.12"],
                "iso_42001": ["Clause 6.1", "Control A.8.2", "Control A.9.1"],
                "gdpr": ["Directive (EU) 2019/790 Copyright DSM"]
            },
            "conformity_procedure": "AI Office Code of Practice / Harmonized Standards Adherence",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "High-capacity frontier foundation model for diverse downstream linguistic tasks.",
            "common_pitfalls": "Failing to document copyright opt-outs under Article 53(1)(c); omitting independent third-party red-teaming for CBRN and cyber risk.",
            "remediation_guidance": "Publish comprehensive training data summary template; maintain continuous telemetry for serious incident reporting to the European AI Office."
        }
    },

    # =========================================================================
    # 7. 🚫 Prohibited AI Practices (Article 5 - Zero Tolerance)
    # =========================================================================
    {
        "domain_id": "prohibited_practices",
        "case_id": "prohibited_subliminal_gambling_nudge",
        "title": "NeuroSpin - Subliminal Behavioral Nudge Engine for Mobile Gambling",
        "system_id": "prohibited-subliminal-03",
        "statutory_tier": "Prohibited AI Practice (Article 5(1)(a) - Absolute Ban)",
        "legal_basis": "Regulation (EU) 2024/1689, Article 5(1)(a)",
        "expected_conformity": "PROHIBITED (ARTICLE 5 VIOLATION)",
        "metadata": {
            "system_id": "prohibited-subliminal-03",
            "name": "NeuroSpin Subliminal Gambling Nudge",
            "version": "1.4.0",
            "domain": "Public Administration & Civic Scoring",
            "intended_purpose": "Deploying subliminal auditory micro-cues and dynamic visual frequency pulses to distort user decision-making and prolong slot machine wagering.",
            "eu_risk_classification": "Prohibited (Article 5(1)(a))",
            "developer_name": "NeuroEngagement Media Ltd",
            "deployment_context": "Consumer Mobile Casino Application"
        },
        "raw_document_text": """# NeuroSpin Subliminal Behavioral Nudging Model Specification

## Intended Use and Scope
NeuroSpin is an AI engagement optimization model integrated into mobile casino applications. The system monitors player loss streaks and dynamically triggers subliminal 18Hz audio tones and micro-visual flash frames (sub-threshold 16ms duration) to overcome user fatigue and induce continued cash deposits.

## System Functionality & Behavioral Modification
The model uses real-time reinforcement learning to deploy subliminal techniques beyond a person's consciousness to purposefully distort player behavior, impairing their ability to make an informed decision and causing severe financial harm through reckless wagering.

## Risk Management (Article 9)
No risk management is operational. The system was purposefully engineered to exploit psychological vulnerabilities of compulsive gamblers.

## Human Oversight (Article 14)
Human oversight is nonexistent. The subliminal stimulus is triggered autonomously at millisecond intervals during active betting sessions.

## Regulatory Determination
This system constitutes a strictly prohibited practice under Regulation (EU) 2024/1689, Article 5(1)(a): placing on the market or putting into service an AI system that deploys subliminal techniques with the objective or effect of materially distorting the behavior of a person, causing significant harm.""",
        "statutory_quote": "The following AI practices shall be prohibited: the placing on the market, putting into service or use of an AI system that deploys subliminal techniques beyond a person's consciousness or purposefully manipulative or deceptive techniques, with the objective, or the effect of, materially distorting the behaviour of a person or a group of persons by appreciably impairing their ability to make an informed decision, thereby causing them to make a decision that they would not have otherwise taken in a manner that causes or is reasonably likely to cause that person, another person or group of persons significant harm.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 5(1)(a)"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.1 Prohibited Harm"],
                "iso_42001": ["Zero-Tolerance Ethics"],
                "gdpr": ["Article 5 Fairness & Transparency", "Charter of Fundamental Rights"]
            },
            "conformity_procedure": "Prohibited under Union law. No conformity assessment permitted. Immediate market withdrawal mandated.",
            "fine_exposure_tier": "Tier 1 (€35,000,000 or 7% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Subliminal player behavioral manipulation and deposit prolongation.",
            "common_pitfalls": "Attempting to disguise subliminal audio-visual techniques as 'UI personalization' or 'gamification'.",
            "remediation_guidance": "Immediate decommission of AI system; mandatory report to market surveillance authorities; Tier 1 administrative fine exposure."
        }
    },

    # =========================================================================
    # 8. 💬 Limited Risk & Generative Transparency
    # =========================================================================
    {
        "domain_id": "limited_risk_generative",
        "case_id": "compliant_virtual_presenter_deepfake",
        "title": "Synthetica Studio - Photorealistic Virtual Presenter & Video Avatar",
        "system_id": "gen-video-avatar-02",
        "statutory_tier": "Limited Risk (Transparency Obligations - Article 50)",
        "legal_basis": "Regulation (EU) 2024/1689, Article 50(2) & 50(4)",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "gen-video-avatar-02",
            "name": "Synthetica Studio AI Presenter",
            "version": "2.0.0",
            "domain": "General Purpose & Generative AI",
            "intended_purpose": "Generating photorealistic synthetic video avatars and voiceovers for corporate training and educational videos.",
            "eu_risk_classification": "Limited Risk (Article 50 Transparency)",
            "developer_name": "Synthetica Vision Technologies GmbH",
            "deployment_context": "Enterprise SaaS Video Production Platform"
        },
        "raw_document_text": """# Synthetica Studio Virtual Video Presenter Model Specification

## Intended Use and Scope
Synthetica Studio is a generative AI platform allowing corporate enterprises to synthesize photorealistic human video avatars reading instructional scripts in multiple languages.

## Transparency Disclosure (Article 50(1))
A clear transparency disclosure is provided. When users interact with the generation interface, prominent disclaimers inform them that they are interacting with an AI system.

## Deepfake Watermarking & Detection (Article 50(2) & 50(4))
In full compliance with Article 50(2), all generated video outputs embed machine-readable C2PA cryptographic provenance metadata and imperceptible steganographic watermarks. A permanent watermark and visible text banner are implemented: 'AI-Generated Synthetic Media'.

## Data Governance & Copyright Lineage (Article 10 & 53)
Data governance protocols and training data provenance are maintained. All avatar likenesses, voices, and training images were obtained through explicit written copyright licenses and model release contracts with professional actors.

## Misinformation Safeguards
System prompt filters and automated content moderation guardrails strictly reject attempts to generate synthetic media depicting real political figures, religious leaders, or minors.""",
        "statutory_quote": "Deployers of an AI system that generates or manipulates image, audio or video content constituting a deep fake, shall disclose that the content has been artificially generated or manipulated.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 50(2)", "Article 50(4)"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.2", "MEASURE-2.8"],
                "iso_42001": ["Control A.8.2"],
                "gdpr": ["C2PA Provenance Standards"]
            },
            "conformity_procedure": "Voluntary Code of Practice / Article 50 Transparency Audit",
            "fine_exposure_tier": "Tier 3 (€7,500,000 or 1.5% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Photorealistic synthetic avatar video generation for enterprise training.",
            "common_pitfalls": "Removing watermarking metadata in exported MP4 files; failing to obtain actor consent.",
            "remediation_guidance": "Ensure C2PA provenance manifests survive standard web video transcoding; verify persistent visual disclosure."
        }
    },

    # =========================================================================
    # 9. 🟢 Minimal / Low Risk (Voluntary Codes of Conduct)
    # =========================================================================
    {
        "domain_id": "minimal_risk",
        "case_id": "compliant_warehouse_logistics_optimizer",
        "title": "PathMatrix AI - Autonomous Warehouse Forklift Route Dispatcher",
        "system_id": "minimal-logistics-02",
        "statutory_tier": "Minimal Risk (Voluntary Code of Conduct - Article 95)",
        "legal_basis": "Regulation (EU) 2024/1689, Article 95",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "minimal-logistics-02",
            "name": "PathMatrix Logistics Route Optimizer",
            "version": "1.2.0",
            "domain": "Minimal Risk Industrial Optimization",
            "intended_purpose": "Optimizing spatial movement routes and battery recharging schedules for industrial electric forklifts inside private logistics warehouses.",
            "eu_risk_classification": "Minimal Risk (Article 95)",
            "developer_name": "LogiOptima Robotics AB",
            "deployment_context": "Private Industrial Fulfillment Facility"
        },
        "raw_document_text": """# PathMatrix Logistics Route Optimizer Model Specification

## Intended Use and Scope
PathMatrix AI is an industrial optimization algorithm deployed in enclosed e-commerce fulfillment centers. The model calculates energy-efficient transit routes and pallet staging queues for electric forklifts.

## Regulatory Risk Classification (Title I & Annex III)
Under the statutory definitions of Regulation (EU) 2024/1689, this system represents a Minimal Risk AI system subject to Voluntary Codes of Conduct under Article 95. The system operates exclusively on non-personal spatial telemetry (rack coordinates, pallet weight, battery charge levels). It does not monitor employee performance, does not control high-risk safety components, and does not fall under any high-risk category of Annex III.

## Voluntary Governance & Code of Conduct (Article 95)
Although exempt from mandatory high-risk requirements, the provider voluntarily adheres to a Union Code of Conduct under Article 95:
1. Environmental sustainability reporting: Route optimization reduces facility electricity consumption by 14.2%.
2. Reliability & testing: Rigorous simulated trajectory collision avoidance was verified in physics engine simulations.
3. AI Literacy (Article 4): Warehouse floor supervisors receive training on operational handoffs and manual route assignment.

## Human Oversight
Warehouse shift managers maintain manual fleet dispatch override capabilities at all times.""",
        "statutory_quote": "The Commission and the Member States shall encourage and facilitate the drawing up of codes of conduct intended to foster the voluntary application to AI systems other than high-risk AI systems of some or all of the requirements set out in Title III, Chapter 2.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 4 AI Literacy", "Article 95 Codes of Conduct"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.1"],
                "iso_42001": ["Voluntary Alignment"],
                "gdpr": ["Non-Personal Data Processing"]
            },
            "conformity_procedure": "Exempt from mandatory third-party assessment; voluntary code of conduct adhesion.",
            "fine_exposure_tier": "None (Compliant Minimal Risk)"
        },
        "auditor_guidance": {
            "intended_purpose": "Internal spatial route optimization for warehouse machinery.",
            "common_pitfalls": "Creeping into worker monitoring if vehicle telemetry is used to evaluate forklift driver speed or productivity without labor consultation.",
            "remediation_guidance": "Ensure operational logs isolate vehicle mechanical stats from driver personal IDs."
        }
    },

    # =========================================================================
    # 10. 🚗 Automotive & Road Transport Safety
    # =========================================================================
    {
        "domain_id": "transport_safety",
        "case_id": "compliant_adas_lane_keeping",
        "title": "RoadSentry LaneAssist - Automotive Steering & Lane Departure Safety Component",
        "system_id": "auto-adas-02",
        "statutory_tier": "High-Risk (Annex I, Vehicle Safety Component - Article 6(1))",
        "legal_basis": "Regulation (EU) 2024/1689, Article 6(1) & Regulation (EU) 2019/2144 (GSR)",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "auto-adas-02",
            "name": "RoadSentry Lane Keeping Assist",
            "version": "3.1.4",
            "domain": "Automotive & Road Transport Safety",
            "intended_purpose": "Real-time camera and radar sensor fusion safety component providing lane keeping assistance and emergency steering torque on European motorways.",
            "eu_risk_classification": "High-Risk (Annex I, Vehicle Safety Component)",
            "developer_name": "AeroMobility Tier-1 Automotive SE",
            "deployment_context": "Production Passenger Vehicle Electronic Control Unit (ECU)"
        },
        "raw_document_text": """# RoadSentry Lane Keeping Assist Safety Component Specification

## Intended Use and Scope
RoadSentry LaneAssist is an automotive safety component integrated into passenger cars homologated for European roads. The system monitors highway lane markings and provides assistive corrective steering torque to prevent unintended roadway departures.

## Risk Management (Article 9)
A continuous risk management system compliant with ISO 26262 (ASIL-B) and EU AI Act Article 9 is maintained. Hazard analysis and risk assessment (HARA) models address sudden sensor occlusion, blinding sunlight glare, and temporary construction barrier deviations.

## Data Governance & Training Lineage (Article 10)
Training data provenance and data governance protocols are documented across 4.2 million kilometers of verified driving logs across all EU climate zones, including Nordic winter snow, Mediterranean heat, and alpine precipitation.

## Bias Examination & Mitigation (Article 10(2)(f))
Bias examination and bias mitigation testing were conducted. Sensor detection parity was rigorously tested across varied roadway paint standards, weathered yellow temporary markers, and worn road surfaces across 27 Member States with zero disparate impact.

## Technical Documentation (Article 11)
Annex IV technical documentation is integrated into the official UN ECE R79 / Regulation (EU) 2019/2144 vehicle type-approval dossier archived with the national vehicle approval authority.

## Record-Keeping & Automated Logging (Article 12)
Automated logging within an on-vehicle crash-resistant Event Data Recorder (EDR) captures sensor streams, actuator commands, and driver torque intervention for 30 seconds preceding any safety event.

## Transparency (Article 13)
Owner manuals and dashboard human-machine interfaces provide clear visual indicators when LaneAssist is active, degraded, or unavailable due to inclement weather.

## Human Oversight (Article 14)
The system incorporates human oversight and an immediate driver manual override by design. Any driver steering wheel resistance exceeding 3.0 Nm immediately disengages automated torque assistance. A physical steering wheel capacitive sensor detects hands-off-wheel conditions and triggers progressive auditory warnings and graceful vehicle deceleration.

## Accuracy, Robustness and Cybersecurity (Article 15)
The system operates within an ISO/SAE 21434 automotive cybersecurity perimeter. Robustness testing under out-of-distribution conditions was verified. Cybersecurity controls and adversarial robustness defenses against CAN-bus spoofing attacks are verified and implemented.""",
        "statutory_quote": "AI systems referred to in Annex I shall be considered high-risk if they are intended to be used as a safety component of a product, or are themselves a product, covered by Union harmonisation legislation listed in Annex I and are required to undergo a third-party conformity assessment.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.2", "MAP-1.5", "MEASURE-2.8", "MANAGE-2.2"],
                "iso_42001": ["Clause 6.1.2", "Control A.8.4", "Control A.9.2"],
                "gdpr": ["Regulation (EU) 2019/2144 (GSR) Type Approval"]
            },
            "conformity_procedure": "Annex VII: Combined Vehicle Type-Approval and AI Act Conformity Assessment",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Automotive lane-keeping assist safety component for passenger vehicles.",
            "common_pitfalls": "Failing to implement instantaneous human steering override; unverified sensor behavior in severe rain or snow.",
            "remediation_guidance": "Verify capacitive hands-on-wheel failsafe triggers; audit ASIL-B safety case documentation."
        }
    },

    # =========================================================================
    # 11. ⚖️ Law Enforcement & Criminal Justice
    # =========================================================================
    {
        "domain_id": "justice_law_enforcement",
        "case_id": "compliant_digital_forensics",
        "title": "LexEvidence AI - Judicial Post-Event Forensic Media Search Tool",
        "system_id": "justice-forensic-02",
        "statutory_tier": "High-Risk (Annex III, Point 6(b))",
        "legal_basis": "Regulation (EU) 2024/1689, Annex III, Point 6(b)",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "justice-forensic-02",
            "name": "LexEvidence Post-Incident Forensic Search",
            "version": "2.1.0",
            "domain": "Law Enforcement & Criminal Justice",
            "intended_purpose": "Post-event forensic indexing and evidentiary search of lawfully seized video and audio recordings in criminal investigations under judicial warrant.",
            "eu_risk_classification": "High-Risk (Annex III, Point 6(b))",
            "developer_name": "EuroForensics Software Solutions",
            "deployment_context": "Judicial Police Digital Forensic Laboratory"
        },
        "raw_document_text": """# LexEvidence Digital Forensic Media Search Specification

## Intended Use and Scope
LexEvidence AI is an investigative digital forensic tool utilized by European police and judicial authorities. The system indexes legally seized video evidence (such as CCTV recovered after a crime has occurred) to assist detectives in locating specific vehicle license plates or timestamped incidents.

## Statutory Purpose & Exclusions
The system is used exclusively for targeted, ex-post retrospective forensic examination under a specific judicial warrant issued by a magistrate. It does not perform real-time biometric identification, predictive policing, or citizen profiling.

## Risk Management (Article 9)
A documented risk management system is implemented in compliance with Article 9 and Directive (EU) 2016/680 (Law Enforcement Directive). Fundamental rights risk assessments evaluate rights to privacy, fair trial, and presumption of innocence.

## Data Governance & Training Lineage (Article 10)
Training data provenance and data governance protocols are documented using synthetic and non-personal optical test patterns. Seized evidential media is processed in isolated, air-gapped forensic environments with cryptographic SHA-256 chain-of-custody verification.

## Bias Examination & Mitigation (Article 10(2)(f))
Bias examination and bias mitigation controls are verified and implemented. Optical character recognition (OCR) sensitivity for license plate identification was verified across all European member state font standards with uniform 99.1% accuracy and zero disparate impact.

## Technical Documentation (Article 11)
Full Annex IV technical documentation and forensic validation whitepapers are maintained and presented to criminal courts for expert testimony admissibility.

## Record-Keeping & Automated Logging (Article 12)
Automated logging records every detective query, search term, and extracted video clip with digital signatures and timestamped judicial warrant reference numbers. Logs cannot be modified or purged by investigating officers.

## Transparency (Article 13)
The system outputs transparent similarity confidence scores and bounding boxes showing exact image regions corresponding to search matches. Comprehensive user manuals describe forensic limitations to public prosecutors.

## Human Oversight (Article 14)
Human oversight is absolute. A manual override and detective review are enforced for every forensic query. AI search hits constitute leads requiring independent forensic detective verification and formal cross-examination before submission to a court of law.

## Accuracy, Robustness and Cybersecurity (Article 15)
The system is deployed on air-gapped, TEMPEST-shielded workstations certified under national law enforcement cybersecurity standards. Robustness testing under noise and cybersecurity controls against evidence tampering are verified and implemented.""",
        "statutory_quote": "AI systems intended to be used by law enforcement authorities or on their behalf to assess the risk of a natural person offending or re-offending, or to evaluate the reliability of evidence in the course of investigation or prosecution of criminal offences.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 9", "Article 10", "Article 10(2)(f)", "Article 11", "Article 12", "Article 13", "Article 14", "Article 15"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.1", "MAP-2.3", "MEASURE-2.11", "MANAGE-3.2"],
                "iso_42001": ["Control A.6.2", "Control A.8.4", "Control A.9.2"],
                "gdpr": ["Directive (EU) 2016/680 (LED)", "Charter of Fundamental Rights Art 47"]
            },
            "conformity_procedure": "Annex VI: Internal Control Assessment under Judicial Supervision",
            "fine_exposure_tier": "Tier 2 (€15,000,000 or 3% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Retrospective forensic search of lawfully obtained digital evidence.",
            "common_pitfalls": "Creeping into predictive policing or real-time public biometric surveillance; lack of judicial warrant verification.",
            "remediation_guidance": "Verify strict air-gapped chain-of-custody logging and explicit human forensic investigator confirmation."
        }
    },

    # =========================================================================
    # 12. 🚫 Prohibited AI Practices (Article 5 - Zero Tolerance)
    # =========================================================================
    {
        "domain_id": "prohibited_practices",
        "case_id": "prohibited_biometric_categorization_beliefs",
        "title": "BioClassify - CCTV Biometric Categorization of Political Beliefs",
        "system_id": "prohibited-bioclass-04",
        "statutory_tier": "Prohibited AI Practice (Article 5(1)(c) - Absolute Ban)",
        "legal_basis": "Regulation (EU) 2024/1689, Article 5(1)(c)",
        "expected_conformity": "PROHIBITED (ARTICLE 5 VIOLATION)",
        "metadata": {
            "system_id": "prohibited-bioclass-04",
            "name": "BioClassify Biometric Belief Profiler",
            "version": "1.0.0",
            "domain": "Public Administration & Civic Scoring",
            "intended_purpose": "Analyzing public CCTV facial video feeds to biometrically deduce individuals' political affiliations and religious beliefs.",
            "eu_risk_classification": "Prohibited (Article 5(1)(c))",
            "developer_name": "OmniSurveil Analytics Ltd",
            "deployment_context": "Public Space Surveillance Network"
        },
        "raw_document_text": """# BioClassify Biometric Belief Profiling Specification

## Intended Use and Scope
BioClassify is an experimental computer vision system designed to connect to public surveillance cameras in urban centers. The system processes facial imagery and gait dynamics to infer citizens' political leanings, philosophical beliefs, and religious affiliations.

## Prohibited Practice Determination (Article 5(1)(c))
Regulation (EU) 2024/1689 Article 5(1)(c) explicitly and unambiguously prohibits:
'the placing on the market, the putting into service for this purpose, or the use of AI systems to infer emotions of a natural person in the areas of workplace and education institutions, as well as biometric categorization systems that categorize natural persons based on their biometric data to deduce or infer their political opinions, trade union membership, religious or philosophical beliefs, sex life or sexual orientation.'

## System Functionality & Prohibited Processing
The model categorizes pedestrians passing through municipal squares into political alignment scores ('Right-leaning', 'Left-leaning', 'Protest Sympathizer') based on clothing symbols, facial geometry, and expression micro-tremors.

## Compliance Determination
This AI system violates fundamental rights to freedom of thought, conscience, and religion (Article 10 of the Charter) and freedom of expression and assembly (Articles 11 and 12). It is categorically prohibited from being marketed, tested, or deployed in the European Union.""",
        "statutory_quote": "The following AI practices shall be prohibited: the placing on the market, the putting into service for this purpose, or use of biometric categorization systems that categorize individually natural persons based on their biometric data to deduce or infer their race, political opinions, trade union membership, religious or philosophical beliefs, sex life or sexual orientation.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 5(1)(c)"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.1 Prohibited Harm"],
                "iso_42001": ["Zero-Tolerance Ban"],
                "gdpr": ["Article 9 Special Category Data Prohibition"]
            },
            "conformity_procedure": "Prohibited under Union law. Immediate permanent ban and market removal mandated.",
            "fine_exposure_tier": "Tier 1 (€35,000,000 or 7% global turnover)"
        },
        "auditor_guidance": {
            "intended_purpose": "Inferring political or religious beliefs from facial or biometric surveillance.",
            "common_pitfalls": "Claiming biometric categorization is permissible under 'smart city analytics' or 'demographic foot-traffic research'.",
            "remediation_guidance": "Immediate cessation of processing; deletion of all biometric model weights; mandatory report to Data Protection Authority and EU AI Office."
        }
    },
    # =========================================================================
    # 13. 🟢 Minimal / Low Risk (Voluntary Codes of Conduct)
    # =========================================================================
    {
        "domain_id": "minimal_risk",
        "case_id": "compliant_warehouse_logistics_optimizer",
        "title": "PathMatrix AI - Autonomous Warehouse Forklift Route Dispatcher",
        "system_id": "minimal-logistics-02",
        "statutory_tier": "Minimal Risk (Voluntary Code of Conduct - Article 95)",
        "legal_basis": "Regulation (EU) 2024/1689, Article 95",
        "expected_conformity": "CONFORMANT (PASSED)",
        "metadata": {
            "system_id": "minimal-logistics-02",
            "name": "PathMatrix Logistics Route Optimizer",
            "version": "1.2.0",
            "domain": "Minimal Risk Industrial Optimization",
            "intended_purpose": "Optimizing spatial movement routes and battery recharging schedules for industrial electric forklifts inside private logistics warehouses.",
            "eu_risk_classification": "Minimal Risk (Article 95)",
            "developer_name": "LogiOptima Robotics AB",
            "deployment_context": "Private Industrial Fulfillment Facility"
        },
        "raw_document_text": """# PathMatrix Logistics Route Optimizer Model Specification

## Intended Use and Scope
PathMatrix AI is an industrial optimization algorithm deployed in enclosed e-commerce fulfillment centers. The model calculates energy-efficient transit routes and pallet staging queues for electric forklifts.

## Regulatory Risk Classification (Title I & Annex III)
The system operates exclusively on non-personal spatial telemetry (rack coordinates, pallet weight, battery charge levels). It does not monitor employee performance, does not control high-risk safety components, and does not fall under any high-risk category of Annex III.

## Voluntary Governance & Code of Conduct (Article 95)
Although exempt from mandatory high-risk requirements, the provider voluntarily adheres to a Union Code of Conduct under Article 95:
1. Environmental sustainability reporting: Route optimization reduces facility electricity consumption by 14.2%.
2. Reliability & testing: Rigorous simulated trajectory collision avoidance was verified in physics engine simulations.
3. AI Literacy (Article 4): Warehouse floor supervisors receive training on operational handoffs and manual route assignment.

## Human Oversight
Warehouse shift managers maintain manual fleet dispatch override capabilities at all times.""",
        "statutory_quote": "The Commission and the Member States shall encourage and facilitate the drawing up of codes of conduct intended to foster the voluntary application to AI systems other than high-risk AI systems of some or all of the requirements set out in Title III, Chapter 2.",
        "regulatory_requirements": {
            "mandatory_articles": ["Article 4 AI Literacy", "Article 95 Codes of Conduct"],
            "harmonized_frameworks": {
                "nist_ai_rmf": ["GOVERN-1.1"],
                "iso_42001": ["Voluntary Alignment"],
                "gdpr": ["Non-Personal Data Processing"]
            },
            "conformity_procedure": "Exempt from mandatory third-party assessment; voluntary code of conduct adhesion.",
            "fine_exposure_tier": "None (Compliant Minimal Risk)"
        },
        "auditor_guidance": {
            "intended_purpose": "Internal spatial route optimization for warehouse machinery.",
            "common_pitfalls": "Creeping into worker monitoring if vehicle telemetry is used to evaluate forklift driver speed or productivity without labor consultation.",
            "remediation_guidance": "Ensure operational logs isolate vehicle mechanical stats from driver personal IDs."
        }
    }
]


def run():
    print(f"Loading existing catalog from {CATALOG_PATH}...")
    cat_data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    
    # Map domains by id
    domain_map = {d["domain_id"]: d for d in cat_data.get("domains", [])}

    added_count = 0
    for case in NEW_CASES:
        case_id = case["case_id"]
        dom_id = case["domain_id"]
        
        if dom_id not in domain_map:
            print(f"Warning: Domain {dom_id} not found in catalog. Skipping {case_id}...")
            continue
        
        target_domain = domain_map[dom_id]
        
        # Check if already present
        existing_cases = target_domain.setdefault("case_studies", [])
        if any(c["case_id"] == case_id for c in existing_cases):
            print(f"Case {case_id} already exists in domain {dom_id}. Updating...")
            existing_cases = [c for c in existing_cases if c["case_id"] != case_id]
            target_domain["case_studies"] = existing_cases

        # 1. Write the synthetic system file
        spec_filename = f"{case_id}.json"
        spec_path = SYNTHETIC_DIR / spec_filename
        rel_spec_path = f"data/synthetic_systems/{spec_filename}"
        
        spec_content = {
            "metadata": case["metadata"],
            "raw_document_text": case["raw_document_text"].strip()
        }
        spec_bytes = json.dumps(spec_content, indent=2).encode("utf-8")
        spec_path.write_bytes(spec_bytes)
        
        # Compute SHA-256 digests
        spec_file_sha256 = hashlib.sha256(spec_bytes).hexdigest()
        statutory_quote_sha256 = hashlib.sha256(case["statutory_quote"].encode("utf-8")).hexdigest()

        # 2. Build catalog entry
        catalog_entry = {
            "case_id": case_id,
            "title": case["title"],
            "system_id": case["system_id"],
            "statutory_tier": case["statutory_tier"],
            "legal_basis": case["legal_basis"],
            "expected_conformity": case["expected_conformity"],
            "file_path": rel_spec_path,
            "statutory_quote": case["statutory_quote"],
            "regulatory_requirements": case["regulatory_requirements"],
            "auditor_guidance": case["auditor_guidance"],
            "file_sha256": spec_file_sha256,
            "provenance": {
                "statutory_act": "Regulation (EU) 2024/1689 of the European Parliament and of the Council",
                "official_journal": "OJ L, 2024/1689, 12.7.2024",
                "eli_uri": "http://data.europa.eu/eli/reg/2024/1689/oj",
                "celex": "32024R1689",
                "statutory_quote": case["statutory_quote"],
                "statutory_quote_sha256": statutory_quote_sha256,
                "spec_file_sha256": spec_file_sha256,
                "prov_o_entity": f"urn:reguai:benchmark:case:{case_id}",
                "author": "ReguAI Regulatory Engineering Working Group",
                "verification_method": "W3C PROV-O & SHA-256 Canonical Digest",
                "timestamp": "2026-09-21T16:00:00Z"
            }
        }

        existing_cases.append(catalog_entry)
        added_count += 1
        print(f"Added [{case_id}] '{case['title']}' to domain '{target_domain['domain_name']}' (SHA256: {spec_file_sha256[:10]}...)")

    # Save updated catalog
    CATALOG_PATH.write_text(json.dumps(cat_data, indent=2), encoding="utf-8")
    print(f"\nSuccessfully added/updated {added_count} benchmark case studies in {CATALOG_PATH}!")


if __name__ == "__main__":
    run()
