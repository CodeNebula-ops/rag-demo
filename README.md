# Retrion — Production-Grade RAG System

A production RAG (Retrieval-Augmented Generation) system with a 7-stage pipeline, hallucination guardrails, and source citations. Upload documents, ask questions, get grounded answers.

## Pipeline Architecture

```
Any data in → cited, grounded, verified answers out
```

| Stage | What it does | Implementation |
|-------|-------------|----------------|
| **01 Ingestion** | OCR, layout-aware parsing, semantic chunking, hybrid indexing | PyMuPDF, heading detection, hierarchical chunking, BM25 + Qdrant |
| **02 Query Understanding** | Rewrite, expansion, intent detection, routing | Groq LLM query analysis, pronoun resolution, term expansion |
| **03 Retrieval** | BM25 + dense vector, metadata filtering | Hybrid search, Reciprocal Rank Fusion (RRF), top-k filtering |
| **04 Post-Retrieval** | Reranking, compression, deduplication, context ordering | Embedding similarity rerank, semantic dedup, intent-based ordering |
| **05 Generation** | Grounded prompting, citation enforcement | Strict system prompt, low temperature, mandatory [Source:] format |
| **06 Validation** | Faithfulness check, confidence scoring, abstention | Embedding-based claim verification, hard skip threshold |
| **07 Operations** | Observability, feedback loop, semantic cache | Structured logging, audit trail, thumbs up/down, query cache |

## Tech Stack

- **LLM**: Groq API (Llama 3.1 8B, free tier)
- **Embeddings**: BAAI/bge-small-en-v1.5 (384-dim, local ONNX via fastembed)
- **Vector Store**: Qdrant Cloud (free 1GB)
- **Database**: PostgreSQL 16
- **Backend**: Python FastAPI (async)
- **Frontend**: React 18 + Vite + TailwindCSS

## Hallucination Prevention

1. Strict grounded system prompt — answers only from provided context
2. Low temperature (0.1) for deterministic outputs
3. Query understanding — rewrites ambiguous queries before retrieval
4. Hard abstention — skips LLM entirely if all retrieval scores < 0.3
5. Post-generation faithfulness check via embedding similarity
6. Confidence scoring (retrieval quality + faithfulness ratio)
7. Mandatory citation validation with [Source: doc, section] format
8. Visual confidence indicators (high/medium/low) on every message
9. Unfaithful answer warnings appended automatically
10. Semantic cache — consistent answers for similar queries
11. Human feedback (thumbs up/down) logging for continuous improvement
12. Section breadcrumbs prepended to every chunk for traceability
13. Max token limit (512) to prevent rambling

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

- **Minimum**: 4GB RAM, 2-core CPU
- **Storage**: ~2GB for Docker images + documents

---

## Deploy to Render (Free Tier)

### Prerequisites

Free accounts on:
1. **Groq** — https://console.groq.com (API key for LLM)
2. **Qdrant Cloud** — https://cloud.qdrant.io (free 1GB cluster)
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
2. **Backend**: Create a Web Service
   - Runtime: Docker
   - Set environment variables:
     - `DATABASE_URL` = (from Render PostgreSQL)
     - `GROQ_API_KEY` = your key
     - `QDRANT_HOST` = your Qdrant Cloud URL
     - `QDRANT_API_KEY` = your Qdrant Cloud key
     - `EMBEDDING_MODEL_NAME` = `BAAI/bge-small-en-v1.5`
3. **Frontend**: Create a Static Site
   - Build command: `cd frontend && npm ci && npm run build`
   - Publish directory: `frontend/dist`
   - Add rewrite rule: `/api/*` → `https://your-backend.onrender.com/api/*`

---

## API Endpoints

Once running, visit http://localhost:8000/docs for interactive Swagger UI.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Service health checks (DB, Qdrant, LLM, embeddings) |
| `/api/v1/chat/sessions` | POST | Create chat session |
| `/api/v1/chat/sessions` | GET | List recent sessions |
| `/api/v1/chat/sessions/{id}/messages` | POST | Send message (SSE stream) |
| `/api/v1/chat/sessions/{id}` | DELETE | Delete session |
| `/api/v1/chat/sessions/{id}/history` | GET | Get session history |
| `/api/v1/chat/messages/{id}/feedback` | POST | Submit thumbs up/down |
| `/api/v1/documents` | POST | Upload document |
| `/api/v1/documents` | GET | List documents |
| `/api/v1/documents/{id}` | GET | Get document details |
| `/api/v1/documents/{id}` | DELETE | Delete document |
| `/api/v1/documents/{id}/reprocess` | POST | Reprocess failed document |
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

PDF (.pdf), Word (.docx, .doc), Text (.txt), Markdown (.md) — up to 50MB
