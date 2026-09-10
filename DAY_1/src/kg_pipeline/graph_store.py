import os

from neo4j import Driver, GraphDatabase

from kg_pipeline.entity_extraction import ENTITY_TYPES, Entity
from kg_pipeline.relationship_mapping import RELATIONSHIP_TYPES, Relationship

# Cypher does not allow parameterized labels/relationship types, so we interpolate
# them directly. This is only safe because Entity.type and Relationship.type are
# constrained to these fixed whitelists via Pydantic Literal types.
assert set(ENTITY_TYPES) and set(RELATIONSHIP_TYPES)


def get_driver() -> Driver:
    uri = os.environ["NEO4J_URI"]
    username = os.environ["NEO4J_USERNAME"]
    password = os.environ["NEO4J_PASSWORD"]
    return GraphDatabase.driver(uri, auth=(username, password))


def _merge_entity(tx, entity: Entity, source: str) -> None:
    query = f"MERGE (n:{entity.type} {{name: $name}}) SET n.source = $source"
    tx.run(query, name=entity.name, source=source)


def _merge_relationship(tx, relationship: Relationship) -> None:
    query = (
        "MATCH (a {name: $source}), (b {name: $target}) "
        f"MERGE (a)-[r:{relationship.type}]->(b)"
    )
    tx.run(query, source=relationship.source, target=relationship.target)


def store_graph(
    driver: Driver,
    entities: list[Entity],
    relationships: list[Relationship],
    source: str,
    database: str | None = None,
) -> None:
    database = database or os.environ.get("NEO4J_DATABASE", "neo4j")
    with driver.session(database=database) as session:
        for entity in entities:
            session.execute_write(_merge_entity, entity, source)
        for relationship in relationships:
            session.execute_write(_merge_relationship, relationship)
