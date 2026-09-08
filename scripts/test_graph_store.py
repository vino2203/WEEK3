import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from kg_pipeline.document_loader import load_documents
from kg_pipeline.entity_extraction import extract_entities, get_extractor
from kg_pipeline.graph_store import get_driver, store_graph
from kg_pipeline.relationship_mapping import get_mapper, map_relationships
from kg_pipeline.text_splitter import split_documents

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference"
SAMPLE_SIZE = 5


def main() -> None:
    documents = load_documents(REFERENCE_DIR)
    chunks = split_documents(documents)

    extractor = get_extractor()
    mapper = get_mapper()
    driver = get_driver()

    total_entities = 0
    total_relationships = 0

    try:
        for chunk in chunks[:SAMPLE_SIZE]:
            source = chunk.metadata.get("source")
            print("=== Source:", source, "===")

            entities = extract_entities(chunk, extractor=extractor).entities
            if not entities:
                print("  (no entities, skipping)\n")
                continue

            relationships = map_relationships(chunk, entities, mapper=mapper).relationships

            store_graph(driver, entities, relationships, source=source)

            total_entities += len(entities)
            total_relationships += len(relationships)

            for entity in entities:
                print(f"  [{entity.type}] {entity.name}")
            for rel in relationships:
                print(f"  ({rel.source}) -[{rel.type}]-> ({rel.target})")
            print()

        print(f"Stored {total_entities} entities and {total_relationships} relationships.")

        with driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            rel_count = session.run("MATCH ()-->() RETURN count(*) AS c").single()["c"]
        print(f"Neo4j now has {node_count} nodes and {rel_count} relationships total.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
