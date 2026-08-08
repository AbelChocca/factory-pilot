from pydantic import BaseModel, Field

class RagQuerySchema(BaseModel):
    query: str
    limit: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
    )

class RagSearchResult(BaseModel):
    content: str
    source: str
    metadata: dict
    similarity: float


class RagQueryResponse(BaseModel):
    results: list[RagSearchResult]