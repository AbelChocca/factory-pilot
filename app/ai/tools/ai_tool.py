from abc import ABC, abstractmethod
from typing import Any

from app.ai.chat.schemas.event_schemas import AIEvent
from app.ai.chat.schemas.message_schemas import AIAgentStatus

class AITool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        ...

    @property
    @abstractmethod
    def agent_status(self) -> AIAgentStatus:
        ...

    @abstractmethod
    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        ...

    def to_event(
        self,
        result: Any,
    ) -> AIEvent | None:
        return None