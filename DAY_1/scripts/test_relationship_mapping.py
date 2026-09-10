import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from kg_pipeline.document_loader import load_documents
from kg_pipeline.entity_extraction import extract_entities, get_extractor
from kg_pipeline.relationship_mapping import get_mapper, map_relationships
from kg_pipeline.text_splitter import split_documents

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference"
SAMPLE_SIZE = 3


def main() -> None:
    documents = load_documents(REFERENCE_DIR)
    chunks = split_documents(documents)

    extractor = get_extractor()
    mapper = get_mapper()

    for chunk in chunks[:SAMPLE_SIZE]:
        print("=== Source:", chunk.metadata.get("source"), "===")
        entities = extract_entities(chunk, extractor=extractor).entities
        if not entities:
            print("  (no entities, skipping)\n")
            continue

        for entity in entities:
            print(f"  [{entity.type}] {entity.name}")

        relationships = map_relationships(chunk, entities, mapper=mapper).relationships
        print("  --- relationships ---")
        for rel in relationships:
            print(f"  ({rel.source}) -[{rel.type}]-> ({rel.target})")
        print()


if __name__ == "__main__":
    main()
