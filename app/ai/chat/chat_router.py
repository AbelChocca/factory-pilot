from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.ai.chat.schemas.event_schemas import AIChatRequest
from app.ai.chat.use_cases.ai_chat import AIChatUseCase
from app.ai.chat.use_cases.ai_stream_chat import AIStreamChatUseCase
from app.ai.chat.dependencies.use_cases import get_ai_chat_use_case, get_ai_chat_stream_use_case


chat_router = APIRouter(
    prefix="/ai/chat",
    tags=["AI - Chat"],
)


@chat_router.post("")
async def chat(
    request: AIChatRequest,
    use_case: AIChatUseCase = Depends(
        get_ai_chat_use_case,
    ),
):
    return await use_case.execute(
        message=request.message,
        conversation_id=request.conversation_id
    )


@chat_router.post("/stream")
async def chat_stream(
    request: AIChatRequest,
    use_case: AIStreamChatUseCase = Depends(
        get_ai_chat_stream_use_case,
    ),
):
    async def event_stream():
        async for event in use_case.execute_stream(
            message=request.message,
            conversation_id=request.conversation_id,
        ):
            yield (
                f"event: {event.type}\n"
                f"data: {event.model_dump_json()}\n\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )