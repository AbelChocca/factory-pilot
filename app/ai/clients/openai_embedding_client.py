from openai import AsyncOpenAI

from app.core.pydantic_settings import settings


class OpenAIEmbeddingClient:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        response = await self.client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
            dimensions=settings.GEMINI_EMBEDDING_DIMENSION
        )

        return response.data[0].embedding

    async def embed_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        response = await self.client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=texts,
            dimensions=settings.GEMINI_EMBEDDING_DIMENSION
        )

        return [
            item.embedding
            for item in response.data
        ]

def get_openai_embedding_client() -> OpenAIEmbeddingClient:

    return OpenAIEmbeddingClient()