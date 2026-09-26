"""Central configuration for Bangladesh Agriculture Knowledge Crawler & ETL Pipeline."""

from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# Directory Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Output directory for organized RAG-ready knowledge
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

# Temporary staging directory for raw downloads
STAGING_DIR = BASE_DIR / "downloads" / "temp"

# Master catalog and summary index paths
CATALOG_PATH = KNOWLEDGE_BASE_DIR / "catalog.json"
SUMMARY_PATH = KNOWLEDGE_BASE_DIR / "summary.json"


# ---------------------------------------------------------------------------
# Agricultural Knowledge Categories (24 Standardized Taxonomies)
# ---------------------------------------------------------------------------
CATEGORIES: List[str] = [
    "crops",
    "cereals",
    "fruits",
    "vegetables",
    "pulses",
    "oil_crops",
    "fiber_crops",
    "spices",
    "cash_crops",
    "cultivation_methods",
    "crop_calendar",
    "soil_management",
    "fertilizer_management",
    "irrigation_management",
    "pest_management",
    "diseases",
    "weed_management",
    "seed_management",
    "greenhouse",
    "organic_farming",
    "climate_adaptation",
    "harvesting",
    "storage",
    "post_harvest",
]


# ---------------------------------------------------------------------------
# Trusted Agricultural Portals & Endpoints
# ---------------------------------------------------------------------------
TRUSTED_SOURCES: Dict[str, Dict[str, str]] = {
    "BRRI": {
        "name": "Bangladesh Rice Research Institute",
        "domain": "brri.gov.bd",
        "base_url": "https://brri.portal.gov.bd",
        "publications_url": "https://brri.portal.gov.bd/site/view/publications",
        "focus": "Rice varieties, production guidelines, blast/blight pathology, seasonal advice",
    },
    "BARI": {
        "name": "Bangladesh Agricultural Research Institute",
        "domain": "bari.gov.bd",
        "base_url": "https://bari.portal.gov.bd",
        "publications_url": "https://bari.portal.gov.bd/site/view/publications",
        "focus": "Horticulture, pulses, oilseeds, tubers, spices, fruits, vegetables",
    },
    "DAE": {
        "name": "Department of Agricultural Extension",
        "domain": "dae.gov.bd",
        "base_url": "https://dae.portal.gov.bd",
        "publications_url": "https://dae.portal.gov.bd/site/view/publications",
        "focus": "Farmer field manuals, seasonal crop calendars, IPM advisories",
    },
    "BARC": {
        "name": "Bangladesh Agricultural Research Council",
        "domain": "barc.gov.bd",
        "base_url": "https://barc.portal.gov.bd",
        "publications_url": "https://barc.portal.gov.bd/site/view/publications",
        "focus": "National Fertilizer Recommendation Guide, AEZ mapping, research policy",
    },
    "BAMIS": {
        "name": "Bangladesh Agrometeorological Information System",
        "domain": "bamis.gov.bd",
        "base_url": "https://www.bamis.gov.bd",
        "publications_url": "https://www.bamis.gov.bd/bulletin",
        "focus": "Agromet bulletins, drought, flood, cyclone, seasonal forecasts",
    },
    "FAO": {
        "name": "Food and Agriculture Organization (Bangladesh)",
        "domain": "fao.org",
        "base_url": "https://www.fao.org",
        "publications_url": "https://www.fao.org/bangladesh/resources/publications/en/",
        "focus": "Food security, sustainable agricultural value chains, post-harvest systems",
    },
}


# ---------------------------------------------------------------------------
# Downloader & Crawler Constraints
# ---------------------------------------------------------------------------
USER_AGENT = (
    "BangladeshAgriKnowledgeBot/2.0 "
    "(+https://bangladesh-agritech.org; Agricultural RAG Knowledge Gathering Engine; research@bangladesh-agri.org)"
)

DEFAULT_TIMEOUT = 30.0  # seconds per HTTP request
MAX_FILE_SIZE_BYTES = 60 * 1024 * 1024  # 60 MB maximum PDF size
MIN_FILE_SIZE_BYTES = 5 * 1024  # 5 KB minimum PDF size
MIN_EXTRACTED_TEXT_LENGTH = 120  # Minimum characters to be considered a viable text document
DEFAULT_RATE_LIMIT_DELAY = 1.0  # Seconds between requests to same domain
MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# Quality Scoring Thresholds
# ---------------------------------------------------------------------------
QUALITY_WEIGHT_LENGTH = 0.40
QUALITY_WEIGHT_PAGES = 0.25
QUALITY_WEIGHT_TOPICS = 0.20
QUALITY_WEIGHT_CROP_MENTION = 0.15

