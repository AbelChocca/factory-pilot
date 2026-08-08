from google import genai
from collections.abc import AsyncIterator

from app.core.pydantic_settings import settings


class GeminiLLMClient:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        ).aio

    async def generate(
        self,
        prompt: str,
    ) -> str:

        response = await self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        return response.text

    async def generate_stream(
        self,
        prompt: str,
    ) -> AsyncIterator[str]:

        response = await self.client.models.generate_content_stream(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

def get_gemini_llm_client() -> GeminiLLMClient:
    return GeminiLLMClient()