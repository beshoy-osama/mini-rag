from enum import Enum
from xmlrpc.client import SYSTEM_ERROR

class LLMEnums(Enum):

    openai = "OPENAI"
    cohere = "COHERE"

class OPENAIEnums(Enum):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"