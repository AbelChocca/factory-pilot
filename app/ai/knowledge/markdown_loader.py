from pathlib import Path

from app.ai.knowledge.knowledge_dto import KnowledgeDocument


class MarkdownLoader:

    def __init__(
        self,
        knowledge_path: Path,
    ):
        self.knowledge_path = knowledge_path

    def load(self) -> list[KnowledgeDocument]:

        documents: list[KnowledgeDocument] = []

        for path in sorted(
            self.knowledge_path.glob("*.md")
        ):
            documents.append(
                self._load_file(path)
            )

        return documents

    def _load_file(
        self,
        path: Path,
    ) -> KnowledgeDocument:

        content = path.read_text(
            encoding="utf-8",
        )

        return KnowledgeDocument(
            content=content,
            source=str(
                path.relative_to(
                    self.knowledge_path.parent
                )
            ),
            document_type=self._get_document_type(path),
            metadata={
                "filename": path.name,
            },
        )

    def _get_document_type(
        self,
        path: Path,
    ) -> str:

        return path.stem