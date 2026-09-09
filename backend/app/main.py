from fastapi import FastAPI
from app.generation.llm import generate_response
from app.api.routes_query import router as query_router
from app.api.routes_upload import router as upload_router
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_documents import router as documents_router
#from app.api.routes_health import router as health_router

app = FastAPI(
    title="ResearchMind API",
    description="Production-grade AI Research Assistant",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/generate")
def generate():
    response = generate_response(
        "Explain what retrieval augmented generation is in 3 sentences."
    )

    return {
        "response": response
    }


app.include_router(
    documents_router
)

app.include_router(
    query_router
)

#app.include_router(
 #   health_router
#)