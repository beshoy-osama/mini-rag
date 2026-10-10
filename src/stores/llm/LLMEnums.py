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
    ASSISTANT = "model"

class COHEREEnums(Enum):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnums(Enum):

    DOCUMENT = "document"
    QUERY = "query"
