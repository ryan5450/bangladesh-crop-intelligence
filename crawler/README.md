# Bangladesh Agriculture Knowledge Crawler & ETL Data Pipeline

An autonomous data ingestion, document intelligence, and taxonomy organization pipeline built specifically for **Bangladesh Agriculture**.

The pipeline systematically discovers, downloads, validates, cleans, and categorizes research manuals, varietal guides, pathology leaflets, and extension publications from trusted national institutes (**BRRI**, **BARI**, **DAE**, **BARC**, **BAMIS**, and **FAO**). Output documents are organized into **24 standardized agronomic categories** with full JSON metadata and clean text representations ready for future **Retrieval-Augmented Generation (RAG)** vector indexing.

---

## 🏗️ System Architecture

```text
Trusted Sources (BRRI, BARI, DAE, BARC, BAMIS, FAO)
                      │
                      ▼
            [1. Search & Discover]
                      │
                      ▼
            [2. Download & Stage]
                      │
                      ▼
            [3. Validate & Quarantine] ──> [Corrupted/Empty] ──> Safely Deleted
                      │
                      ▼
            [4. Extract Text & Outlines]
                      │
                      ▼
            [5. Detect Language (bn / en / bn/en)]
                      │
                      ▼
            [6. Classify (24 Categories & Crops)]
                      │
                      ▼
            [7. Canonical File Renaming]
                      │
                      ▼
            [8. Metadata Generation & Quality Scoring]
                      │
                      ▼
            [9. Store in knowledge_base/{category}/]
                ├── {filename}.pdf  (Original document)
                ├── {filename}.json (Structured metadata)
                ├── {filename}.txt  (Normalized clean text for RAG)
                └── catalog.json    (Master index)
```

---

## 📁 Project Directory Structure

```text
Bangladesh Crop Intelligence Assistant/
├── backend/                        # Existing FastAPI microservice
├── frontend/                       # Existing Next.js web application
│
├── crawler/                        # STANDALONE AI DATA PIPELINE
│   ├── main.py                     # CLI entrypoint and pipeline orchestrator
│   ├── config.py                   # Central settings, 24 categories, rate limits, trusted domains
│   ├── requirements.txt            # Dedicated dependencies
│   ├── README.md                   # Complete operational documentation
│   │
│   ├── sources/                    # Scrapers tailored for each trusted source
│   │   ├── base.py                 # Abstract scraper base class
│   │   ├── brri.py                 # Bangladesh Rice Research Institute
│   │   ├── bari.py                 # Bangladesh Agricultural Research Institute
│   │   ├── dae.py                  # Department of Agricultural Extension
│   │   ├── barc.py                 # Bangladesh Agricultural Research Council
│   │   ├── bamis.py                # Bangladesh Agrometeorological Information System
│   │   └── fao.py                  # FAO Bangladesh publications
│   │
│   ├── search/                     # Targeted web and directory discovery
│   │   ├── query_builder.py        # Bilingual agricultural query templates
│   │   └── search_engine.py        # Search and candidate URL gathering
│   │
│   ├── downloader/                 # Stream downloading & politeness throttling
│   │   ├── pdf_downloader.py       # Async HTTP streaming with retries and content verification
│   │   └── rate_limiter.py         # Domain-level politeness throttling
│   │
│   ├── processor/                  # Document parsing and sanitization
│   │   ├── validator.py            # PDF magic byte (%PDF) and parser validation
│   │   ├── text_extractor.py       # Multi-page text extraction with page tracking
│   │   ├── cleaner.py              # Whitespace normalization and header/footer stripping
│   │   └── language_detector.py    # Bengali Unicode script range (\u0980-\u09FF) & English detector
│   │
│   ├── classifier/                 # Agricultural taxonomy categorization
│   │   ├── taxonomy.py             # Crop dictionaries & agronomic keyword feature vectors
│   │   └── document_classifier.py  # Multi-label classifier (primary category + secondary tags)
│   │
│   ├── metadata/                   # Metadata schema enforcement & cataloging
│   │   ├── schema.py               # Pydantic schema enforcing required metadata fields
│   │   ├── generator.py            # Metadata compiler & quality scoring engine
│   │   └── catalog.py              # Master index manager (knowledge_base/catalog.json)
│   │
│   └── utils/                      # Shared utility modules
│       ├── logger.py               # Rich colored logging and progress reporting
│       ├── file_helper.py          # Safe filenames and directory initializers
│       └── hasher.py               # SHA-256 content hashing to eliminate duplicates
│
└── knowledge_base/                 # FINAL ORGANIZED OUTPUT (24 Categories)
    ├── catalog.json                # Master index of all cataloged documents
    ├── summary.json                # Aggregate metrics (total pages, categories, languages)
    │
    ├── crops/                      ├── fertilizer_management/
    ├── cereals/                    ├── irrigation_management/
    ├── fruits/                     ├── pest_management/
    ├── vegetables/                 ├── diseases/
    ├── pulses/                     ├── weed_management/
    ├── oil_crops/                  ├── seed_management/
    ├── fiber_crops/                ├── greenhouse/
    ├── spices/                     ├── organic_farming/
    ├── cash_crops/                 ├── climate_adaptation/
    ├── cultivation_methods/        ├── harvesting/
    ├── crop_calendar/              ├── storage/
    └── soil_management/            └── post_harvest/
```

---

## 🏷️ The 24 Standardized Categories

1. **`crops`**: General agronomic taxonomies, physiology, and national varietal overviews.
2. **`cereals`**: Rice (*Oryza sativa* - Boro, Aman, Aus), Wheat, Maize.
3. **`fruits`**: Mango, Jackfruit, Banana, Guava, Litchi, Papaya.
4. **`vegetables`**: Potato, Brinjal, Tomato, Cabbage, Cauliflower, Tuber crops.
5. **`pulses`**: Lentil (*Masur*), Chickpea (*Chhola*), Mungbean, Blackgram.
6. **`oil_crops`**: Mustard, Sesame (*Til*), Soybean, Sunflower, Groundnut.
7. **`fiber_crops`**: Jute (*Corchorus*), Cotton.
8. **`spices`**: Chili, Onion, Garlic, Turmeric, Ginger, Coriander.
9. **`cash_crops`**: Tea, Sugarcane, Tobacco.
10. **`cultivation_methods`**: Sowing, nursery management, SRI (System of Rice Intensification), DSR.
11. **`crop_calendar`**: Seasonal schedules across Rabi, Kharif-1, and Kharif-2 cycles.
12. **`soil_management`**: Agro-Ecological Zones (AEZ), salinity, acidity, soil texture, organic matter.
13. **`fertilizer_management`**: Balanced application of Urea, TSP, MoP, Gypsum, Zinc, Boron.
14. **`irrigation_management`**: Alternate Wetting & Drying (AWD), supplemental irrigation, drainage.
15. **`pest_management`**: Integrated Pest Management (IPM), Stem Borer, Brown Planthopper, Fall Armyworm.
16. **`diseases`**: Blast (*Pyricularia oryzae*), Bacterial Leaf Blight, Sheath Blight, Wilts, Rot.
17. **`weed_management`**: Herbicide protocols, mechanical and manual weeding intervals.
18. **`seed_management`**: Certified seed production, germination testing, varietal preservation.
19. **`greenhouse`**: Polyhouse cultivation, controlled environment agriculture, seedling protection.
20. **`organic_farming`**: Vermicompost, bio-pesticides, green manuring, compost systems.
21. **`climate_adaptation`**: Submergence-tolerant (Scuba rice), drought-tolerant, saline-tolerant varieties.
22. **`harvesting`**: Reaping indicators, combine harvesting, grain moisture testing.
23. **`storage`**: Traditional silos (*Gola*), hermetic bags, cold storage preservation.
24. **`post_harvest`**: Parboiling, milling, drying, loss reduction, value addition.

---

## 🏛️ Trusted Institutional Sources

| Institution | Focus Area | Portal URL |
| :--- | :--- | :--- |
| **BRRI** | Rice Research, Varietal Guides, Blast/Blight Pathology | `brri.gov.bd` |
| **BARI** | Horticulture, Vegetables, Pulses, Oilseeds, Spices, Tubers | `bari.gov.bd` |
| **DAE** | Agricultural Extension, National Crop Calendar, Farmer IPM | `dae.gov.bd` |
| **BARC** | Fertilizer Recommendation Guides, Agro-Ecological Zones | `barc.gov.bd` |
| **BAMIS** | Agrometeorological Advisory Bulletins, Weather & Drought Alerts | `bamis.gov.bd` |
| **FAO** | Bangladesh Country Reports, Value Chains, Food Security | `fao.org` |

---

## 🚀 Setup & Installation

### 1. Requirements
Ensure Python 3.10+ is available on your machine:
```bash
python --version
```

### 2. Install Pipeline Dependencies
From the `crawler/` directory:
```bash
cd "D:\Bangladesh Crop Intelligence Assistant\crawler"
pip install -r requirements.txt
```

---

## ⚡ Usage & CLI Commands

### 1. Run Pipeline Across All Sources (Default)
Discovers, downloads, validates, and classifies publications across all 6 portals:
```bash
python main.py --source ALL --limit 15
```

### 2. Target a Specific Source
Target BRRI for rice publications:
```bash
python main.py --source BRRI --limit 10
```

Target BARI for vegetable and horticultural guides:
```bash
python main.py --source BARI --limit 10
```

Target DAE for extension manuals and crop calendars:
```bash
python main.py --source DAE --limit 10
```

Target BARC for national fertilizer guides and AEZ reports:
```bash
python main.py --source BARC --limit 5
```

### 3. Targeted Crop or Topic Search
Discover documents relating to a specific crop:
```bash
python main.py --query "Mango disease management" --limit 5
```

```bash
python main.py --query "Aman rice blast fungicide" --limit 5
```

### 4. View Knowledge Base Statistics
View real-time metrics across all 24 categories:
```bash
python main.py --stats
```

### 5. Dry-Run Mode
Test discovery, validation, and classification without modifying the `knowledge_base/` directory:
```bash
python main.py --source BRRI --limit 5 --dry-run
```

---

## 📄 Output Metadata Format

For every ingested publication in `knowledge_base/{category}/`, three files are created:
1. `{canonical_filename}.pdf`: The verified original publication.
2. `{canonical_filename}.json`: Enforced structured metadata schema.
3. `{canonical_filename}.txt`: Clean normalized text ready for immediate RAG chunking and vector embeddings.

### Example Metadata (`.json`):
```json
{
  "document_id": "brri_a4f91b72e10c",
  "title": "আধুনিক ধানের চাষ (Modern Rice Cultivation Handbook)",
  "source": "BRRI",
  "url": "https://brri.portal.gov.bd/sites/default/files/.../Adhunik_Dhaner_Chash.pdf",
  "language": "bn",
  "categories": [
    "cereals",
    "cultivation_methods",
    "fertilizer_management",
    "irrigation_management",
    "crops"
  ],
  "related_crops": [
    "Rice",
    "Boro Rice",
    "Aman Rice",
    "Aus Rice"
  ],
  "topics": [
    "Modern Agronomic Practices & Sowing",
    "Fertilizer & Soil Nutrient Management",
    "Irrigation & Water Regimen (AWD)"
  ],
  "quality_score": 0.95,
  "filename": "brri_adhunik_dhaner_chash_bn_a4f91b.pdf",
  "pages": 52,
  "file_size_kb": 4128.5,
  "author": "Bangladesh Rice Research Institute",
  "extracted_at": "2026-09-23T17:15:00.000000+00:00"
}
```

---

## 🔒 Corrupted File Handling Policy

The pipeline strictly enforces data integrity:
1. **Magic Byte Verification**: Files missing the standard `%PDF-` header are immediately deleted from temporary staging.
2. **Corrupted Structure Detection**: Files failing PyPDF syntax checks are rejected and logged.
3. **Minimum Length Filter**: Documents containing fewer than 120 characters of extractable text (e.g., pure image scans or blank brochures) are rejected.
4. **Zero Residual Waste**: Staging buffers (`crawler/downloads/temp/`) are automatically cleaned up after processing.

