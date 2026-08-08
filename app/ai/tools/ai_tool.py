from abc import ABC, abstractmethod
from typing import Any

from app.ai.chat.schemas.event_schemas import AIEvent

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