# scripts/test_gemini_embedding.py

import asyncio

from app.ai.clients.gemini_embeddings_client import GeminiEmbeddingClient


async def main():
    client = GeminiEmbeddingClient()

    embedding = await client.embed(
        "MDF Board 15 mm is used for office desks."
    )

    print(f"Dimension: {len(embedding)}")
    print(f"First values: {embedding[:5]}")


if __name__ == "__main__":
    asyncio.run(main())