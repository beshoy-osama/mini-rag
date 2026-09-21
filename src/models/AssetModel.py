from bson import ObjectId

from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnums import DataBaseEnums


class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = db_client[DataBaseEnums.COLLECTION_ASSET_NAME.value]

    @classmethod 
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.initialize_collection_with_indexes()
        return instance

    async def initialize_collection_with_indexes(self):
        """Initialize indexes for the project collection."""
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnums.COLLECTION_ASSET_NAME.value not in all_collections:
            await self.db_client.create_collection(DataBaseEnums.COLLECTION_ASSET_NAME.value)
        indexes = Asset.get_indexes()
        await self.collection.create_indexes(indexes)

    async def create_asset(self, asset: Asset):
        """Create a new asset in the database."""
        asset_dict = asset.model_dump(by_alias=True, exclude_unset=True)
        result = await self.collection.insert_one(asset_dict)
        asset.id = result.inserted_id

        return asset

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str = None):

        query = {
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id
        }

        if asset_type:
            query["asset_type"] = asset_type

        records = await self.collection.find(query).to_list(length=None)

        return [
            Asset(**record)
            for record in records
        ]

    async def get_asset_record(self, asset_project_id: str, asset_name: str):

        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name,
        })

        if record:
            return Asset(**record)
        
        return None
