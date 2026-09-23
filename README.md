# NeuroSymbolic AI

An explainable commonsense-reasoning assistant built from the supplied guide. It combines a natural-language layer, a knowledge graph, symbolic paths, recent conversation context, a neural zero-shot classifier, and a chat UI.

## What is included

```
backend/   FastAPI API, SQLite chat history, optional JWT accounts, Neo4j + ConceptNet adapters
frontend/  React/Vite chat client with explanation and confidence views
desktop/   Electron desktop shell
scripts/   Opt-in ConceptNet to Neo4j seeding utility
```

The default experience works without external services: it uses a small bundled commonsense graph and a transparent classifier fallback. This makes the demo immediately usable, while keeping the intended spaCy, Transformers, Neo4j, and ConceptNet integrations ready to enable.

## Architecture

```text
Question
  -> NLP entity/concept extraction (spaCy; rules fallback)
  -> knowledge retrieval (Neo4j; starter graph fallback)
  -> symbolic path inference + conversation context
  -> zero-shot classification (Transformers; lightweight fallback)
  -> answer, graph evidence, explanation, confidence
```

## Run it locally

Requirements: Python 3.10+ and Node.js 18+ (or pnpm).

```powershell
# 1. Backend
cd backend
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```powershell
# 2. Web client
cd frontend
Copy-Item .env.example .env
pnpm install
pnpm dev
```

Open `http://localhost:5173`. The API docs are at `http://localhost:8000/docs`.

## Verify the backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest tests -v

# Or exercise the central endpoint directly
Invoke-RestMethod -Method POST http://localhost:8000/api/chat -ContentType 'application/json' -Body '{"session_id":"demo","message":"Is a penguin a bird?","candidate_answers":["yes","no"]}'
```

## Enable the full knowledge graph

1. Copy `backend/.env.example` to `backend/.env`.
2. Fill `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` for a local Neo4j database or AuraDB instance.
3. From `backend/`, seed selected terms (this is an explicit network action):

```powershell
$env:PYTHONPATH = (Get-Location)
python ..\scripts\seed_conceptnet.py penguin bird dog --limit 10
```

The service detects Neo4j at launch; when it is unavailable it automatically continues on the starter graph.

## Enable the Transformer model

Set these in `backend/.env` after dependencies are installed:

```dotenv
ENABLE_TRANSFORMERS=true
HF_MODEL_NAME=facebook/bart-large-mnli
```

The first enabled request downloads and loads the model. Keep `ENABLE_TRANSFORMERS=false` for a fast, dependency-light demonstration. The fallback is clearly reported in every explanation, so the confidence score is never presented as a calibrated probability or a hidden model result.

## Accounts and history

`POST /api/auth/signup` and `POST /api/auth/login` return Bearer tokens. Anonymous users can explore the demo; signed-in users have their messages linked to their account. Before a deployment, replace `JWT_SECRET` with a long random secret, use HTTPS, and move SQLite to managed PostgreSQL.

## Desktop development

Run the web client first, then:

```powershell
cd desktop
pnpm install
pnpm start
```

For a deployed web app, point the shell at it before launching or building:

```powershell
$env:ELECTRON_START_URL = "https://your-frontend.example"
pnpm build
```

`electron-builder` writes installers to `desktop/dist/`. Building a macOS DMG requires macOS; build each native installer on its target platform or use a CI build matrix.

## Deployment outline

1. Deploy `backend/` using its Dockerfile, set its production environment variables, and use Neo4j AuraDB + managed PostgreSQL.
2. Deploy `frontend/` to Vercel/Netlify. Set `VITE_API_URL` to the backend HTTPS URL.
3. Add the deployed frontend origin to `CORS_ORIGINS` in the backend environment.
4. Test sign-up, anonymous chat, authenticated history, and explanation output from an incognito browser before sharing the public URL.

## Important limitations

This is a project demonstration, not a fact-verification or high-stakes decision tool. It explains the graph paths it actually retrieved, but a graph path is not proof and the score is an operational indicator, not a probability guarantee. Expand and review the knowledge graph for your chosen domain before evaluating it academically.
