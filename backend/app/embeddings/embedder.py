from sentence_transformers import SentenceTransformer


class Embedder:

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        vector = self.model.encode(text)

        return vector.tolist()

    def embed_documents(
        self,
        documents: list[str]
    ) -> list[list[float]]:

        vectors = self.model.encode(documents)

        return vectors.tolist()