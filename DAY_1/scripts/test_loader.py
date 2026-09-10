import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kg_pipeline.document_loader import load_documents
from kg_pipeline.text_splitter import split_documents

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference"


def main() -> None:
    documents = load_documents(REFERENCE_DIR)
    print(f"Loaded {len(documents)} documents from {REFERENCE_DIR}")

    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    sizes = [len(c.page_content) for c in chunks]
    print(f"Chunk size: min={min(sizes)} max={max(sizes)} avg={sum(sizes) // len(sizes)}")

    print("\n--- Sample document ---")
    print("Source:", documents[0].metadata.get("source"))
    print(documents[0].page_content[:300])

    print("\n--- Sample chunk ---")
    print("Source:", chunks[0].metadata.get("source"))
    print(chunks[0].page_content[:300])


if __name__ == "__main__":
    main()
