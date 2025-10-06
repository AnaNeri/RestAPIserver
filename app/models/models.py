from pydantic import BaseModel

from config import DEFAULT_STRATEGY, DEFAULT_LANGUAGE

class AnonymizationRequest(BaseModel):
    text: str
    strategy: str = DEFAULT_STRATEGY
    language: str = DEFAULT_LANGUAGE

class EntityExplanation(BaseModel):
    entity: str
    method: str
    type: str
    replacement: str

class AnonymizationResponse(BaseModel):
    original: str
    anonymized: str
    explanations: list[EntityExplanation]
