from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from pathlib import Path
import shutil

from app.ingestion.loader import load_pdf
from app.ingestion.cleaner import clean_text
from app.ingestion.chunker import chunk_text
from app.embeddings.embedder import Embedder

from app.core import state


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

UPLOAD_DIR = Path(
    "data/raw"
)

VECTOR_STORE_PATH = (
    "data/processed/vector_store"
)


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Embedder
# --------------------------------------------------

embedder = Embedder()


# --------------------------------------------------
# Upload
# --------------------------------------------------

@router.post("/upload")
async def upload_documents(
    files: list[UploadFile] = File(...)
):

    if not files:

        raise HTTPException(
            status_code=400,
            detail="No files were uploaded."
        )


    if len(files) > 10:

        raise HTTPException(
            status_code=400,
            detail="You can upload a maximum of 10 PDFs at once."
        )


    results = []


    for file in files:

        # --------------------------------------------------
        # Validate PDF
        # --------------------------------------------------

        if not file.filename.lower().endswith(
            ".pdf"
        ):

            results.append({
                "filename": file.filename,
                "status": "error",
                "error": "Only PDF files are supported."
            })

            continue


        file_path = (
            UPLOAD_DIR /
            file.filename
        )


        try:

            # --------------------------------------------------
            # Save PDF
            # --------------------------------------------------

            with file_path.open(
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    file.file,
                    buffer
                )


            # --------------------------------------------------
            # Load PDF
            # --------------------------------------------------

            raw_text = load_pdf(
                str(file_path)
            )


            # --------------------------------------------------
            # Clean text
            # --------------------------------------------------

            cleaned_text = clean_text(
                raw_text
            )


            # --------------------------------------------------
            # Chunk
            # --------------------------------------------------

            chunks = chunk_text(
                cleaned_text
            )


            # --------------------------------------------------
            # Build document objects
            # --------------------------------------------------

            documents = []

            for chunk_id, chunk in enumerate(
                chunks
            ):

                documents.append({
                    "document_name":
                        file.filename,

                    "chunk_id":
                        chunk_id,

                    "text":
                        chunk
                })


            # --------------------------------------------------
            # Generate embeddings
            # --------------------------------------------------

            embeddings = [
                embedder.embed_text(
                    document["text"]
                )
                for document in documents
            ]


            # --------------------------------------------------
            # Add to FAISS
            # --------------------------------------------------

            state.vector_store.add(
                embeddings,
                documents
            )


            # --------------------------------------------------
            # Rebuild BM25 / hybrid retriever
            # --------------------------------------------------

            state.rebuild_retriever()


            # --------------------------------------------------
            # Save vector store
            # --------------------------------------------------

            state.vector_store.save(
                VECTOR_STORE_PATH
            )


            results.append({
                "filename":
                    file.filename,

                "characters":
                    len(cleaned_text),

                "chunks":
                    len(chunks),

                "status":
                    "success"
            })


        except Exception as e:

            results.append({
                "filename":
                    file.filename,

                "status":
                    "error",

                "error":
                    str(e)
            })


    return {
        "results": results
    }


# --------------------------------------------------
# List documents
# --------------------------------------------------

@router.get("")
def list_documents():

    document_map = {}


    for document in (
        state.vector_store.documents
    ):

        filename = (
            document["document_name"]
        )


        if filename not in document_map:

            document_map[filename] = {
                "filename": filename,
                "chunks": 0
            }


        document_map[
            filename
        ]["chunks"] += 1


    return list(
        document_map.values()
    )


# --------------------------------------------------
# Delete one document
# --------------------------------------------------

@router.delete(
    "/{filename}"
)
def delete_document(
    filename: str
):

    current_documents = (
        state.vector_store.documents
    )


    remaining_documents = [
        document
        for document in current_documents
        if document["document_name"]
        != filename
    ]


    # --------------------------------------------------
    # Check document exists
    # --------------------------------------------------

    if len(remaining_documents) == len(
        current_documents
    ):

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )


    # --------------------------------------------------
    # Rebuild FAISS index
    # --------------------------------------------------

    from app.database.vector_store import (
        VectorStore
    )


    new_store = VectorStore(
        dimension=
            state.vector_store.dimension
    )


    if remaining_documents:

        embeddings = [
            embedder.embed_text(
                document["text"]
            )
            for document
            in remaining_documents
        ]


        new_store.add(
            embeddings,
            remaining_documents
        )


    # --------------------------------------------------
    # Replace shared store contents
    # --------------------------------------------------

    state.vector_store.index = (
        new_store.index
    )

    state.vector_store.documents = (
        new_store.documents
    )


    # --------------------------------------------------
    # Rebuild retriever
    # --------------------------------------------------

    state.rebuild_retriever()


    # --------------------------------------------------
    # Save updated store
    # --------------------------------------------------

    if remaining_documents:

        state.vector_store.save(
            VECTOR_STORE_PATH
        )

    else:

        index_path = Path(
            VECTOR_STORE_PATH,
            "index.faiss"
        )

        documents_path = Path(
            VECTOR_STORE_PATH,
            "documents.pkl"
        )


        if index_path.exists():
            index_path.unlink()


        if documents_path.exists():
            documents_path.unlink()


    # --------------------------------------------------
    # Delete original PDF
    # --------------------------------------------------

    file_path = (
        UPLOAD_DIR /
        filename
    )


    if file_path.exists():

        file_path.unlink()


    return {
        "status":
            "deleted",

        "filename":
            filename
    }


# --------------------------------------------------
# Clear all documents
# --------------------------------------------------

@router.delete("")
def clear_all_documents():

    from app.database.vector_store import (
        VectorStore
    )


    # --------------------------------------------------
    # Reset shared vector store
    # --------------------------------------------------

    new_store = VectorStore(
        dimension=
            state.vector_store.dimension
    )


    state.vector_store.index = (
        new_store.index
    )

    state.vector_store.documents = []


    # --------------------------------------------------
    # Rebuild retriever
    # --------------------------------------------------

    state.rebuild_retriever()


    # --------------------------------------------------
    # Delete saved FAISS files
    # --------------------------------------------------

    index_path = Path(
        VECTOR_STORE_PATH,
        "index.faiss"
    )

    documents_path = Path(
        VECTOR_STORE_PATH,
        "documents.pkl"
    )


    if index_path.exists():

        index_path.unlink()


    if documents_path.exists():

        documents_path.unlink()


    # --------------------------------------------------
    # Delete uploaded PDFs
    # --------------------------------------------------

    for pdf_file in (
        UPLOAD_DIR.glob("*.pdf")
    ):

        pdf_file.unlink()


    return {
        "status":
            "cleared"
    }