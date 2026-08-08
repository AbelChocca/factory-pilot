from fastapi import Depends

from app.ai.clients.openai_llm_client import OpenAILLMClient
from app.ai.chat.use_cases.ai_chat import AIChatUseCase
from app.ai.chat.use_cases.ai_stream_chat import AIStreamChatUseCase
from app.ai.tools.tool_registry import ToolRegistry
from app.ai.clients.openai_llm_client import get_openai_llm_client
from app.ai.tools.dependency import get_tool_registry

from app.ai.chat.dependencies.repositories import get_ai_conversation_repository
from app.ai.chat.repositories.conversation_repository import AIConversationRepository

def get_ai_chat_use_case(
    llm_client: OpenAILLMClient = Depends(
        get_openai_llm_client,
    ),
    tool_registry: ToolRegistry = Depends(
        get_tool_registry,
    ),
    conversation_repository: AIConversationRepository = Depends(
        get_ai_conversation_repository
    )
) -> AIChatUseCase:

    return AIChatUseCase(
        llm_client=llm_client,
        tool_registry=tool_registry,
        conversation_repository=conversation_repository
    )

def get_ai_chat_stream_use_case(
    llm_client: OpenAILLMClient = Depends(
        get_openai_llm_client,
    ),
    tool_registry: ToolRegistry = Depends(
        get_tool_registry,
    ),
    conversation_repository: AIConversationRepository = Depends(
        get_ai_conversation_repository,
    ),
) -> AIStreamChatUseCase:

    return AIStreamChatUseCase(
        llm_client=llm_client,
        tool_registry=tool_registry,
        conversation_repository=conversation_repository,
    )