from dataclasses import dataclass


@dataclass
class ChunkMetadata:
    document_name: str
    chunk_id: int
    total_chunks: int


def create_chunk_metadata(
    document_name: str,
    chunks: list[str]
) -> list[ChunkMetadata]:

    total_chunks = len(chunks)

    return [
        ChunkMetadata(
            document_name=document_name,
            chunk_id=index,
            total_chunks=total_chunks
        )
        for index in range(total_chunks)
    ]