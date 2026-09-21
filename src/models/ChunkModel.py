from .BaseDataModel import BaseDataModel
from .db_schemes.data_chunk import DataChunk
from .enums.DataBaseEnums import DataBaseEnums
from bson.objectid import ObjectId

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):

        super().__init__(db_client=db_client)
        self.collection = db_client[DataBaseEnums.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.initialize_collection_with_indexes()
        return instance

    async def initialize_collection_with_indexes(self):
        """Initialize indexes for the project collection."""
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnums.COLLECTION_CHUNK_NAME.value not in all_collections:
            await self.db_client.create_collection(DataBaseEnums.COLLECTION_CHUNK_NAME.value)
        indexes = DataChunk.get_indexes()
        await self.collection.create_indexes(indexes)

    async def create_chunk(self, chunk: DataChunk):
        """insert a new chunks in the database."""

        chunk_data = chunk.model_dump(by_alias=True, exclude_unset=True)

        result = await self.collection.insert_many(chunk_data)

        chunk.id = result.inserted_id

        return chunk

    async def get_chunk(self, chunk_id: str):
        """Get a chunk by its ID."""

        chunk = await self.collection.find_one({'_id': ObjectId(chunk_id)})

        if chunk is None:
            return None

        return DataChunk(**chunk)

    async def insert_many_chunks(self, chunks: list[DataChunk]):
        """Insert multiple chunks into the database."""

        chunk_data_list = [chunk.model_dump(by_alias=True, exclude_unset=True) for chunk in chunks]

        result = await self.collection.insert_many(chunk_data_list)

        for chunk, inserted_id in zip(chunks, result.inserted_ids):
            chunk.id = inserted_id

        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        """Delete all chunks associated with a specific project ID."""

        result = await self.collection.delete_many({
            "chunk_project_id" : project_id
        })

        return result.deleted_count

    



