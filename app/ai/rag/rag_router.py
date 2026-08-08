from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.ai.rag.dependencies import get_rag_use_case
from app.ai.rag.rag_use_case import RagUseCase
from app.ai.rag.schema import RagQuerySchema


rag_router = APIRouter(
    prefix="/ai/rag",
    tags=["AI - RAG"],
)


@rag_router.post("/search")
async def search_knowledge(
    request: RagQuerySchema,
    use_case: RagUseCase = Depends(get_rag_use_case),
):
    return StreamingResponse(
        use_case.execute_stream(
            query=request.query,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold,
        ),
        media_type="text/plain",
    )