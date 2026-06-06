# GraphRAG Law Assistant

An AI-powered legal assistant that answers questions about the **Labour Law of the Federation of Bosnia and Herzegovina** (Zakon o radu FBiH). Built with GraphRAG — a retrieval-augmented generation pipeline that uses a knowledge graph instead of flat vector search, enabling multi-hop reasoning across interconnected legal concepts.

## How it works

1. The law is chunked, embedded, and stored as a **knowledge graph** (nodes = legal concepts, edges = relationships)
2. At query time, the graph is traversed to retrieve the most relevant context — including related clauses that flat retrieval would miss
3. An LLM generates a grounded answer from the retrieved graph context

## Features

- **Three query modes** — general Q&A, compliance analysis, contract analysis
- **Domain-aware retrieval** — pre-defined keyword clusters for salary, working hours, contracts, vacation, termination, probation, maternity leave, health & safety
- **Knowledge graph visualisation** — interactive HTML graph (`visualizations/knowledge_graph.html`)
- **React frontend** — language detection, typewriter text effect, clean chat UI

## Project structure

```
├── backend/
│   ├── app.py                      # FastAPI application entry point
│   └── src/
│       ├── graph_rag.py            # Core GraphRAG engine
│       ├── retrieval.py            # Context retrieval (general / compliance / contract)
│       ├── generation.py           # LLM answer generation
│       ├── embeddings.py           # Text embedding pipeline
│       ├── chunking.py             # Document chunking
│       └── data_processing.py     # Law document preprocessing
└── frontend/
    └── src/
        ├── components/
        │   ├── LanguageDetector.jsx
        │   └── TypewriterText.jsx
        └── App.js
```

## Running locally

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend
cd frontend
npm install
npm start
```

## Tech stack

- **Python / FastAPI** — backend API
- **GraphRAG** — knowledge graph retrieval
- **React** — frontend interface
- **NetworkX** — graph construction and traversal
