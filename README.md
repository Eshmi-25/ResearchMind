# ResearchMind

ResearchMind is a production-style AI research assistant built to explore retrieval-augmented generation (RAG), information retrieval, embeddings,reranking, grounded generation, and evaluation.

## Project Goals
- Build a complete RAG pipeline
- Compare dense, sparse, and hybrid retrieval
- Experiment with reranking
- Evaluate retrieval and generation quality
- Build a production-style FastAPI backend
- Containerize and deploy the system
- Measure performance and reliability

## Current Status

🚧 Project foundation in progress.

## Architecture

                         ┌──────────────────────┐
                         │       FRONTEND       │
                         │                      │
                         │  Upload PDF          │
                         │  Ask Question        │
                         │  View Answer         │
                         │  View Citations      │
                         │  View Sources        │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP
                                    ▼
                         ┌──────────────────────┐
                         │      FASTAPI         │
                         │       BACKEND        │
                         │                      │
                         │ /documents/upload    │
                         │ /documents           │
                         │ /query               │
                         │ /health              │
                         │ /metrics             │
                         └──────────┬───────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                │                                       │
                ▼                                       ▼
       ┌─────────────────┐                    ┌─────────────────┐
       │ DOCUMENT        │                    │ QUERY           │
       │ INGESTION       │                    │ PIPELINE        │
       │                 │                    │                 │
       │ PDF             │                    │ User Query      │
       │ ↓               │                    │ ↓               │
       │ Extraction      │                    │ Query Embedding │
       │ ↓               │                    │ ↓               │
       │ Cleaning        │                    │ Dense Retrieval │
       │ ↓               │                    │ +               │
       │ Metadata        │                    │ Sparse Retrieval│
       │ ↓               │                    │ ↓               │
       │ Chunking        │                    │ Hybrid          │
       └────────┬────────┘                    │ Retrieval       │
                │                             │ ↓               │
                ▼                             │ Reranking       │
       ┌─────────────────┐                    │ ↓               │
       │   EMBEDDING     │                    │ Top-K Context   │
       │     MODEL       │                    └────────┬────────┘
       └────────┬────────┘                             │
                │                                      ▼
                ▼                              ┌─────────────────┐
       ┌─────────────────┐                     │      LLM        │
       │  VECTOR STORE   │                     │                 │
       │                 │                     │ Prompt +        │
       │ FAISS initially │                     │ Evidence        │
       │                 │                     │ ↓               │
       └─────────────────┘                     │ Answer          │
                                               └────────┬────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ CITATION +      │
                                               │ GROUNDING       │
                                               │ VERIFICATION    │
                                               └────────┬────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │     RESPONSE    │
                                               │ Answer          │
                                               │ Sources         │
                                               │ Citations       │
                                               │ Grounding info  │
                                               └─────────────────┘


## Tech Stack

FastAPI
Uvicorn


Python
NumPy
Pydantic
pytest
Git

## Evaluation

Results will be added only after running actual experiments.

## Installation

Coming soon.

## Running Locally

Coming soon.

## Docker

Coming soon.

## Deployment

Coming soon.

## Limitations

Coming soon.

## Future Work

Coming soon.