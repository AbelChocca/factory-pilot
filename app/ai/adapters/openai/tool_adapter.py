from typing import Any

from app.ai.tools.ai_tool import AITool


class OpenAIToolAdapter:

    @staticmethod
    def to_schema(
        tool: AITool,
    ) -> dict[str, Any]:

        return {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "strict": True,
        }