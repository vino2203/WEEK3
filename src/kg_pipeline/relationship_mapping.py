from typing import Literal

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from kg_pipeline.entity_extraction import Entity

RELATIONSHIP_TYPES = [
    "ADMINISTERED_BY",
    "TARGETS",
    "FUNDED_AS",
    "PROVIDES_BENEFIT",
    "LOCATED_IN",
    "OPERATED_BY",
]

RelationshipType = Literal[
    "ADMINISTERED_BY",
    "TARGETS",
    "FUNDED_AS",
    "PROVIDES_BENEFIT",
    "LOCATED_IN",
    "OPERATED_BY",
]


class Relationship(BaseModel):
    source: str = Field(description="Name of the source entity")
    type: RelationshipType = Field(description=f"One of: {', '.join(RELATIONSHIP_TYPES)}")
    target: str = Field(description="Name of the target entity")


class ExtractedRelationships(BaseModel):
    relationships: list[Relationship]


_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You map relationships between entities already extracted from a Tamil Nadu "
            "government scheme document. "
            f"Only use these relationship types: {', '.join(RELATIONSHIP_TYPES)}. "
            "Only create a relationship if it is a source entity and a target entity from "
            "the given entity list, and the text supports the relationship. "
            "Do not invent entities or relationships not grounded in the text.",
        ),
        (
            "human",
            "Text:\n{text}\n\nEntities:\n{entities}",
        ),
    ]
)


def get_mapper(model: str = "gpt-4o-mini"):
    llm = ChatOpenAI(model=model, temperature=0)
    structured_llm = llm.with_structured_output(ExtractedRelationships)
    return _PROMPT | structured_llm


def map_relationships(
    chunk: Document, entities: list[Entity], mapper=None
) -> ExtractedRelationships:
    if mapper is None:
        mapper = get_mapper()
    entity_list = "\n".join(f"- ({e.type}) {e.name}" for e in entities)
    return mapper.invoke({"text": chunk.page_content, "entities": entity_list})
