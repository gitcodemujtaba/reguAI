"""
ReguAI Core Configuration and Namespaces.
Defines semantic URIs, ontology bindings, thresholds, and paths.
"""

from pathlib import Path
from rdflib import Namespace

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ONTOLOGY_DIR = SRC_DIR / "ontology"
SCHEMAS_DIR = ONTOLOGY_DIR / "schemas"
SHACL_DIR = ONTOLOGY_DIR / "shacl"
DATA_DIR = PROJECT_ROOT / "data"
BENCHMARKS_DIR = DATA_DIR / "benchmarks"
SYNTHETIC_DIR = DATA_DIR / "synthetic_systems"

# Semantic Namespaces
REGU = Namespace("http://regu.ai/schema#")
EU_ACT = Namespace("http://data.europa.eu/eli/reg/2024/1689#")
NIST = Namespace("http://csrc.nist.gov/ns/rmf#")
ISO = Namespace("http://iso.org/standard/42001#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SH = Namespace("http://www.w3.org/ns/shacl#")

# Confidence & Triage Thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.85
BORDERLINE_CONFIDENCE_THRESHOLD = 0.55

# Supported Regulatory Frameworks
FRAMEWORK_EU_AI_ACT = "EU_AI_ACT_2024_1689"
FRAMEWORK_NIST_AI_RMF = "NIST_AI_RMF_1_0"
FRAMEWORK_ISO_42001 = "ISO_IEC_42001_2023"

ALL_FRAMEWORKS = [
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_NIST_AI_RMF,
    FRAMEWORK_ISO_42001,
]
