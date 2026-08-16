import asyncio
import json
from typing import Any, AsyncIterator
from uuid import UUID
from openai import BadRequestError

from app.core.logging import logger
from app.ai.chat.schemas.message_schemas import (
    AIToolEvent,
    AIMessageDelta,
    AIMessageStart,
    AIMessageEnd,
    AIStreamError,
    AIToolStart,
    AIStreamEvent
)
from app.ai.adapters.openai.tool_adapter import OpenAIToolAdapter
from app.ai.clients.openai_llm_client import OpenAILLMClient
from app.ai.tools.tool_registry import ToolRegistry
from app.ai.chat.repositories.conversation_repository import (
    AIConversationRepository,
)
from app.ai.chat.schemas.event_schemas import ErrorEvent
from app.ai.chat.types import AIAgentStatus


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

        self.priority = {
            AIAgentStatus.THINKING: 1,
            AIAgentStatus.ANALYZING: 2,
            AIAgentStatus.COMPLETED: 3,
            AIAgentStatus.ERROR: 4,
        }

    async def execute_stream(
        self,
        message: str,
        conversation_id: UUID | None = None,
    ) -> AsyncIterator[AIStreamEvent]:
        
        try:
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

            agent_status = AIAgentStatus.THINKING

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

                            yield AIToolStart(
                                tool_name=item.name,
                                call_id=item.call_id,
                            )

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

                        yield AIToolEvent(
                            call_id=tool_output["call_id"],
                            event=tool_output["event"],
                        )

                        agent_status = self._resolve_agent_status(
                            agent_status,
                            tool_output["agent_status"],
                        )

                input = [
                    tool_output["output"]
                    for tool_output in tool_outputs
                ]

                previous_response_id = response_id


            yield AIMessageEnd(status=agent_status)
        except BadRequestError as exc:

            yield AIStreamError(
                message=(
                    "I couldn't process this AI request. "
                    "Please try again."
                ),
            )

        except Exception:

            yield AIStreamError(
                message=(
                    "Something went wrong while processing "
                    "your request."
                ),
            )

    async def _execute_stream_tool(
        self,
        function_call: Any,
    ) -> dict[str, Any]:

        try:
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
                "call_id": function_call.call_id,
                "agent_status": tool.agent_status,
            }

        except Exception as exc:

            logger.exception(
                "Error executing AI tool '%s'.",
                function_call.name,
            )

            return {
                "output": {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps({
                        "error": str(exc),
                    }),
                },
                "event": ErrorEvent(
                    message=(
                        f"Unable to execute "
                        f"'{function_call.name}'."
                    ),
                ),
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

    def _resolve_agent_status(
        self,
        current_status: AIAgentStatus,
        new_status: AIAgentStatus,
    ) -> AIAgentStatus:

        if self.priority[new_status] > self.priority[current_status]:
            return new_status

        return current_status