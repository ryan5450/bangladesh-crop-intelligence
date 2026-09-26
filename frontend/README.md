# Bangladesh Crop Intelligence Assistant - Frontend

A modern, high-performance agricultural intelligence web application built with **Next.js 14**, **TypeScript**, **Tailwind CSS**, **Framer Motion**, and **Lucide Icons**. It connects seamlessly to the FastAPI backend microservice to deliver precision agronomic data across Bangladesh.

---

## 1. Features

- **AgriTech Noir Design System**: Premium dark aesthetic (`#060907`), glassmorphism panels, ambient radial glows, and agriculture emerald accents.
- **Homepage**:
  - Hero banner with headline, AI indicator, and quick statistics (25+ crops, 130+ growth phases, 50+ diseases, 8 divisions).
  - Prominent debounced search bar with live dropdown suggestions (`GET /search?query=...`).
  - Interactive category filter chips (`All`, `Cereal`, `Fruit`, `Vegetable`, `Pulse`, `Cash Crop`, `Spice`).
  - Featured crops grid with hover motion and visual badges.
- **All Crops Listing (`/crops`)**:
  - Full catalog of all 25 crops.
  - Search filter, category filters, and sorting by name or category.
  - Result count indicators and loading skeletons.
- **Dynamic Crop Details Page (`/crops/[name]`)**:
  - Scientific name, duration, and fertilizer regimen.
  - 6 Core Agronomic Metrics (Growing Season, Planting Window, Harvest Time, Water, Soil, Duration).
  - **`GrowthTimeline`**: Ordered chronological development stages (e.g. Seedling to Harvest).
  - **`DiseaseCard`**: Pathology cards with alert icons and risk indicators.
  - **Divisional Suitability**: Regional pills highlighting suitable growing districts.
- **System Health Monitor**:
  - Sticky `Navbar` with automatic polling of FastAPI backend status (`API Online` / `API Disconnected`).

---

## 2. Directory Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx            # Global layout, ambient lighting & fonts
│   │   ├── globals.css           # Tailwind directives & dark glass utility classes
│   │   ├── page.tsx              # Homepage
│   │   └── crops/
│   │       ├── page.tsx          # All Crops catalog
│   │       └── [name]/page.tsx   # Dynamic crop detail view
│   ├── components/
│   │   ├── Navbar.tsx            # Sticky header with API health indicator
│   │   ├── Footer.tsx            # Agricultural info & credits
│   │   ├── CropCard.tsx          # Glass card with category badges & hover motion
│   │   ├── SearchBar.tsx         # Debounced live search with dropdown suggestions
│   │   ├── GrowthTimeline.tsx    # Chronological step timeline for growth stages
│   │   ├── DiseaseCard.tsx       # Pathology alert card
│   │   └── LoadingSkeleton.tsx   # Glass shimmer loading states
│   └── lib/
│       ├── api.ts                # Axios client for FastAPI endpoints
│       └── types.ts              # TypeScript interfaces
├── .env.local                    # NEXT_PUBLIC_API_URL
├── tailwind.config.ts            # Extended dark glass & emerald color palette
├── tsconfig.json                 # TypeScript compiler configuration
└── package.json                  # Dependencies
```

---

## 3. Getting Started

### Prerequisites
- Node.js 18.x or newer (Tested on Node v24)
- npm 9.x or newer
- FastAPI backend running at `http://127.0.0.1:8000`

### Step 1: Install Dependencies
```powershell
cd "D:\Bangladesh Crop Intelligence Assistant\frontend"
npm install
```

### Step 2: Environment Configuration
Check `.env.local` inside `frontend/`:
```dotenv
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Step 3: Run the Development Server
```powershell
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 4. Production Build

To test or deploy an optimized production build:

```powershell
npm run build
npm start
```

