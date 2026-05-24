# AI Knowledge Base — Production-Grade RAG System

A Dockerized RAG (Retrieval-Augmented Generation) system with zero-hallucination guardrails. Upload documents, ask questions, and get grounded answers with source citations and confidence scores.

## Architecture

- **LLM**: Groq API (free, ultra-fast — Llama 3.1 8B)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384-dim)
- **Reranker**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Vector Store**: Qdrant (local Docker or Qdrant Cloud free tier)
- **Database**: PostgreSQL 16
- **Backend**: Python FastAPI (async)
- **Frontend**: React 18 + Vite + TailwindCSS
- **Retrieval**: Hybrid dense + sparse (BM25) + RRF fusion + cross-encoder reranking

## Hallucination Prevention (10 layers)

1. Strict system prompt constraining answers to provided context
2. Low temperature (0.1) for deterministic outputs
3. Empty retrieval guard — skips LLM if no relevant docs found
4. Post-generation faithfulness check via embedding similarity
5. Confidence scoring (retrieval quality + faithfulness ratio)
6. Mandatory citation validation
7. Visual confidence indicators on every message
8. Human feedback (thumbs up/down) logging
9. Section breadcrumbs prepended to every chunk
10. Max token limit (512) to prevent rambling

## Quick Start (Local with Docker)

### 1. Get a free Groq API key

Go to https://console.groq.com, sign up, and create an API key.

### 2. Configure and run

```bash
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY
docker compose up --build
```

Open http://localhost:3000 once services are ready.

### Hardware Requirements (Local)

- **Minimum**: 8GB RAM, 4-core CPU
- **Storage**: ~3GB for Docker images + documents

---

## Deploy to Render (Free Tier)

### Prerequisites

You need free accounts on:
1. **Groq** — https://console.groq.com (API key for LLM)
2. **Qdrant Cloud** — https://cloud.qdrant.io (free 1GB cluster for vector storage)
3. **Render** — https://render.com (hosting)

### Step-by-step

#### 1. Set up Qdrant Cloud

1. Create account at https://cloud.qdrant.io
2. Create a free cluster
3. Note the **cluster URL** (e.g., `abc123-xyz.aws.cloud.qdrant.io`) and **API key**

#### 2. Deploy to Render

**Option A: Blueprint (automated)**

1. Push this repo to GitHub
2. Go to https://render.com/deploy
3. Connect your repo — Render reads `render.yaml` automatically
4. Set these environment variables on the `kb-backend` service:
   - `GROQ_API_KEY` = your Groq key
   - `QDRANT_HOST` = your Qdrant Cloud cluster URL (without `https://`)
   - `QDRANT_API_KEY` = your Qdrant Cloud API key
5. Deploy

**Option B: Manual setup**

1. **PostgreSQL**: Create a free PostgreSQL database on Render
2. **Backend**: Create a Web Service pointing to the `backend/` directory
   - Runtime: Docker
   - Set environment variables:
     - `DATABASE_URL` = (from Render PostgreSQL)
     - `GROQ_API_KEY` = your key
     - `QDRANT_HOST` = your Qdrant Cloud URL
     - `QDRANT_API_KEY` = your Qdrant Cloud key
     - `GROQ_MODEL_NAME` = `llama-3.1-8b-instant`
3. **Frontend**: Create a Static Site pointing to the `frontend/` directory
   - Build command: `npm ci && npm run build`
   - Publish directory: `dist`
   - Add env var: `VITE_API_URL` = `https://your-backend.onrender.com/api/v1`
   - Add rewrite rule: `/api/*` → `https://your-backend.onrender.com/api/*`

---

## API Documentation

Once running, visit http://localhost:8000/docs for interactive Swagger UI.

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Service health checks |
| `/api/v1/chat/sessions` | POST | Create chat session |
| `/api/v1/chat/sessions/{id}/messages` | POST | Send message (SSE stream) |
| `/api/v1/documents` | POST | Upload document |
| `/api/v1/documents` | GET | List documents |
| `/api/v1/analytics/usage` | GET | Usage statistics |
| `/api/v1/analytics/content-gaps` | GET | Low-confidence queries |

## Development

### Backend only
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend only
```bash
cd frontend
npm install
npm run dev
```

## Supported File Types

PDF (.pdf), Word (.docx, .doc), Text (.txt), Markdown (.md)
