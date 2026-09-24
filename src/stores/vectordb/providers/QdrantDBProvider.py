from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethod

from qdrant_client import QdrantClient, models
from qdrant_client.models import ScoredPoint

import logging

import uuid

from typing import List, Dict

class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_method: str):

        self.db_path =db_path
        self. distance_method = None

        self.client = None

        self.logger = logging.getLogger(__name__)

        if distance_method == DistanceMethod.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethod.DOT.value:
            self.distance_method = models.Distance.DOT
        else:
            self.logger.error("error in distance_method value")
            return None


    def connect(self):
        self.client = QdrantClient(path=self.db_path)


    def disconnect(self):
        self.client = None


    def is_collection_exist(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)


    def list_all_collections(self) -> List:
        return self.client.get_collections()


    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str, 
                        embedding_size: int = 384, do_reset: bool = False):

            if do_reset == 1:
                self.delete_collection(collection_name=collection_name)

            if not self.is_collection_exist(collection_name=collection_name):

                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=embedding_size, distance=self.distance_method
                    ),
                )

                return True

            return False


    def delete_collection(self, collection_name: str):
        if self.is_collection_exist(collection_name=collection_name):
            self.client.delete_collection(collection_name=collection_name)


    def insert_one(
        self,
        collection_name: str,
        vector: List[float],
        text: str = None,
        metadata: Dict[str, str] = None,
        record_id: str = None,
            ):

        if not self.is_collection_exist(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False

        point_id = record_id if record_id is not None else str(uuid.uuid4())

        # Prepare Payload
        payload = {}
        if text is not None:
            payload["text"] = text
        if metadata:
            payload.update(metadata)

        # Insert the point into the collection
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                ],
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to insert record into {collection_name}: {e}")
            return False



    def insert_many(self, collection_name: str,
                    texts: List[str], 
                    vectors: List[List[float]],
                    metadatas: List[Dict[str, str]] = None, 
                    record_ids: List[str] = None, 
                    batch_size: int = 50):

        if not self.is_collection_exist(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False

        if not vectors:
            self.logger.error("No vectors provided for insertion.")
            return False

        if metadatas is None:
            metadatas = [{}] * len(texts)


        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        # insert in batches
        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]

            batch_points = [
                    models.PointStruct(
                        id=record_ids[i + x],
                        vector=batch_vectors[x],
                        payload={"text": batch_texts[x], "metadata": batch_metadatas[x]}
                        )
                for x in range(len(batch_texts))
            ]

            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points
                )
            except Exception as e:
                self.logger.error(f"Failed to insert batch into {collection_name}: {e}")
                return False

        return True


    def search_by_vector(self, collection_name: str, query_vector: List[float], top_k: int = 5) -> List[ScoredPoint] | None:

        if not self.is_collection_exist(collection_name=collection_name):
            self.logger.error(f"Collection '{collection_name}' does not exist.")
            return None

        self.logger.info(
            f"Searching in collection '{collection_name}' for top {top_k} similar vectors."
        )

        try:
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_vector, 
                limit=top_k,
                with_payload=True, 
                with_vectors=False,
            )
            return response.points

        except Exception as e:
            self.logger.error(
                f"Vector search failed in collection '{collection_name}': {e}"
            )
            return None