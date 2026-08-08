import re

from app.ai.knowledge.knowledge_dto import KnowledgeDocument


class MarkdownChunker:
    HEADING_PATTERN = re.compile(
        r"^(#{1,3})\s+(.+)$"
    )

    MAX_CHUNK_CHARS = 3000
    MIN_CHUNK_CHARS = 0
    OVERLAP_CHARS = 0

    def chunk(
        self,
        document: KnowledgeDocument,
    ) -> list[KnowledgeDocument]:

        semantic_chunks = self._split_by_headings(document)

        resized_chunks = self._resize_chunks(
            semantic_chunks
        )

        final_chunks: list[KnowledgeDocument] = []

        for chunk in resized_chunks:
            final_chunks.extend(
                self._split_large_chunk(chunk)
            )

        return final_chunks

    def _split_by_headings(
        self,
        document: KnowledgeDocument,
    ) -> list[KnowledgeDocument]:

        lines = document.content.splitlines()

        chunks: list[KnowledgeDocument] = []

        current_content: list[str] = []

        current_h1: str | None = None
        current_h2: str | None = None
        current_h3: str | None = None

        pending_heading: str | None = None

        for line in lines:

            match = self.HEADING_PATTERN.match(line)

            if match:
                level = len(match.group(1))
                title = match.group(2).strip()

                # Flush previous content before changing hierarchy.
                if current_content:
                    chunks.append(
                        self._build_chunk(
                            document=document,
                            content=current_content,
                            h1=current_h1,
                            h2=current_h2,
                            h3=current_h3,
                        )
                    )

                    current_content = []

                # Update hierarchy.
                if level == 1:
                    current_h1 = title
                    current_h2 = None
                    current_h3 = None

                elif level == 2:
                    current_h2 = title
                    current_h3 = None

                elif level == 3:
                    current_h3 = title

                # Keep the heading pending.
                pending_heading = line

                continue

            # Ignore empty lines before real content.
            if not line.strip():
                continue

            # We found real content after a heading.
            if pending_heading is not None:
                current_content.append(pending_heading)
                pending_heading = None

            current_content.append(line)

        # Flush final content.
        if current_content:
            chunks.append(
                self._build_chunk(
                    document=document,
                    content=current_content,
                    h1=current_h1,
                    h2=current_h2,
                    h3=current_h3,
                )
            )

        return chunks

    def _build_chunk(
        self,
        document: KnowledgeDocument,
        content: list[str],
        h1: str | None,
        h2: str | None,
        h3: str | None,
    ) -> KnowledgeDocument:

        body = "\n".join(content).strip()

        hierarchy = [
            heading
            for heading in (h1, h2, h3)
            if heading
        ]

        context = " > ".join(hierarchy)

        if context:
            text = f"{context}\n\n{body}"
        else:
            text = body

        metadata = {
            **document.metadata,
            "h1": h1,
            "h2": h2,
            "h3": h3,
        }

        if h3:
            metadata["entity"] = h3

        elif h2:
            metadata["section"] = h2

        return KnowledgeDocument(
            content=text,
            source=document.source,
            document_type=document.document_type,
            metadata=metadata,
        )

    def _merge_chunks(
        self,
        current: KnowledgeDocument,
        next_chunk: KnowledgeDocument,
    ) -> KnowledgeDocument:

        content = (
            f"{current.content}\n\n"
            f"{next_chunk.content}"
        )

        metadata = {
            **current.metadata,
            "merged": True,
        }

        return KnowledgeDocument(
            content=content,
            source=current.source,
            document_type=current.document_type,
            metadata=metadata,
        )

    def _split_large_chunk(
        self,
        chunk: KnowledgeDocument,
    ) -> list[KnowledgeDocument]:

        if len(chunk.content) <= self.MAX_CHUNK_CHARS:
            return [chunk]

        paragraphs = chunk.content.split("\n\n")

        chunks: list[KnowledgeDocument] = []

        current: list[str] = []
        current_length = 0

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            paragraph_length = len(paragraph)

            if (
                current
                and current_length + paragraph_length
                > self.MAX_CHUNK_CHARS
            ):
                chunks.append(
                    self._create_split_chunk(
                        chunk,
                        current,
                    )
                )

                current = []
                current_length = 0

            current.append(paragraph)
            current_length += paragraph_length

        if current:
            chunks.append(
                self._create_split_chunk(
                    chunk,
                    current,
                )
            )

        return chunks

    def _create_split_chunk(
        self,
        original: KnowledgeDocument,
        content: list[str],
    ) -> KnowledgeDocument:

        body = "\n\n".join(content)

        return KnowledgeDocument(
            content=body,
            source=original.source,
            document_type=original.document_type,
            metadata={
                **original.metadata,
            },
        )

    def _resize_chunks(
        self,
        chunks: list[KnowledgeDocument],
    ) -> list[KnowledgeDocument]:

        resized: list[KnowledgeDocument] = []

        current: KnowledgeDocument | None = None

        for chunk in chunks:

            if current is None:
                current = chunk
                continue

            if self._can_merge(current, chunk):
                current = self._merge_chunks(
                    current,
                    chunk,
                )

            else:
                resized.append(current)
                current = chunk

        if current is not None:
            resized.append(current)

        return resized


    def _can_merge(
        self,
        current: KnowledgeDocument,
        next_chunk: KnowledgeDocument,
    ) -> bool:

        next_h3 = next_chunk.metadata.get("h3")

        # Metadata belongs to the previous entity/section.
        if next_h3 == "Metadata":
            if not self._same_section(current, next_chunk):
                return False

            return (
                len(current.content)
                + 2
                + len(next_chunk.content)
                <= self.MAX_CHUNK_CHARS
            )

        return False


    def _same_section(
        self,
        first: KnowledgeDocument,
        second: KnowledgeDocument,
    ) -> bool:

        return (
            first.metadata.get("h1")
            == second.metadata.get("h1")
            and first.metadata.get("h2")
            == second.metadata.get("h2")
        )