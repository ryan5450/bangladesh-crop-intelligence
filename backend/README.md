# Bangladesh Crop Intelligence API - Milestone 2

A modular FastAPI backend providing agricultural intelligence for crops in Bangladesh. The API integrates with Supabase PostgreSQL to deliver basic crop data combined with growth stages, common crop diseases, and suitable growing regions.

---

## 1. Project Structure

```text
backend/
├── main.py                # FastAPI application entrypoint, CORS & middleware
├── supabase_client.py     # Centralized Supabase client with URL normalization
├── routes/
│   ├── __init__.py
│   └── crops.py           # Crop endpoints, Pydantic schemas & relational aggregations
├── data/
│   └── bangladesh_crop_database_v2.json  # Raw source data
├── import_data.py         # JSON-to-database ETL script
├── requirements.txt       # Dependencies
├── .env                   # Configuration & API credentials (do not commit)
└── README.md              # Documentation
```

---

## 2. Installation

From the `backend` directory:

### Step 1: Create and activate virtual environment

On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(If script execution is disabled on Windows, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first)*

On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 3. Environment Setup

Ensure a `.env` file exists in the `backend/` directory with your Supabase credentials:

```dotenv
SUPABASE_URL=https://braiwlsjyczorxuxtifi.supabase.co
SUPABASE_KEY=your-supabase-key-here
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,*
```

- **`SUPABASE_URL`**: Your base Supabase project URL.
- **`SUPABASE_KEY`**: Your Supabase API key (`anon` key for read access with RLS enabled, or `service_role` key).
- **`CORS_ORIGINS`**: Comma-separated list of permitted frontend origins.

---

## 4. Running the Server

Start the FastAPI server with auto-reload:

```powershell
uvicorn main:app --reload
```

The API will be live at:
- **Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 5. API Endpoints

### 1. Root Health Check
- **`GET /`**
- **Description**: Verify API status and service information.
- **Example Request**:
  ```powershell
  curl.exe http://127.0.0.1:8000/
  ```

---

### 2. Get All Crops
- **`GET /crops`**
- **Description**: Returns all crops as compact summaries (`id`, `crop_name`, `category`).
- **Example Request**:
  ```powershell
  curl.exe http://127.0.0.1:8000/crops
  ```
- **Example Response**:
  ```json
  [
    {
      "id": 30,
      "crop_name": "Mango",
      "category": "Fruit"
    },
    {
      "id": 28,
      "crop_name": "Aman Rice",
      "category": "Cereal"
    }
  ]
  ```

---

### 3. Get Complete Crop Information
- **`GET /crops/{crop_name}`**
- **Description**: Returns complete information for a specific crop (case-insensitive). Dynamically aggregates ordered growth stages from `growth_stages`, disease lists from `diseases`, and region lists from `regions`.
- **Example Request**:
  ```powershell
  curl.exe http://127.0.0.1:8000/crops/Mango
  ```
- **Example Response**:
  ```json
  {
    "id": 30,
    "crop_name": "Mango",
    "scientific_name": "Mangifera indica",
    "category": "Fruit",
    "growing_season": "Summer / Pre-monsoon harvest",
    "planting_time": "June-August (monsoon season grafting/planting)",
    "harvest_time": "May-July",
    "soil_requirement": "Deep, well-drained alluvial or sandy loam soil",
    "water_requirement": "Moderate; irrigation beneficial during fruit development",
    "fertilizer": "Compost, urea, TSP, MOP, micronutrients",
    "image": "assets/crops/mango.jpg",
    "crop_duration_days": "Perennial (productive 30+ years)",
    "growth_stages": [
      {
        "stage_number": 1,
        "stage_name": "Plant establishment"
      },
      {
        "stage_number": 2,
        "stage_name": "Vegetative growth"
      },
      {
        "stage_number": 3,
        "stage_name": "Flowering / Panicle emergence"
      },
      {
        "stage_number": 4,
        "stage_name": "Fruit set"
      },
      {
        "stage_number": 5,
        "stage_name": "Fruit development"
      },
      {
        "stage_number": 6,
        "stage_name": "Fruit maturation"
      },
      {
        "stage_number": 7,
        "stage_name": "Harvest"
      }
    ],
    "diseases": [
      "Anthracnose",
      "Powdery mildew",
      "Fruit fly"
    ],
    "regions": [
      "Rajshahi",
      "Chapainawabganj",
      "Naogaon",
      "Dinajpur"
    ]
  }
  ```
- **Status Codes**:
  - `200 OK`: Crop found.
  - `404 Not Found`: If crop does not exist (e.g. `{"detail": "Crop 'xyz' not found."}`).

---

### 4. Search Crops
- **`GET /search?query={query}`**
- **Description**: Performs a case-insensitive substring search on crop names.
- **Example Request**:
  ```powershell
  curl.exe "http://127.0.0.1:8000/search?query=rice"
  ```
- **Example Response**:
  ```json
  [
    {
      "id": 28,
      "crop_name": "Aman Rice",
      "category": "Cereal"
    },
    {
      "id": 29,
      "crop_name": "Aus Rice",
      "category": "Cereal"
    },
    {
      "id": 27,
      "crop_name": "Boro Rice",
      "category": "Cereal"
    }
  ]
  ```

---

### 5. Filter Crops by Category
- **`GET /categories/{category}`**
- **Description**: Returns all crops belonging to a specific category (case-insensitive).
- **Example Request**:
  ```powershell
  curl.exe http://127.0.0.1:8000/categories/Fruit
  ```
- **Example Response**:
  ```json
  [
    {
      "id": 31,
      "crop_name": "Banana",
      "category": "Fruit"
    },
    {
      "id": 33,
      "crop_name": "Guava",
      "category": "Fruit"
    },
    {
      "id": 32,
      "crop_name": "Jackfruit",
      "category": "Fruit"
    },
    {
      "id": 34,
      "crop_name": "Litchi",
      "category": "Fruit"
    },
    {
      "id": 30,
      "crop_name": "Mango",
      "category": "Fruit"
    }
  ]
  ```

---

## 6. Error Handling

- **`400 Bad Request`**: Raised for missing or invalid path/query parameters.
- **`404 Not Found`**: Raised when a requested crop or entity does not exist.
- **`500 / 503 Server / Service Unavailable`**: Handled gracefully if database connection or PostgREST service errors occur.
