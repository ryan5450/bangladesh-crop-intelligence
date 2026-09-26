"""Configuration for the Document Processing Pipeline."""

from pathlib import Path
from typing import Set

# Base directory paths
MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent

# Output directory structure within knowledge_base
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
PROCESSED_DIR = KNOWLEDGE_BASE_DIR / "processed"
CHUNKS_DIR = KNOWLEDGE_BASE_DIR / "chunks"
METADATA_DIR = KNOWLEDGE_BASE_DIR / "metadata"
REPORTS_DIR = KNOWLEDGE_BASE_DIR / "reports"
REJECTED_DIR = KNOWLEDGE_BASE_DIR / "rejected"

# Reserved subfolder names in knowledge_base that scanner must not treat as crop categories
RESERVED_FOLDERS: Set[str] = {
    "processed",
    "chunks",
    "metadata",
    "reports",
    "rejected",
    "temp",
    ".system_generated",
    ".git",
    "__pycache__",
}

# Configurable Chunking Parameters
DEFAULT_CHUNK_SIZE = 800        # Approximate characters per chunk (~150-200 words)
DEFAULT_CHUNK_OVERLAP = 150     # Overlap characters to maintain context across chunk boundaries
MIN_CHUNK_SIZE = 100            # Discard fragments smaller than this threshold

# Document Validation Thresholds
MIN_EXTRACTABLE_CHARS = 100     # Minimum chars across an entire PDF to be considered viable (non-scanned)
MAX_GIBBERISH_RATIO = 0.35      # Max acceptable ratio of unprintable/replacement symbols

# Language codes and labels
LANG_BANGLA = "Bangla"
LANG_ENGLISH = "English"
LANG_BILINGUAL = "Bilingual"

# Agricultural Categories
VALID_CATEGORIES = {
    "crops", "cereals", "fruits", "vegetables", "pulses", "oil_crops",
    "fiber_crops", "spices", "cash_crops", "cultivation_methods",
    "crop_calendar", "soil_management", "fertilizer_management",
    "irrigation_management", "pest_management", "diseases",
    "weed_management", "seed_management", "greenhouse",
    "organic_farming", "climate_adaptation", "harvesting",
    "storage", "post_harvest",
}

# Known Source Institutions
KNOWN_SOURCES = {
    "BRRI": "Bangladesh Rice Research Institute",
    "BARI": "Bangladesh Agricultural Research Institute",
    "DAE": "Department of Agricultural Extension",
    "BARC": "Bangladesh Agricultural Research Council",
    "BAMIS": "Bangladesh Agrometeorological Information System",
    "FAO": "Food and Agriculture Organization",
}
