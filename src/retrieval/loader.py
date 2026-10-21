from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


def load_documents(
    knowledge_dir: str | Path = KNOWLEDGE_DIR,
) -> list[dict]:
    """
    Load Markdown knowledge documents from the knowledge directory.

    Each returned document contains:
    - source: file name
    - content: raw document text
    """

    knowledge_path = Path(knowledge_dir)

    if not knowledge_path.exists():
        raise FileNotFoundError(
            f"Knowledge directory does not exist: {knowledge_path}"
        )

    documents = []

    for file_path in sorted(knowledge_path.glob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        documents.append(
            {
                "source": file_path.name,
                "content": content,
            }
        )

    return documents


def chunk_document(
    document: dict,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[dict]:
    """
    Split a document into overlapping word-based chunks.

    Word-based chunking keeps the implementation deterministic and easy
    to inspect for this knowledge base.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    words = document["content"].split()

    if not words:
        return []

    chunks = []
    start = 0
    chunk_index = 0

    step = chunk_size - chunk_overlap

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk_text = " ".join(words[start:end])

        chunks.append(
            {
                "source": document["source"],
                "chunk_id": chunk_index,
                "content": chunk_text,
            }
        )

        chunk_index += 1
        start += step

    return chunks


def load_and_chunk_documents(
    knowledge_dir: str | Path = KNOWLEDGE_DIR,
) -> list[dict]:
    """
    Load all knowledge documents and split them into chunks.
    """

    documents = load_documents(knowledge_dir)

    chunks = []

    for document in documents:
        chunks.extend(chunk_document(document))

    return chunks