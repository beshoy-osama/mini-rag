from abc import ABC, abstractmethod
from typing import List
from qdrant_client.models import ScoredPoint

class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def is_collection_exist(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, 
                        embedding_size: int, do_reset: bool = False):
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def insert_one(self, collection_name: str, vector: List[float], 
                metadata: dict = None, record_id: str = None):
        pass

    @abstractmethod
    def insert_many(self, collection_name: str, vectors: List[List[float]],
                metadatas: List[dict] = None, record_ids: List[str] = None, batch_size: int = 100):
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, query_vector: List[float], 
                    top_k: int = 10) -> List[ScoredPoint] | None:
        pass