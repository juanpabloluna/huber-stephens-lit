# Huber-Stephens Literature Expert Agent

## Overview
RAG-based research assistant for the Huber-Stephens research program on welfare states, state capacity, redistribution, and democracy. Covers 30 works from 1992-2025.

## Architecture
Cloned from `~/projects/what-works-agent/` with:
- Collection: `huber_stephens_literature` (ChromaDB 1.4.1)
- Corpus: 30 works (23 successfully indexed, 7 scanned PDFs pending OCR)
- 100 chunks from ~1,200 pages
- Embedding: all-MiniLM-L6-v2
- LLM: claude-sonnet-4-20250514

## Key Customizations
- Domain-specific prompts in `src/agents/prompts.py` — emphasize full authorship, Huber-Stephens partnership
- **NEW: Visualization engine** (`src/agents/visualization_engine.py`) — generates interactive HTML concept maps, causal graphs, timelines
- **NEW: Visualizations page** (`pages/5_visualizations.py`) — Streamlit UI for requesting and rendering visualizations

## Pages
1. Q&A — question answering with citations
2. Synthesis — literature review generation
3. Review — research draft review
4. Agentic Q&A — multi-query Claude agent
5. **Visualizations** — interactive concept maps & causal graphs (NEW)
6. Bibliography — APA 7th formatted
8. Usage Log

## Corpus Location
- PDFs: `~/Desktop/huber stephens/`
- Metadata: `data/papers_metadata.csv`
- Vector DB: `data/chromadb/`

## Failed PDFs (scanned, need OCR)
- Models of Capitalism (2002)
- Postindustrial Social Policy (2015)
- Nelson & Stephens (2009)
- Changing Shapes of LA Welfare States (2019)
- Predistribution and Redistribution (2014)
- Capitalist Development & Democracy (1992)
- CD&D: The Controversy

## Deployment
- GitHub: `juanpabloluna/huber-stephens-lit` (to be created)
- Streamlit Cloud: password-protected
- Run locally: `streamlit run app.py`
