from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from app.ingestion.loader import load_pdf
from app.ingestion.cleaner import clean_text
from app.ingestion.chunker import chunk_text


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = Path("data/raw")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        raw_text = load_pdf(str(file_path))
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text)

        return {
            "filename": file.filename,
            "characters": len(cleaned_text),
            "chunks": len(chunks),
            "status": "processed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )