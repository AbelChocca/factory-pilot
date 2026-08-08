import asyncio
import json
from typing import Any
from uuid import UUID

from app.ai.chat.repositories.conversation_repository import (
    AIConversationRepository,
)
from app.ai.adapters.openai.tool_adapter import OpenAIToolAdapter
from app.ai.clients.openai_llm_client import OpenAILLMClient
from app.ai.tools.tool_registry import ToolRegistry
from app.ai.chat.schemas.event_schemas import AIChatResponse, AIEvent

class AIChatUseCase:

    def __init__(
        self,
        llm_client: OpenAILLMClient,
        tool_registry: ToolRegistry,
        conversation_repository: AIConversationRepository,
    ):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.conversation_repository = (
            conversation_repository
        )

    async def execute(
        self,
        message: str,
        conversation_id: UUID | None = None,
    ) -> AIChatResponse:

        events: list[AIEvent] = []

        tools = [
            OpenAIToolAdapter.to_schema(tool)
            for tool in self.tool_registry.tools
        ]

        if conversation_id is None:

            conversation = (
                await self.conversation_repository.create()
            )

        else:

            conversation = (
                await self.conversation_repository.get_by_id(
                    conversation_id,
                )
            )

            if conversation is None:
                raise ValueError(
                    "Conversation not found."
                )

        async def execute_tool(
            function_call: Any,
        ) -> dict[str, Any]:

            arguments = json.loads(
                function_call.arguments,
            )

            tool = self.tool_registry.get(
                function_call.name,
            )

            result = await tool.execute(
                arguments=arguments,
            )

            event = tool.to_event(result)

            if event is not None:
                events.append(event)

            return {
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": json.dumps(
                    result,
                    default=str,
                ),
            }

        input = message
        previous_response_id = (
            conversation.previous_response_id
        )

        while True:
            response = await self.llm_client.create_response(
                input=input,
                tools=tools,
                previous_response_id=previous_response_id,
            )

            function_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not function_calls:
                await self.conversation_repository.update_response_id(
                    conversation=conversation,
                    response_id=response.id,
                )

                return AIChatResponse(
                    conversation_id=conversation.id,
                    message=response.output_text,
                    events=events,
                )

            tool_outputs = await asyncio.gather(
                *(
                    execute_tool(function_call)
                    for function_call in function_calls
                )
            )

            input = tool_outputs
            previous_response_id = response.id