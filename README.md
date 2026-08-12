# Uplift - Agentic AI Government Scheme Recommender

**Uplift** is an AI-powered government scheme discovery and recommendation platform designed to help citizens across India automatically discover, evaluate eligibility for, and directly apply to central and state government schemes.

---

## 🚀 Complete End-to-End System Workflow

The diagram below illustrates how user interactions flow through the **React Frontend**, **FastAPI Backend**, **Gemini 2.5 Flash Agentic Pipeline**, and **Data Ingestion Engines**:

```mermaid
flowchart TD
    %% User Layer
    subgraph User Interface (Frontend)
        A[User Input: Chat Query or Search] --> B[React + Vite App]
        B --> C1[Chat View / Chat.jsx]
        B --> C2[Explorer Directory / Explorer.jsx]
    end

    %% API Layer
    subgraph FastAPI Backend Layer
        C1 -->|POST /api/v1/chat/| D[Chat Router]
        C2 -->|GET /api/v1/schemes/| E[Schemes Router]
        F1[Paste Scheme URL] -->|POST /api/v1/schemes/scrape| G[Web Scraper Service]
        F2[Upload Scheme PDF] -->|POST /api/v1/schemes/ingest-pdf| H[PDF Ingestion Service]
    end

    %% Agentic Workflow Layer
    subgraph 5-Stage Agentic Workflow (app/workflows/agent_workflow.py)
        D --> W1[1. Profile Extraction Node]
        W1 -->|Gemini 2.5 Flash| W2[2. Candidate Scheme Retrieval Node]
        W2 --> W3[3. Eligibility Rules Evaluator Node]
        W3 -->|Logical Operators: lte, gte, in, equals| W4[4. Reflection Agent Node]
        W4 -->|Reasoning & Step-by-Step Focus| W5[5. Response Formatting Node]
    end

    %% Data Layer
    subgraph Data & Storage Layer
        W2 <--> DB[(schemes.json - 172 Schemes)]
        G --> DB
        H --> DB
    end

    %% Response Layer
    W5 -->|JSON Response| C1
    C1 -->|Renders Matched Schemes & Forms| UI1[Step-by-Step Forms & Apply Online Link]
    E -->|Returns Schemes List| C2
```

---

## 🔄 Step-by-Step Workflows

### 1. Conversational Chat Assistant Workflow
```text
[User Prompt] ➔ [Profile Extraction] ➔ [Candidate Retrieval] ➔ [Rule Evaluation] ➔ [Reflection Agent] ➔ [Interactive UI]
```
1. **User Prompting**: The citizen types a query in natural language (e.g. *"I am a 20 year old student from Maharashtra with family income of 2 Lakhs"*).
2. **Entity Extraction**: **Gemini 2.5 Flash** extracts key user attributes (`age`, `state`, `occupation`, `education`, `income`, `gender`, `category`) and normalizes Indian financial shorthand (`2 Lakh` $\rightarrow$ `250000.0`).
3. **Turn-by-Turn Context Merging**: The backend merges newly extracted details into `existing_profile` turn-by-turn.
4. **Candidate Retrieval**: Pre-filters schemes from `data/schemes.json` based on state and target group.
5. **Rules Engine Evaluation**: Evaluates condition rules (`equals`, `lte`, `gte`, `in`) against the user profile:
   - **Eligible Schemes**: Automatically matched.
   - **Unknown Eligibility**: Identifies missing parameters needed to confirm eligibility.
6. **Reflection Agent**: Crafts empathetic conversational AI guidance and focuses prompt text on the **first missing attribute** (`missing_info[0]`).
7. **Step-by-Step Interactive Form**: The frontend renders progressive single-question forms with option buttons (e.g. Social Category $\rightarrow$ Education Level $\rightarrow$ Income $\rightarrow$ Gender).

---

### 2. Schemes Directory & Direct Application Workflow
1. **Directory Browsing**: The Explorer tab lists all **172 ingested schemes** with multi-field search filtering (Title, Description, State, Occupation, Category).
2. **Detail Inspection**: Selecting any scheme displays full details, required document checklists, and eligibility requirements.
3. **Direct Application**: Clicking **"Apply Directly Online"** ($\nearrow$) opens official government application portals (e.g. `scholarships.gov.in`, `pmkisan.gov.in`, `mysy.guj.nic.in`).

---

### 3. Automated Data Ingestion Workflows
- **Web Scraping Pipeline**:
  - Fetches scheme guidelines from URLs using `httpx` + `BeautifulSoup4`.
  - Gemini AI parses text into structured `Scheme` objects and updates `schemes.json`.
- **PDF Guidelines Ingestion Engine**:
  - Extracts text from PDF guideline brochures using `pypdf`.
  - Uses Gemini AI to build eligibility rules (`attribute`, `condition`, `value`, `description`).
  - Features an **offline heuristic regex parser fallback** if API rate limits occur.
  - **Bulk Multi-Page PDF Tool** ([`ingest_large_pdf.py`](file:///c:/Users/agrim/Uplift/backend/ingest_large_pdf.py)): Processes multi-page scheme catalog ebooks (e.g. 112-page `Schemes-Volume-1-English.pdf`) in page windows.

---

## 🗂️ Project Repository Structure

```text
Uplift/
├── frontend/                   # React 18 + Vite + TailwindCSS App
│   ├── src/
│   │   ├── components/         # UI Components
│   │   │   ├── chat/           # ChatWindow, MessageBubble, SchemeDetailDrawer, SidebarDashboard
│   │   │   ├── common/         # Header, Layout, LoadingSpinner
│   │   │   └── dashboard/      # Analytics Cards & Statistics
│   │   ├── pages/              # Chat, Explorer, Dashboard
│   │   ├── services/           # api.js, chatService.js, schemeService.js
│   │   └── routes/             # App Router configuration
│   └── package.json
│
├── backend/                    # FastAPI Async Python Backend
│   ├── app/
│   │   ├── api/routers/        # chat.py, schemes.py, health.py
│   │   ├── agents/             # reflection_agent.py
│   │   ├── services/           # profile_extractor.py, recommendation_service.py, pdf_ingestion_service.py, scheme_scraper.py
│   │   ├── schemas/            # scheme_schema.py, profile_schema.py, chat_schema.py
│   │   └── workflows/          # agent_workflow.py (Master 5-stage orchestrator)
│   ├── data/
│   │   └── schemes.json        # Database containing 172 government schemes
│   ├── pdf_schemes/            # Folder for input scheme PDF files
│   ├── tests/                  # PyTest Suite (22/22 tests passing)
│   ├── ingest_pdfs.py          # Single PDF ingestion CLI script
│   ├── ingest_large_pdf.py     # Multi-page catalog PDF ingestion CLI script
│   ├── run.py                  # Server launcher
│   └── requirements.txt        # Python dependencies
│
└── README.md                   # Project System Workflow Documentation
```

---

## 🚀 How to Run the Full Stack

### 1. Start Backend Server
```powershell
cd c:\Users\agrim\Uplift\backend
.\venv\Scripts\python.exe run.py
```
*Backend runs on `http://127.0.0.1:8000`*

### 2. Start Frontend App
```powershell
cd c:\Users\agrim\Uplift\frontend
npm run dev
```
*Frontend runs on `http://localhost:5173`*

### 3. Run Backend Test Suite
```powershell
cd c:\Users\agrim\Uplift\backend
.\venv\Scripts\python.exe -m pytest
```
*Verification Status*: **22 / 22 Tests Passed** (`100% clean`).
