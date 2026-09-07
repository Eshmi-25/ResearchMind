from app.ingestion.indexer import DocumentIndexer


PDF_PATH = r"C:\Users\sumit\OneDrive\Desktop\ResearchMind\data\raw\super-cheatsheet-machine-learning.pdf"


indexer = DocumentIndexer()

result = indexer.index_document(PDF_PATH)

print("INDEXING RESULT")
print(result)

print("\nSEARCH RESULTS")

results = indexer.search(
    "What is supervised learning?",
    top_k=3
)

for result in results:

    print("\nScore:", result["score"])

    print("Document:", result["document_name"])

    print("Chunk ID:", result["chunk_id"])

    print("Text:")

    print(result["text"][:500])