from fastapi import FastAPI

from app.api.routes_documents import router as documents_router

app = FastAPI(
    title="ResearchMind",
    description="AI-powered research assistant",
    version="0.1.0"
)

app.include_router(documents_router)


@app.get("/")
def root():
    return {"message": "ResearchMind is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}