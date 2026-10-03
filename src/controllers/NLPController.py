from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnums

from typing import List
import json

class NLPController(BaseController):

    def __init__(self, vector_DB_client, embedding_client, generation_client):
        super().__init__()
        self.vector_DB_client = vector_DB_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client

    def create_collection_name(self, project_id: str):
        """
        Creates a collection name based on the project ID.
        """
        return f"collection_{project_id}".strip()

    def reset_vectorDB_collection(self, project: Project):
        """
        Resets the vectorDB collection for the given project.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)

        # Reset the vectorDB collection for the given collection_name
        self.vector_DB_client.delete_collection(collection_name=collection_name)

    def get_vectorDB_collection_info(self, project: Project):
        """
        Retrieves information about the vectorDB collection for the given project.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vector_DB_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
            ) 

    def index_into_vectorDB(self, project: Project, chunks: List[DataChunk],
                            do_reset: bool = False):

        #step 1: Create collection
        collection_name = self.create_collection_name(project_id=project.project_id)

        #step2: manage items in the collection
        texts = [chunk.chunk_text for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]

        vectors = [
            self.embedding_client.embed_text(
                text=text,
                document_type=DocumentTypeEnums.DOCUMENT.value,
            )
            for text in texts
        ]

        #step3: create collection if not exist
        if not self.vector_DB_client.is_collection_exist(collection_name=collection_name):
            self.vector_DB_client.create_collection(collection_name=collection_name,
                                                    embedding_size=self.embedding_client.embedding_size)
        else:
            if do_reset:
                self.vector_DB_client.delete_collection(collection_name=collection_name)
                self.vector_DB_client.create_collection(collection_name=collection_name,
                                                        embedding_size=self.embedding_client.embedding_size)
                
        #step4: insert items into the collection
        self.vector_DB_client.insert_many(
                    collection_name=collection_name,
                    vectors=vectors,
                    texts=texts,
                    metadatas=metadata
                )

        return True

    def search_vectorDB_collection(self, project: Project, query_text: str, top_k: int = 5):

        collection_name = self.create_collection_name(project_id=project.project_id)

        # Step 1: Embed the query text
        query_vector = self.embedding_client.embed_text(
            text=query_text,
            document_type=DocumentTypeEnums.QUERY.value,
        )

        if not query_vector or len(query_vector) == 0:
            return False

        # Step 2: Perform the search in the vectorDB
        search_results = self.vector_DB_client.search_by_vector(
            collection_name=collection_name,
            query_vector=query_vector,
            top_k=top_k
        )

        return json.loads(
                    json.dumps(search_results, default=lambda x: x.__dict__)
                    ) 