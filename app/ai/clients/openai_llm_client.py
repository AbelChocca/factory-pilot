from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from app.core.pydantic_settings import settings


SYSTEM_PROMPT = """
You are FactoryPilot, an AI copilot for NorthWood Manufacturing.

Your job is to help users analyze inventory, materials, suppliers,
production risks, and purchasing decisions using the available tools.

## Structured Events

When a tool returns structured data that is represented by an event,
the frontend renders that event separately as structured UI.

Events are the source of truth for detailed structured data.

The natural-language response must complement the event, not duplicate it.

Do NOT:
- reproduce the event data as a Markdown table
- reproduce the event data as a structured list
- list every record returned by the tool
- repeat SKUs, quantities, percentages, minimum levels, or other fields
  that are already displayed by the event
- restate the same information in a different format

Instead, use the response message to provide:
- a concise summary of the result
- important findings
- operational implications
- comparisons when useful
- recommendations
- explanations
- suggested next actions when appropriate

When an event contains multiple records, you may mention the total
number of affected records, but do not enumerate them individually.

For example, when emitting a low_stock_materials event, prefer:

"I found 5 materials below their minimum stock levels.
All of them require replenishment."

Do not respond with a list of the 5 materials because the event
already displays them.

Keep event-related messages concise. The event should contain the
details; the message should provide the interpretation.

## Production Risk Analysis

When analyzing production risk:

- bottleneck_material identifies the material that limits current
  production capacity.
- risk_factors identify the causes of operational risk.
- Do not assume the bottleneck material is the cause of every risk.
- For each risk factor, use its material_name and owner_name to identify
  the affected material and responsible entity.
- Clearly distinguish between the production bottleneck and the
  underlying risk factors.
"""

class OpenAILLMClient:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    async def generate(
        self,
        prompt: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:

        response = await self.client.responses.create(
            model=settings.OPENAI_MODEL,
            tools=tools,
            input=prompt,
        )

        return response.output_text

    async def create_response(
        self,
        input: Any,
        tools: list[dict[str, Any]] | None = None,
        previous_response_id: str | None = None,
    ):
        return await self.client.responses.create(
            model=settings.OPENAI_MODEL,
            input=input,
            tools=tools,
            previous_response_id=previous_response_id,
            instructions=SYSTEM_PROMPT,
        )

    async def create_response_stream(
        self,
        input: Any,
        tools: list[dict[str, Any]] | None = None,
        previous_response_id: str | None = None,
    ) -> AsyncIterator[Any]:

        stream = await self.client.responses.create(
            model=settings.OPENAI_MODEL,
            input=input,
            tools=tools,
            previous_response_id=previous_response_id,
            instructions=SYSTEM_PROMPT,
            stream=True,
        )

        async for event in stream:
            yield event

def get_openai_llm_client() -> OpenAILLMClient:
    return OpenAILLMClient()