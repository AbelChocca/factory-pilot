from pathlib import Path

from app.ai.knowledge.knowledge_dto import KnowledgeDocument
from app.ai.knowledge.markdown_chunker import MarkdownChunker


KNOWLEDGE_DIR = Path("knowledge")


def main() -> None:
    chunker = MarkdownChunker()

    markdown_files = sorted(
        KNOWLEDGE_DIR.glob("*.md")
    )

    if not markdown_files:
        print("No markdown files found.")
        return

    total_chunks = 0

    for path in markdown_files:
        print()
        print("=" * 80)
        print(f"FILE: {path}")
        print("=" * 80)

        content = path.read_text(
            encoding="utf-8"
        )

        document = KnowledgeDocument(
            content=content,
            source=str(path),
            document_type=path.stem,
            metadata={},
        )

        chunks = chunker.chunk(document)

        validate_chunks(chunks)

        print(f"Chunks: {len(chunks)}")

        print_chunk_index(chunks)

        total_chunks += len(chunks)

    print()
    print("=" * 80)
    print(f"TOTAL CHUNKS: {total_chunks}")
    print("=" * 80)

def print_chunk_index(
    chunks: list[KnowledgeDocument],
) -> None:

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"[{index:02d}] "
            f"{chunk.metadata.get('h1')} > "
            f"{chunk.metadata.get('h2')} > "
            f"{chunk.metadata.get('h3')} "
            f"({len(chunk.content)} chars)"
        )

def validate_chunks(
    chunks: list[KnowledgeDocument],
) -> None:

    for index, chunk in enumerate(chunks, start=1):

        assert chunk.content.strip(), (
            f"Chunk {index} is empty"
        )

        assert len(chunk.content) <= MarkdownChunker.MAX_CHUNK_CHARS, (
            f"Chunk {index} exceeds max size: "
            f"{len(chunk.content)} chars"
        )

        assert chunk.metadata.get("h1") is not None, (
            f"Chunk {index} has no h1 context"
        )

if __name__ == "__main__":
    main()