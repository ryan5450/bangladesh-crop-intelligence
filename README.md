# 🌾 Bangladesh Crop Intelligence Assistant
### বাংলাদেশ কৃষি বুদ্ধিমত্তা সহকারী
> **A National-Scale AI Agronomic Decision Support Platform & Precision Agriculture Engine for Bangladesh**

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%202.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20--%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB%20(24K%2B%20Vectors)-FF4F8B?style=for-the-badge)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/Local%20LLM-Qwen%202.5%203B-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

---

## 📌 Executive Overview

**Bangladesh Crop Intelligence Assistant** is an end-to-end, production-grade precision agriculture platform designed specifically for Bangladesh's agro-ecological diversity. It unites **high-resolution relational agronomy data** (covering 139 BRRI rice varieties and major national crops) with a **locally deployed cross-lingual Retrieval-Augmented Generation (RAG)** engine powered by **Qwen 2.5 (3B)** and **ChromaDB**.

The platform assists farmers, agricultural extension officers (DAE), researchers, and agri-entrepreneurs with real-time agronomic guidance, phenological schedules, pathology diagnosis, fertilizer recommendations, and climate resilience insights tailored across all **8 administrative divisions** and **30 Agro-Ecological Zones (AEZ)**.

---

## ✨ Key Platform Features

### 1. 🌾 Complete BRRI Rice & Crop Taxonomy
- **139 Official BRRI Rice Varieties**: Exhaustive profiles for Aus, Aman, and Boro seasons including life duration (days), average yield (t/ha), maximum yield, grain traits, and special attributes (salinity tolerance, submergence survival, zinc enrichment, drought resistance).
- **Core Agricultural Crops**: Detailed profiles for cereals, pulses, oilseeds, vegetables, spices, cash crops, and fiber crops.
- **Phenological Growth Stages**: Precise calendar-based breakdown from seedbed preparation to transplanting, tillering, panicle initiation, flowering, grain filling, and harvest.

### 2. 🧠 Cross-Lingual RAG Engine (Qwen 2.5 3B)
- **Multilingual Query Ingestion**: Understands queries typed or spoken in **Bangla (বাংলা)**, **Banglish (phonetic)**, and **English**.
- **Dense Vector Search**: Powered by **ChromaDB** containing **24,178 vectorized knowledge chunks** mined from BRRI, BARI, DAE, FAO, and BAMIS publications.
- **Default Structured English Responses**: Answers in crisp, English agronomic format by default for universal clarity, with automatic switching to Bangla whenever explicitly instructed (*"বাংলায় বলো"*).
- **Conversational Memory**: Maintains multi-turn dialog context (last 8 conversation turns) for natural follow-up questions.

### 3. 🎙️ Continuous Conversational Voice Input
- **Web Speech API Integration**: Seamless speech-to-text with bilingual speech detection (`bn-BD` / `en-US`).
- **3.0-Second Conversational Silence Debounce**: Prevents premature cutoff when users pause to think or breathe.
- **Socket Keep-Alive & Auto-Recovery**: Prevents Chromium socket disconnects with an asynchronous keep-alive restart mechanism.

### 4. 🗺️ Divisional Agro-Ecological Mapping
- Maps soil suitability, average precipitation, flooding susceptibility, and drought risk factors across all 8 divisions:
  - **Rangpur & Rajshahi**: Northern drought and cold-wave resilient cultivation.
  - **Sylhet & Mymensingh**: Flash-flood and Haor-adapted varieties (e.g., BRRI dhan29, BRRI dhan88).
  - **Khulna & Barisal**: Southern coastal salinity and tidal submergence varieties (e.g., BRRI dhan67, BRRI dhan73, BRRI dhan97).
  - **Dhaka & Chattogram**: High-yield central basin and hilly tract management.

### 5. 🩺 Pathology, Pest & Fertilizer Diagnostic Engine
- Diagnostic advisory for common agricultural pests and diseases (Blast, Bacterial Leaf Blight, Sheath Blight, Brown Planthopper, Stem Borer, Cutworm).
- Actionable treatment plans specifying active chemical ingredients, organic alternatives, and prevention protocols.

---

## 🏛️ Enterprise Software Architecture

> 💡 **Interactive Archify Architecture Diagram**: An interactive, explorable standalone architecture diagram generated with [Archify](https://github.com/tt-a1i/archify) is included in the repository at [`architecture-runtime.html`](architecture-runtime.html) (specification: [`architecture-runtime.json`](architecture-runtime.json)). Open it in any browser to toggle guided view overlays and inspect component boundaries.

```mermaid
flowchart TD
    %% ========================================================
    %% 1. USER LAYER
    %% ========================================================
    subgraph L1 ["1. USER & CLIENT LAYER"]
        direction LR
        U_Farmers["👨‍🌾 Farmers & Extension Officers"]
        U_Researchers["🔬 Agronomists & Researchers"]
        U_Admins["🛡️ Authorized Administrators"]
        Devices["📱 Devices: Web Browser / Mobile Responsive"]
        U_Farmers --> Devices
        U_Researchers --> Devices
        U_Admins --> Devices
    end

    %% ========================================================
    %% 2. FRONTEND LAYER
    %% ========================================================
    subgraph L2 ["2. FRONTEND LAYER (Next.js 14 / TypeScript / Tailwind CSS / Framer Motion)"]
        direction TB
        subgraph F_Public ["Public Web Portal"]
            F_Home["Homepage Hero & Telemetry"]
            F_Explorer["Crop Explorer & 8-Division AEZ Filter"]
            F_Detail["Crop Detail Pages & Growth Timeline"]
            F_Search["Search Engine & Taxonomy Bar"]
            F_Chat["AI Chat Interface (Web Speech + 3s Debounce)"]
        end
        subgraph F_Admin ["Admin Dashboard (Protected)"]
            F_Auth["Admin Login & Session Verify"]
            F_CropMgmt["Crop Management (CRUD)"]
            F_DocMgmt["Document & Knowledge Base CMS"]
            F_ImgMgmt["Image Gallery & Upload Console"]
        end
    end

    Devices -->|Browse / Search| F_Public
    Devices -->|Manage / Admin| F_Admin

    %% ========================================================
    %% 3. BACKEND APPLICATION LAYER
    %% ========================================================
    subgraph L3 ["3. BACKEND APPLICATION LAYER (Python FastAPI :8000)"]
        direction TB
        subgraph B_Gateway ["API Gateway & Middlewares"]
            B_Routes["REST API Routing Engine"]
            B_Val["Pydantic v2 Request Validation"]
            B_AuthMid["Supabase Auth Token Middleware"]
            B_CORS["CORS & Origin Policies"]
        end

        subgraph B_Services ["Core Microservices"]
            S_Crop["Crop Service<br/>• Get All Crops<br/>• Search & Filter<br/>• Phenology & Stages"]
            S_Admin["Admin Service<br/>• Create / Update / Delete<br/>• Document CMS<br/>• Sync Triggers"]
            S_AI["AI / RAG Service<br/>• Multilingual Intent Gate<br/>• Context Retriever<br/>• LLM Streamer"]
            S_Image["Image Service<br/>• Upload Processor<br/>• URL Resolver"]
            S_Weather["Weather Intelligence<br/>• Agro-climatic Analysis<br/>• Seasonal Advisories"]
        end

        B_Routes --> S_Crop
        B_Routes --> S_Admin
        B_Routes --> S_AI
        B_Routes --> S_Image
        B_Routes --> S_Weather
    end

    F_Public -->|REST / SSE Streaming| B_Gateway
    F_Admin -->|Authenticated REST| B_Gateway

    %% ========================================================
    %% 4. AUTHENTICATION & SECURITY
    %% ========================================================
    subgraph L4 ["4. AUTHENTICATION & SECURITY (Supabase Auth)"]
        A_Auth["Supabase Auth Engine<br/>• User Authentication<br/>• Admin RBAC Verification<br/>• JWT Tokens & Sessions"]
    end

    F_Auth -->|Verify Credentials| A_Auth
    B_AuthMid -.->|Validate JWT| A_Auth

    %% ========================================================
    %% 5 & 6. DATABASE & STORAGE LAYER
    %% ========================================================
    subgraph L5_6 ["5 & 6. PERSISTENCE LAYER (Supabase Cloud)"]
        direction LR
        subgraph L5 ["5. PostgreSQL Database"]
            T_Crops["crops table (Taxonomy, Soil, Climate)"]
            T_Varieties["crop_varieties table (139 BRRI Varieties)"]
            T_Stages["growth_stages table (Phenological Orders)"]
            T_Diseases["diseases table (Pathology & Treatment)"]
            T_Regions["regions table (8 Divisions & AEZs)"]
            T_Future["Future: users, admins, conversations, feedback"]
        end
        subgraph L6 ["6. Object Storage"]
            Store_Images["Crop Images Bucket (Main & Gallery)"]
            Store_Docs["Knowledge Documents Bucket (PDFs & Guides)"]
        end
    end

    S_Crop -->|PostgREST SQL| L5
    S_Admin -->|CRUD SQL| L5
    S_Image -->|Upload & Retrieve| Store_Images
    S_Admin -->|Archive PDFs| Store_Docs

    %% ========================================================
    %% 7. KNOWLEDGE COLLECTION PIPELINE
    %% ========================================================
    subgraph L7 ["7. KNOWLEDGE COLLECTION PIPELINE (Crawler Service - Python)"]
        direction TB
        subgraph C_Collectors ["Source Crawlers"]
            C_BRRI["BRRI Crawler"]
            C_BARI["BARI Crawler"]
            C_DAE["DAE Crawler"]
            C_BARC["BARC Crawler"]
            C_BAMIS["BAMIS Crawler"]
            C_FAO["FAO Crawler"]
        end
        C_Discovery["Search & Document Discovery Engine"]
        C_Downloader["Downloader & Deduplication (MD5)"]
        C_Processor["PDF Processing (Text Extract, OCR, Language Detect, Cleaner)"]
        C_Classifier["Document Classifier (Crop, Disease, Soil, Fertilizer, Climate)"]
        C_Meta["Metadata Generator (Quality Score, Source, Taxon)"]
        C_KB["Clean Knowledge Base Corpus"]

        C_Collectors --> C_Discovery --> C_Downloader --> C_Processor --> C_Classifier --> C_Meta --> C_KB
    end

    %% ========================================================
    %% 8 & 9. AI / RAG LAYER & FEATURES
    %% ========================================================
    subgraph L8_9 ["8 & 9. AI / RAG LAYER & ADVANCED INTELLIGENCE"]
        direction TB
        subgraph RAG_Engine ["RAG Processing Engine"]
            R_Chunk["Context Chunker (Semantic Boundaries)"]
            R_Embed["Embedding Generator (BAAI bge-m3 / MiniLM)"]
            R_VectorDB[("ChromaDB Vector Store<br/>24,178 Dense Vectors")]
            R_Retrieve["Similarity Search & Context Re-Ranker"]
        end

        subgraph LLM_Tier ["Local Inference Layer"]
            Ollama["Ollama Engine (:11434)"]
            Models["Models: Qwen 2.5 (3B) / Llama 3.1"]
            Ollama --- Models
        end

        subgraph Future_AI ["Advanced AI Modules"]
            AI_Vision["Computer Vision: Leaf Disease Detection (YOLO / EfficientNet)"]
            AI_Rec["Recommendation Engine (Soil + Region + Season -> Best Variety)"]
        end
    end

    C_KB --> R_Chunk --> R_Embed --> R_VectorDB
    S_AI -->|Embed & Search| R_VectorDB
    R_VectorDB -->|Retrieve Top-K Chunks| R_Retrieve
    R_Retrieve -->|Augmented Prompt| Ollama
    Ollama -->|Token Stream| S_AI

    %% ========================================================
    %% 10. EXTERNAL SERVICES
    %% ========================================================
    subgraph L10 ["10. EXTERNAL SOURCES & DEPLOYMENT TARGETS"]
        Ext_Sources["National Agri Sources: BRRI, BARI, DAE, BARC, BAMIS, FAO"]
        Ext_Weather["Weather API: BAMIS / Open-Meteo"]
        Dep_Vercel["Frontend: Vercel (Edge CDN)"]
        Dep_Backend["Backend: Docker Container / Cloud VPS"]
        Dep_Supa["Database: Supabase Managed Cloud"]
    end

    Ext_Sources -.-> C_Collectors
    Ext_Weather -.-> S_Weather
    F_Public -.-> Dep_Vercel
    B_Gateway -.-> Dep_Backend
    L5_6 -.-> Dep_Supa

    %% Styling and Theme
    classDef client fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef frontend fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef backend fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef database fill:#3b0764,stroke:#c084fc,stroke-width:2px,color:#f8fafc;
    classDef ai fill:#701a75,stroke:#f472b6,stroke-width:2px,color:#f8fafc;
    classDef pipeline fill:#451a03,stroke:#fbbf24,stroke-width:2px,color:#f8fafc;

    class L1 client;
    class L2 frontend;
    class L3 backend;
    class L4,L5_6 database;
    class L7 pipeline;
    class L8_9 ai;
```

---

## 🔁 End-to-End Enterprise Data Flows

### Flow 1: Knowledge Ingestion & Vector Indexing Pipeline
```
[Agri Research Portals: BRRI / BARI / DAE / FAO]
       │
       ▼ (Automated Discovery & Crawl)
[Crawler Service (Python Requests / BeautifulSoup)]
       │
       ▼ (Validate & Deduplicate)
[PDF Processor (pypdf Text Extraction + OCR + Unicode Normalization)]
       │
       ▼ (Semantic Classification: Crop, Disease, Fertilizer, Soil)
[Clean Knowledge Base Corpus]
       │
       ▼ (Semantic Boundary Chunking)
[Embedding Model: BAAI bge-m3 / all-MiniLM-L6-v2]
       │
       ▼ (HNSW Vector Indexing)
[ChromaDB / pgvector (24,178 Knowledge Vectors)]
```

### Flow 2: Real-Time User Question & RAG Inference Flow
```
[Farmer / Agronomist]
       │ (Spoken Audio / Typed Text in Bangla or English)
       ▼
[Web Speech API (3.0s Silence Debounce) / Next.js Assistant UI]
       │ (POST /api/assistant/chat/stream)
       ▼
[FastAPI Gateway (Uvicorn :8000)]
       │ (Cross-Lingual Intent & Language Evaluator)
       ▼
[RAG Orchestrator (rag_service.py + 8-Turn Memory)]
       │ (Dense Vector Search)
       ▼
[ChromaDB Vector Store (Retrieve Top-K Scored Chunks)]
       │ (Augmented Prompt + Variety Metadata)
       ▼
[Local Ollama Daemon (:11434) Running Qwen 2.5 (3B)]
       │ (Server-Sent Events Token Stream)
       ▼
[Next.js Assistant UI] ────► [Farmer Receives Actionable Agronomic Guidance]
```

### Flow 3: Crop Taxonomy & Agro-Ecological Browsing Flow
```
[User] ──► [Next.js Crop Explorer (/crops)]
                 │ (HTTP GET /crops?division=Rangpur&season=Aman)
                 ▼
           [FastAPI Crop Service (routes/crops.py)]
                 │ (PostgREST Query)
                 ▼
           [Supabase PostgreSQL (crops, crop_varieties, growth_stages)]
                 │ (Structured JSON Taxonomy & Durations)
                 ▼
           [Interactive Next.js Grid with 139 BRRI Varieties & Stages]
```

### Flow 4: Admin Management & Security RBAC Flow
```
[Administrator] ──► [Admin Console (/login)]
                          │ (Submit Credentials)
                          ▼
                    [Supabase Auth (Verify role = 'admin' & Issue JWT)]
                          │
                          ├─────────────► [Access Admin Dashboard]
                          │                     │
                          │                     ▼ (CRUD Operation / Media Upload)
                          ▼               [FastAPI Admin Service (routes/admin.py)]
                    [Supabase Storage]          │ (SQL Insert / Update)
                    (Upload Crop Images)        ▼
                                          [Supabase PostgreSQL]
```

---

## 🔄 Cross-Lingual RAG Pipeline Workflow

How natural language questions in Bangla or English are converted into precise agronomic advice:

```mermaid
flowchart LR
    A["Farmer/User Query<br/>(Bangla, Banglish, English)"] --> B["Intent & Topic Evaluator"]
    B -->|Greeting / Non-Agri| C["Direct Conversational Response"]
    B -->|Agricultural Query| D["Cross-Lingual Embedding<br/>(ChromaDB Vector Search)"]
    D --> E["Top-K Agronomic Chunks Retrieval<br/>(Score Reranking)"]
    E --> F["Agronomic Context Builder<br/>+ BRRI Variety Metadata"]
    F --> G["Prompt Construction<br/>(English Default Directives)"]
    G --> H["Local Ollama Engine<br/>(Qwen 2.5 3B Inference)"]
    H --> I["Real-Time Token Stream / JSON<br/>(Advice + Source Citations)"]
```

---

## 🎙️ Continuous Voice Input Flow

The voice input pipeline features continuous audio recording, speech transcript accumulation, and a 3.0-second silence debounce timer:

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as Farmer / Agronomist
    participant Mic as Browser Microphone
    participant Speech as Web Speech API
    participant Debounce as Silence Debounce (3.0s)
    participant Client as Next.js Assistant
    participant API as FastAPI Backend (/stream)

    Farmer->>Mic: Clicks Mic & Begins Speaking (Bangla/English)
    Mic->>Speech: Audio Stream Ingest
    Speech->>Client: Interim Transcript Real-time Update
    Note over Client: accumulatedTranscriptRef updates
    Farmer->>Mic: Pauses to think / breathe (1-2s pause)
    Speech-->>Debounce: Silence timer starts (3.0s window)
    Note over Debounce: Prevents premature cutoff
    Farmer->>Mic: Resumes speaking before timer expires
    Debounce->>Debounce: Timer resets upon new audio
    Farmer->>Mic: Finishes speaking (3s silence elapsed)
    Debounce->>Client: Finalized Transcript Trigger
    Client->>API: POST /api/assistant/chat/stream
    API-->>Client: Real-time Server-Sent Events (SSE) Tokens
    Client-->>Farmer: Animated Response Displayed
```

---

## 🗄️ Relational Database Schema

The platform stores structured crop profiles and research documents in Supabase PostgreSQL:

```mermaid
erDiagram
    CROPS ||--o{ GROWTH_STAGES : "has stages"
    CROPS ||--o{ DISEASES : "suffers from"
    CROPS ||--o{ REGIONS : "grown in"
    CROP_VARIETIES }|--|| CROPS : "variety of"
    KNOWLEDGE_DOCUMENTS ||--o{ CROP_VARIETIES : "cites"

    CROPS {
        bigint id PK
        text crop_name
        text bangla_name
        text category
        text scientific_name
        text season
        text soil_type
        numeric optimal_temp_min
        numeric optimal_temp_max
        numeric rainfall_min
        numeric rainfall_max
        numeric duration_days_min
        numeric duration_days_max
        text image_url
    }

    CROP_VARIETIES {
        bigint id PK
        text document_id UK
        text variety_name
        text variety_name_bn
        text crop
        text category
        text season
        text source
        integer page_count
    }

    GROWTH_STAGES {
        bigint id PK
        bigint crop_id FK
        text stage_name
        integer stage_order
        integer duration_days
        text description
        text water_requirement
        text fertilizer_requirement
    }

    DISEASES {
        bigint id PK
        bigint crop_id FK
        text disease_name
        text bangla_name
        text symptoms
        text chemical_control
        text organic_control
        text prevention
    }

    REGIONS {
        bigint id PK
        bigint crop_id FK
        text region_name
        text division
        text suitability_level
    }
```

---

## 📂 Project Directory Structure

```text
Bangladesh Crop Intelligence Assistant/
├── backend/                              # FastAPI Microservice
│   ├── data/                             # JSON databases & Supabase migration SQL
│   │   ├── bangladesh_crop_database_v2.json
│   │   └── supabase_knowledge_sync.sql   # SQL migration (139 varieties + tables)
│   ├── routes/                           # FastAPI Router endpoints
│   │   ├── crops.py                      # /crops, /categories, /search
│   │   └── assistant.py                  # /api/assistant/chat, /stream, /health
│   ├── services/                         # Core Business & AI Logic
│   │   ├── llm_client.py                 # Ollama Qwen 2.5 client with retry & stream
│   │   ├── rag_service.py                # Cross-lingual RAG retrieval & prompt engine
│   │   ├── supabase_client.py            # Supabase database connection pool
│   │   └── weather_service.py            # Real-time agro-meteorological service
│   ├── .env.example                      # Backend environment variable template
│   ├── main.py                           # FastAPI application entrypoint
│   └── requirements.txt                  # Backend Python dependencies
│
├── frontend/                             # Next.js 14 Frontend Platform
│   ├── public/                           # Static assets (logo.png, icons)
│   ├── src/
│   │   ├── app/                          # Next.js App Router Pages
│   │   │   ├── layout.tsx                # Global Root Layout & Favicon
│   │   │   ├── page.tsx                  # Homepage Hero & Feature Showcase
│   │   │   ├── assistant/page.tsx        # AI Assistant Chat & Voice Interface
│   │   │   ├── crops/page.tsx            # All Crops Catalog & Search
│   │   │   ├── crops/[name]/page.tsx     # Dynamic Individual Crop Profile
│   │   │   └── login/page.tsx            # Protected Personnel Access
│   │   ├── components/                   # Reusable UI Components
│   │   │   ├── Navbar.tsx                # Navigation bar with dynamic telemetry
│   │   │   └── Footer.tsx                # Informational footer & AEZ division tags
│   │   ├── context/                      # State Management (AuthContext)
│   │   └── lib/                          # Utility & API Client bindings
│   ├── .env.example                      # Frontend environment variable template
│   ├── package.json                      # Node.js dependencies
│   └── tailwind.config.ts                # Custom Tailwind design tokens
│
├── knowledge_base/                       # Curated Agronomic Corpus
│   ├── chunks/chunks.json                # Pre-processed chunks with citations
│   ├── processed/                        # Cleaned text corpus from research papers
│   └── metadata/                         # Document manifests & indexing hashes
│
├── vector_store/                         # ChromaDB Vector Store Tools
│   ├── embedding_service.py              # Sentence transformer embedding pipeline
│   ├── indexer.py                        # Batch chunk vectorization script
│   └── main.py                           # CLI for indexing knowledge_base
│
├── document_processor/                   # PDF & Document Extraction Pipeline
│   ├── extractor.py                      # Text & table extraction from BRRI PDFs
│   ├── chunker.py                        # Context-aware semantic text chunking
│   └── cleaner.py                        # Banglish/Bangla Unicode normalizer
│
├── .env.example                          # Root environment template
├── .gitignore                            # Production git ignore (secrets, venvs, DBs)
├── README.md                             # Comprehensive Platform Documentation
└── requirements.txt                      # Complete Root Python dependencies
```

---

## 🚀 Step-by-Step Installation & Setup

### Prerequisites
- **Python**: `3.10` or higher (`3.11` recommended)
- **Node.js**: `18.17.0` or higher (`v20.x LTS` recommended)
- **Ollama**: Installed from [ollama.ai](https://ollama.ai/)
- **Git**: Installed and configured

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/bangladesh-crop-intelligence.git
cd bangladesh-crop-intelligence
```

---

### Step 2: Configure and Start the Local LLM (Ollama)
The assistant uses the high-efficiency **Qwen 2.5 (3B)** model, ideal for fast inference:
```bash
# Pull the 3B parameter model (~2.0 GB)
ollama pull qwen2.5:3b

# Start Ollama service (defaults to http://localhost:11434)
ollama serve
```

---

### Step 3: Backend Setup (FastAPI)
1. Navigate to the backend directory and set up a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your `.env` file:
   ```bash
   cp .env.example .env
   ```
   Open `backend/.env` and insert your Supabase credentials:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   OLLAMA_BASE_URL=http://localhost:11434
   LLM_MODEL=qwen2.5:3b
   OLLAMA_TIMEOUT=120.0
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

5. Launch the FastAPI server:
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *The backend will be available at `http://127.0.0.1:8000` (API docs at `http://127.0.0.1:8000/docs`).*

---

### Step 4: Database Setup (Supabase)
1. Go to your [Supabase Dashboard](https://supabase.com/dashboard) and open the **SQL Editor**.
2. Open [`backend/data/supabase_knowledge_sync.sql`](backend/data/supabase_knowledge_sync.sql), copy its contents, and execute the query.
3. This creates all relational tables (`crops`, `growth_stages`, `diseases`, `regions`, `crop_varieties`, `knowledge_documents`) and populates all **139 BRRI rice varieties**.

---

### Step 5: Frontend Setup (Next.js)
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Configure your `.env.local` file:
   ```bash
   cp .env.example .env.local
   ```
   Configure `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
   NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. Launch the frontend development server:
   ```bash
   npm run dev
   ```
   *Open [http://localhost:3000](http://localhost:3000) in your browser.*

---

## 📡 API Reference

### Health & Telemetry
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root API status and service metadata |
| `GET` | `/api/assistant/health` | LLM connectivity, model name, and vector count |

### Crop Intelligence & Taxonomy
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/crops` | List all 25 crops with seasonal and divisional filters |
| `GET` | `/crops/{crop_name}` | Detailed crop record with growth stages and diseases |
| `GET` | `/categories/{category}` | Filter crops by category (cereals, pulses, etc.) |
| `GET` | `/search?query={query}` | Search crops by Bangla or English name |

### AI Assistant & RAG
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/assistant/chat` | Standard JSON response for single-turn or multi-turn queries |
| `POST` | `/api/assistant/chat/stream` | Server-Sent Events (SSE) streaming token output |

#### Sample Request (`POST /api/assistant/chat`):
```json
{
  "message": "বোরো মৌসুমে কোন ধানের জাত ভালো?",
  "history": []
}
```

#### Sample Response:
```json
{
  "reply": "For the Boro season in Bangladesh, high-yielding and resilient BRRI rice varieties include:\n\n1. BRRI dhan28: Early maturing (140 days) with high yield potential (5.0-6.0 t/ha).\n2. BRRI dhan29: High yielding (7.5 t/ha) standard for irrigated conditions.\n3. BRRI dhan88: Premium grain quality and lodging resistance.\n4. BRRI dhan89: High yielding (8.0 t/ha) replacement for BRRI dhan29.\n\nFor saline coastal belts, BRRI dhan67 and BRRI dhan97 are highly recommended.",
  "sources": [
    {
      "title": "BRRI Rice Knowledge Bank - Boro Varieties",
      "category": "cereals",
      "source": "BRRI"
    }
  ]
}
```

---

## 🛡️ Production & Security Checklist

Before deploying this platform to public cloud environments (e.g., Vercel + AWS/Fly.io/Render):
1. **Never commit `.env` or `.env.local`**: Ensure private keys, Supabase Service Role keys, and database passwords are only injected via cloud environment variable secrets.
2. **Restrict CORS**: In `backend/main.py` and `backend/.env`, set `CORS_ORIGINS` to your production frontend domain (e.g. `https://cropintel-bd.com`).
3. **ChromaDB Persistence**: In containerized environments, mount a persistent Docker volume for `knowledge_base/chroma_db/` or connect to a managed vector service.
4. **Ollama Deployment**: Host Ollama on a GPU-enabled VM (e.g., RunPod, AWS EC2 g4dn) and point `OLLAMA_BASE_URL` to your private microservice URL.

---

## 📚 Acknowledgements & Data Sources

This platform builds upon scientific research and open agronomic data provided by:
- **Bangladesh Rice Research Institute (BRRI)** — Rice variety data, duration, yield, and pathology guidelines.
- **Department of Agricultural Extension (DAE)** — Fertilizer schedules and regional agro-ecological advisories.
- **Bangladesh Agricultural Research Institute (BARI)** — Cash crops, pulses, and oilseeds data.
- **Bangladesh Agro-Meteorological Information System (BAMIS)** — Agro-climatic risk zoning.
- **Food and Agriculture Organization (FAO)** — Soil suitability and crop calendar standards.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
