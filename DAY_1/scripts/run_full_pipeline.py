import sys
import time
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


def main() -> None:
    documents = load_documents(REFERENCE_DIR)
    chunks = split_documents(documents)
    print(f"Loaded {len(documents)} documents, {len(chunks)} chunks", flush=True)

    extractor = get_extractor()
    mapper = get_mapper()
    driver = get_driver()

    total_entities = 0
    total_relationships = 0
    failures = 0
    start = time.time()

    try:
        for i, chunk in enumerate(chunks, start=1):
            source = chunk.metadata.get("source")
            try:
                entities = extract_entities(chunk, extractor=extractor).entities
                if entities:
                    relationships = map_relationships(
                        chunk, entities, mapper=mapper
                    ).relationships
                    store_graph(driver, entities, relationships, source=source)
                    total_entities += len(entities)
                    total_relationships += len(relationships)
            except Exception as exc:
                failures += 1
                print(f"[{i}/{len(chunks)}] FAILED on {source}: {exc}", flush=True)
                continue

            if i % 10 == 0 or i == len(chunks):
                elapsed = time.time() - start
                print(
                    f"[{i}/{len(chunks)}] entities={total_entities} "
                    f"relationships={total_relationships} failures={failures} "
                    f"elapsed={elapsed:.0f}s",
                    flush=True,
                )

        with driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            rel_count = session.run("MATCH ()-->() RETURN count(*) AS c").single()["c"]

        print("\n=== DONE ===")
        print(f"Chunks processed: {len(chunks)} (failures: {failures})")
        print(f"Entities extracted: {total_entities}")
        print(f"Relationships extracted: {total_relationships}")
        print(f"Neo4j total nodes: {node_count}")
        print(f"Neo4j total relationships: {rel_count}")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
