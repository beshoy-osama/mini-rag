from enum import Enum

class LLMEnums(Enum):

    OPENAI = "openai"
    COHERE = "cohere"
    GEMINI = "gemini"

class OPENAIEnums(Enum):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class GEMINIEnums(Enum):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class COHEREEnums(Enum):

    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnums(Enum):

    DOCUMENT = "document"
    QUERY = "query"

