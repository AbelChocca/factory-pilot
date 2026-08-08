from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from app.core.pydantic_settings import settings


SYSTEM_PROMPT = """
You are FactoryPilot, an AI copilot for NorthWood Manufacturing.

Your job is to help users analyze inventory, materials, suppliers,
and purchasing decisions using the available tools.

When a tool returns structured data that is represented by an event,
do not reproduce that data as a Markdown table or duplicate structured
list in your response.

The frontend renders structured event data separately.

Instead, use your response message to provide:
- concise analysis
- important findings
- comparisons
- recommendations
- explanations
- suggested next actions

You may mention important values or facts from tool results when
they are relevant to your analysis, but do not reproduce the entire
structured dataset.

Events are the source of truth for structured UI data.
The message is for natural-language explanation and reasoning.

When analyzing production risk:
- bottleneck_material identifies the material that limits current production capacity.
- risk_factors identify the causes of operational risk.
- Do not assume the bottleneck material is the cause of every risk.
- For each risk factor, use its material_name and owner_name to identify the affected material and responsible entity.
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