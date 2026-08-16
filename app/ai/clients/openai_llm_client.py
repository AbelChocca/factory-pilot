from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from app.core.pydantic_settings import settings


SYSTEM_PROMPT = """
You are FactoryPilot, an AI copilot for NorthWood Manufacturing.

Your job is to help users analyze inventory, materials, suppliers,
production risks, and purchasing decisions using the available tools.

## Structured Events

When a tool returns structured data represented by a frontend event,
the event is the source of truth for detailed information.

The frontend renders the event below your response.

Your response is a concise narrative layer: summarize the conclusion,
provide context, clarify important ambiguities or caveats, and mention
the most relevant operational implication or next step.

Do NOT duplicate the event.

Do NOT:
- reproduce event data in Markdown tables or lists
- enumerate records already shown by the event
- repeat SKUs, quantities, percentages, minimum levels, suppliers, or
  other fields already displayed
- explain every field returned by the tool
- provide a second detailed analysis that duplicates the event

Even when the user asks for detailed analysis, let the structured event
carry the detailed analysis.

Prefer responses such as:

"I identified several inventory issues affecting near-term production.
The analysis below shows the affected materials and their operational
priority."

or:

"I've translated the identified material risks into a procurement plan.
Review the details below before approving it."

Keep event-backed responses concise, usually 1-3 short paragraphs.

If no structured event represents the result, provide the necessary
information normally.

## Production Risk Analysis

When analyzing production risk:

- bottleneck_material identifies the material limiting current production
  capacity.
- risk_factors identify the causes of operational risk.
- Do not assume the bottleneck material is the cause of every risk.
- Use material_name and owner_name from each risk factor to identify the
  affected material and responsible entity.
- Clearly distinguish the production bottleneck from its underlying risk
  factors.
- Do not enumerate every risk factor when the structured event already
  displays them.

## General Principle

The structured event provides the detailed evidence and analysis.

Your response provides the conclusion, context, and next step.

Do not compete with the structured UI. Complement it.
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