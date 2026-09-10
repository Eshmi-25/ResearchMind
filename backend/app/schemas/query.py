from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    selected_documents: list[str] | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]