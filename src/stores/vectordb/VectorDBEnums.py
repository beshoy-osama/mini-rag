from enum import Enum

class DistanceMethod(Enum):

    COSINE = "cosine"
    DOT = "dot"

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"