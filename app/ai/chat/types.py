from enum import StrEnum


class AIAgentStatus(StrEnum):
    THINKING = "thinking"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ERROR = "error"