from google import genai

from app.core.pydantic_settings import settings


class GeminiEmbeddingClient:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        ).aio

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        result = await self.client.models.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            contents=text,
            config={
                "output_dimensionality": 768,
            },
        )

        return result.embeddings[0].values

    async def embed_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        result = await self.client.models.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            contents=texts,
            config={
                "output_dimensionality": 768,
            },
        )

        return [
            embedding.values
            for embedding in result.embeddings
        ]

def get_gemini_embedding_client() -> GeminiEmbeddingClient:

    return GeminiEmbeddingClient()