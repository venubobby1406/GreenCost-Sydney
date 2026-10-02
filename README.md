# GreenCost Sydney

A single-page building life-cycle cost comparison with an animated Three.js scene, a guided form, a research companion, PDF retrieval through **Chroma**, **Tavily** web context and **Gemini** explanations.

## Start locally

Requires Python 3.12+ and Node.js 20.9+.

```powershell
.\scripts\start-local.ps1
```

The script installs missing dependencies, updates the local Chroma index incrementally, and starts the backend on `127.0.0.1:8000` and frontend on `127.0.0.1:3000`. Press Ctrl+C to stop both services. You can supply `-Python 'C:\path\to\python.exe'`.

For manual setup, run these from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe scripts\ingest_knowledge.py
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open **http://127.0.0.1:3000**. Choose **Explore a sample**, continue through the three form steps and choose **Analyse my building**. Results appear on the same page. The API docs are at `http://127.0.0.1:8000/docs`.

Stop the development server before running `npm run build`: development and production builds share `.next`.

## Connect Gemini and Tavily

Copy `.env.example` to `.env` if `.env` does not exist. Add:

```dotenv
GEMINI_API_KEY=your-google-ai-studio-key
GEMINI_MODEL=gemini-3.5-flash
TAVILY_API_KEY=your-tavily-key
RAG_EMBEDDING_MODEL=local-hash-v1
```

Restart the backend after editing. The Gemini model is configurable; select a model available to your API account. API keys stay server-side and are never returned by the health endpoint or embedded in frontend code.

- [Gemini API documentation](https://ai.google.dev/api/generate-content)
- [Google AI Studio API keys](https://aistudio.google.com/api-keys)
- [Tavily search documentation](https://docs.tavily.com/documentation/api-reference/endpoint/search)
- [Chroma Python client documentation](https://docs.trychroma.com/reference/python/client)

Without keys, financial calculations and local PDF retrieval work normally. The page explicitly identifies template explanations and missing or unavailable research connections. No API credentials were supplied or used during verification; external provider contracts were tested with mocked responses.

## User experience

Everything is on one landing page: introduction, animated architectural scene, workflow explanation, project form, research companion, results, methodology and evidence. Old methodology/source URLs redirect to the evidence section.

The form has three guided steps:

1. Building location, distributor and geometry.
2. Construction budget or detailed materials, annual consumption and optional custom tariffs.
3. Sustainable features, quote/premium, combined performance and study horizon.

Financial assumptions, replacement schedules, material service lives and terminal values remain available behind expandable controls. **Start fresh** creates independent inputs. **Fill sample** explicitly loads illustrative values. Geometry, feature selections and system names do not invent prices or performance. Commercial projects select custom utility pricing.

The Three.js scene has interactive floor and solar controls, an animated research companion and a WebGL fallback. Motion respects the user's reduced-motion setting. The companion panel reports real backend progress events rather than timer-based pretend progress.

## Analysis architecture

```text
Single Next.js page
  → /api proxy
  → FastAPI / Pydantic validation
  → LangGraph workflow
      validate inputs
      → retrieve project-specific PDF passages from Chroma
      → optional Tavily official-domain search
      → validate applicable utility rates
      → build conventional and sustainable scenarios
      → Python LCC calculations for 30 / 40 / 50 years
      → 48 sensitivity combinations
      → deterministic financial summary + grounded Gemini interpretation
  → SQLite saved result
  → inline charts, explanations, evidence, HTML report and CSV
```

The browser reads server-sent events from `POST /api/analyse/stream`. Stages and the final saved result are emitted as JSON events. The original `POST /api/analyse` remains available for non-streaming API clients.

Gemini receives non-identifying scenario facts and bounded retrieved excerpts. The analysis interpretation uses qualitative language and supplied citation labels such as `[S1]`. Invented numbers, monetary claims and unknown citation references are rejected; calculated summaries remain available. The financial model never delegates arithmetic to Gemini. Missing keys, timeouts, provider errors and unusable responses have explicit fallback status.

Tavily receives a general query based on building type and selected features, with up to four results and no generated answer. The allowed domains are AER, Sydney Water, ABS, NSW Planning and Planning Portal. External snippets are labelled **WEB_RESEARCH** and support explanation only. They never overwrite tariff records or formulas. Users can disable web research in the form. Normal analysis makes at most one Tavily search and one Gemini explanation request. Non-numerical follow-up questions can make a Gemini request using local retrieval and saved web context; deterministic what-ifs do not make external calls.

## PDF knowledge base and Chroma

Original research PDFs live in `data/knowledge/`. Their passages are labelled **PROJECT_RESEARCH**, with source filename, original page, document hash and deterministic chunk identifier. Official JSON records and regulatory context are indexed with separate categories.

```powershell
.\.venv\Scripts\python.exe scripts\ingest_knowledge.py
```

The persistent vector database is `data/chroma/`. Changed chunks are upserted, unchanged embeddings are reused, and obsolete chunks are deleted. The manifest records the embedding configuration and source hashes. The old `data/faiss/` files are retained as legacy artifacts and are no longer read by the application.

Use **Add a PDF** on the landing page to upload a text-based, unlocked PDF up to 10 MB and 200 pages. The backend sanitizes filenames, preserves page citations and indexes the document. Scanned/image-only PDFs need OCR before upload. Uploaded documents are stored locally; retrieved excerpts may be sent to Gemini when connected. This local prototype has no upload deletion or account permissions interface.

Default embeddings use normalized token/bigram feature hashes, requiring no model download. They provide lexical similarity rather than transformer semantic understanding. For semantic retrieval:

1. Install `sentence-transformers` into `.venv`.
2. Download a model once, outside the normal workflow.
3. Set `RAG_EMBEDDING_MODEL` to the model's local directory.
4. Run `scripts/ingest_knowledge.py --force` and restart the backend.

Local model loading uses `local_files_only=True`. [Chroma](https://docs.trychroma.com/reference/python/client) stores explicit embeddings; its automatic embedding downloads are disabled.

## Financial model

```text
LCC = C0 + Σ (Energy + Water + Maintenance + Replacement + Other)t / (1+r)^t
         + DisposalN / (1+r)^N − ResidualN / (1+r)^N
```

- Capital is year zero; subsequent expenditure is at year end.
- Base prices escalate t times in year t. Use consistent nominal escalation and discount rates.
- Electricity includes grid usage and daily supply. Solar self-use belongs in the consumption assumptions; export income is excluded.
- Water reductions affect variable consumption. Applicable fixed charges stay unchanged between scenarios and are normalized from the provider's 92-day basis to 365 days.
- An explicit construction total overrides AUD/m². A zero construction total is rejected; leave it blank to use a rate.
- Detailed construction includes material quantity × price plus remaining scope. Material maintenance is additional to building maintenance.
- Sustainable construction uses an explicit quote or one editable package premium.
- Replacements occur at entered intervals strictly before retirement. Detailed material replacements apply to both scenarios unless explicit scenario-specific rows are supplied; avoid duplicates.
- Disposal and residual values are base-year equivalents escalated to each horizon's endpoint. Residual value is a credit; none is inferred.
- Savings = conventional LCC − sustainable LCC. Negative savings means sustainable costs more.
- First discounted break-even can later reverse. Inspect annual cash flows.
- Computation retains full precision; displayed values are rounded. CSV preserves numerical precision.
- Historical ABS indexation uses a matching-series index ratio. PPI is never AUD/m².

See `docs/METHODOLOGY.md` for the independent audit example and boundaries.

## Tariff lifecycle

`data/verified/` contains the existing 2026–27 residential tariff register and June 2026 construction index. Official pricing must be effective on the project's reference date. Commercial projects require all four custom prices and a source note. The supplied register is not a live retail quote or an automatic assessment of metering, catchments or drought conditions.

```powershell
.\.venv\Scripts\python.exe scripts\update_sources.py --offline
.\.venv\Scripts\python.exe scripts\update_sources.py --direct
.\.venv\Scripts\python.exe scripts\update_sources.py
.\.venv\Scripts\python.exe scripts\ingest_knowledge.py
```

The administrator refresh remains separate from analysis research. It conservatively verifies the existing dated schema against original pages, retains the previous register on failure, and uses atomic writes. A new financial year or price table requires a reviewed extraction rule and dated record. Online contextual search does not silently update financial values.

## Persistence and API

SQLite stores complete analysis snapshots in `data/greencost.sqlite3`, including inputs, selected rates, calculations, source records, retrieved evidence and provider status. Chat what-ifs reuse saved rates. Saved reports remain reproducible after cache changes.

| Route | Purpose |
|---|---|
| `GET /api/health` | Chroma readiness, document counts, connection flags; no secrets |
| `GET /api/demo` | Labelled sample project |
| `GET /api/sources` | Cached source register |
| `POST /api/knowledge/pdf?filename=research.pdf` | Raw PDF upload and indexing |
| `POST /api/analyse` | Calculate and save |
| `POST /api/analyse/stream` | Real analysis stages and saved result |
| `GET /api/analyses/{id}` | Retrieve saved result |
| `POST /api/analyses/{id}/chat` | Grounded questions and supported what-ifs |
| `GET /api/analyses/{id}/report?years=40` | Self-contained HTML report |
| `GET /api/analyses/{id}/cashflows?years=40` | Full-precision CSV |

Reports include PDF/web reference labels, excerpts and complete input records. Open the downloaded HTML and use Print → Save as PDF. There is no saved-analysis history screen; saved results remain accessible through their API identifier.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check backend scripts
cd frontend
npm run typecheck
npm run lint
npm run build
```

The current suite includes financial audits, source policy, PDF upload, Chroma incremental updates, Gemini request/response contracts, hallucinated money rejection, Tavily allowlists, streamed stages, saved-rate what-ifs and offline fallback. See `docs/REWRITE_VERIFICATION.md` for the rewrite verification record. Earlier checks in `docs/VERIFICATION.md` describe the previous UI and FAISS implementation.

This is an indicative academic model. It is not a QS quotation, calibrated energy simulation or compliance certificate. It binds to loopback and has no authentication; public deployment would require authentication, upload policies and operational hardening.
