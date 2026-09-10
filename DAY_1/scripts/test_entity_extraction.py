import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from kg_pipeline.document_loader import load_documents
from kg_pipeline.entity_extraction import extract_entities, get_extractor
from kg_pipeline.text_splitter import split_documents

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference"
SAMPLE_SIZE = 3


def main() -> None:
    documents = load_documents(REFERENCE_DIR)
    chunks = split_documents(documents)

    extractor = get_extractor()

    for chunk in chunks[:SAMPLE_SIZE]:
        print("=== Source:", chunk.metadata.get("source"), "===")
        result = extract_entities(chunk, extractor=extractor)
        for entity in result.entities:
            print(f"  [{entity.type}] {entity.name}")
        print()


if __name__ == "__main__":
    main()
