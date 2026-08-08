from app.ai.tools.ai_tool import AITool
from typing import Any

class ToolRegistry:

    def __init__(
        self,
        tools: list[AITool],
    ):
        self._tools = {
            tool.name: tool
            for tool in tools
        }

    def get(
        self,
        name: str,
    ) -> AITool:
        try:
            return self._tools[name]
        except KeyError:
            raise ValueError(
                f"AI tool not found: {name}"
            )

    @property
    def tools(self) -> list[AITool]:
        return list(self._tools.values())

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        tool = self.get(name)

        return await tool.execute(arguments)