from dataclasses import dataclass

@dataclass
class KnowledgeDocument:
    content: str
    source: str
    document_type: str
    metadata: dict