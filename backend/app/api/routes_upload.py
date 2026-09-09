from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.ingestion.indexer import DocumentIndexer


router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Load the indexer once so all uploaded PDFs
# are added to the same vector store.
indexer = DocumentIndexer()


@router.post("/")
async def upload_pdfs(
    files: list[UploadFile] = File(...)
):
    """
    Upload and index multiple PDF documents.
    """

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files uploaded."
        )

    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 PDFs can be uploaded at once."
        )

    results = []

    for file in files:

        # Validate extension
        if not file.filename.lower().endswith(".pdf"):
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": "Only PDF files are supported."
            })
            continue

        file_path = UPLOAD_DIR / file.filename

        try:

            # Save uploaded PDF
            contents = await file.read()

            with open(file_path, "wb") as output_file:
                output_file.write(contents)

            # Index document
            result = indexer.index_document(
                str(file_path)
            )

            results.append({
                "filename": file.filename,
                "status": "success",
                "chunks": result["chunks"],
                "embedding_dimension": result[
                    "embedding_dimension"
                ]
            })

        except Exception as error:

            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(error)
            })

    return {
        "message": "PDF processing completed.",
        "files_processed": len(results),
        "results": results
    }