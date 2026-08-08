from app.ai.knowledge.schema import RetrievedKnowledgeDocument

class ContextBuilder:

    def build(
        self,
        documents: list[RetrievedKnowledgeDocument],
    ) -> str:

        return "\n\n---\n\n".join(
            self._format_document(document)
            for document in documents
        )

    def _format_document(
        self,
        document: RetrievedKnowledgeDocument,
    ) -> str:

        return (
            f"[Source: {document.source}]\n"
            f"{document.content}"
        )

def get_context_builder() -> ContextBuilder:
    return ContextBuilder()