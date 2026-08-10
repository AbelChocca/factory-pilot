from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.ai.chat.schemas.event_schemas import AIEvent


class AIMessageStart(BaseModel):
    type: Literal["message_start"] = "message_start"
    conversation_id: UUID


class AIMessageDelta(BaseModel):
    type: Literal["message_delta"] = "message_delta"
    delta: str


class AIMessageEnd(BaseModel):
    type: Literal["message_end"] = "message_end"


class AIToolEvent(BaseModel):
    type: Literal["tool_event"] = "tool_event"
    event: AIEvent


class AIStreamError(BaseModel):
    type: Literal["error"] = "error"
    message: str

AIStreamEvent = (
    AIMessageStart
    | AIMessageDelta
    | AIMessageEnd
    | AIToolEvent
    | AIStreamError
)