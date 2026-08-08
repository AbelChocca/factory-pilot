from pydantic import BaseModel

class RetrievedKnowledgeDocument(BaseModel):
    content: str
    source: str
    metadata: dict
    similarity: float