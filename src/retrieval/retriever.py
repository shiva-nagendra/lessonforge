from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from retrieval.loader import load_and_chunk_documents


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "all-MiniLM-L6-v2"


class KnowledgeRetriever:
    """
    Local semantic retriever for LessonForge knowledge documents.

    Documents are embedded once when the retriever is initialized and
    searched using cosine similarity through a FAISS inner-product index.
    """

    def __init__(
        self,
        knowledge_dir: str | Path | None = None,
        model_name: str = DEFAULT_MODEL,
    ):
        self.model = SentenceTransformer(model_name)

        if knowledge_dir is None:
            knowledge_dir = PROJECT_ROOT / "knowledge"

        self.chunks = load_and_chunk_documents(knowledge_dir)

        if not self.chunks:
            raise ValueError(
                "No knowledge chunks were found. "
                "Add Markdown files to the knowledge directory."
            )

        embeddings = self.model.encode(
            [chunk["content"] for chunk in self.chunks],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        embeddings = embeddings.astype("float32")

        self.index = faiss.IndexFlatIP(
            embeddings.shape[1]
        )

        self.index.add(embeddings)

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Retrieve the most semantically relevant knowledge chunks.
        """

        if not query.strip():
            raise ValueError("query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.chunks)),
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            chunk = self.chunks[index]

            results.append(
                {
                    "source": chunk["source"],
                    "chunk_id": chunk["chunk_id"],
                    "content": chunk["content"],
                    "score": float(score),
                }
            )

        return results