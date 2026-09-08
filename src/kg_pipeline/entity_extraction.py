from typing import Literal

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

ENTITY_TYPES = [
    "SCHEME",
    "DEPARTMENT",
    "BENEFICIARY",
    "DISTRICT",
    "ORGANISATION",
    "FUNDING_TYPE",
    "BENEFIT_TYPE",
]

EntityType = Literal[
    "SCHEME",
    "DEPARTMENT",
    "BENEFICIARY",
    "DISTRICT",
    "ORGANISATION",
    "FUNDING_TYPE",
    "BENEFIT_TYPE",
]


class Entity(BaseModel):
    name: str = Field(description="The exact entity name as it appears in the text")
    type: EntityType = Field(description=f"One of: {', '.join(ENTITY_TYPES)}")


class ExtractedEntities(BaseModel):
    entities: list[Entity]


_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You extract named entities from Tamil Nadu government scheme documents. "
            f"Only use these entity types: {', '.join(ENTITY_TYPES)}. "
            "Extract only entities explicitly present in the text. Do not invent entities. "
            "Skip boilerplate navigation text (e.g. 'Schemes', 'Search', 'A To Z').",
        ),
        ("human", "{text}"),
    ]
)


def get_extractor(model: str = "gpt-4o-mini"):
    llm = ChatOpenAI(model=model, temperature=0)
    structured_llm = llm.with_structured_output(ExtractedEntities)
    return _PROMPT | structured_llm


def extract_entities(chunk: Document, extractor=None) -> ExtractedEntities:
    if extractor is None:
        extractor = get_extractor()
    return extractor.invoke({"text": chunk.page_content})
