import asyncio
import json
from typing import Any, AsyncIterator
from uuid import UUID

from app.ai.chat.schemas.message_schemas import (
    AIEventMessage,
    AIMessageDelta,
    AIMessageStart,
    AIMessageEnd,
    AIStreamEvent
)
from app.ai.adapters.openai.tool_adapter import OpenAIToolAdapter
from app.ai.clients.openai_llm_client import OpenAILLMClient
from app.ai.tools.tool_registry import ToolRegistry
from app.ai.chat.repositories.conversation_repository import (
    AIConversationRepository,
)


class AIStreamChatUseCase:

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

    async def execute_stream(
        self,
        message: str,
        conversation_id: UUID | None = None,
    ) -> AsyncIterator[AIStreamEvent]:

        tools = [
            OpenAIToolAdapter.to_schema(tool)
            for tool in self.tool_registry.tools
        ]

        conversation = await self._get_conversation(
            conversation_id,
        )

        yield AIMessageStart(
            conversation_id=conversation.id,
        )

        input = message

        previous_response_id = (
            conversation.previous_response_id
        )

        while True:

            function_calls: list[Any] = []
            response_id: str | None = None

            async for event in self.llm_client.create_response_stream(
                input=input,
                tools=tools,
                previous_response_id=previous_response_id,
            ):

                if event.type == "response.output_text.delta":

                    yield AIMessageDelta(
                        delta=event.delta,
                    )

                elif event.type == "response.output_item.done":

                    item = event.item

                    if item.type == "function_call":
                        function_calls.append(item)

                elif event.type == "response.completed":

                    response_id = event.response.id

            if response_id is None:
                raise RuntimeError(
                    "OpenAI response completed without an ID."
                )

            if not function_calls:

                await self.conversation_repository.update_response_id(
                    conversation=conversation,
                    response_id=response_id,
                )

                break

            tool_outputs = await asyncio.gather(
                *(
                    self._execute_stream_tool(
                        function_call,
                    )
                    for function_call in function_calls
                )
            )

            for tool_output in tool_outputs:

                if tool_output["event"] is not None:
                    yield AIEventMessage(
                        event=tool_output["event"],
                    )

            input = [
                tool_output["output"]
                for tool_output in tool_outputs
            ]

            previous_response_id = response_id

        yield AIMessageEnd()

    async def _execute_stream_tool(
        self,
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

        output = {
            "type": "function_call_output",
            "call_id": function_call.call_id,
            "output": json.dumps(
                result,
                default=str,
            ),
        }

        return {
            "output": output,
            "event": event,
        }

    async def _get_conversation(
        self,
        conversation_id: UUID | None,
    ):

        if conversation_id is None:
            return await self.conversation_repository.create()

        conversation = (
            await self.conversation_repository.get_by_id(
                conversation_id,
            )
        )

        if conversation is None:
            raise ValueError(
                "Conversation not found."
            )

        return conversation