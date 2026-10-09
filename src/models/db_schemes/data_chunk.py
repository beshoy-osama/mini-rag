from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId
from pymongo import ASCENDING, IndexModel

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            IndexModel(
                [('chunk_project_id', ASCENDING)],
                unique=False,
                name='chunk_project_id_index',
            )
        ]

class RetrievalDocuments(BaseModel):
    text: str
    score: float
    metadata: dict = Field(default_factory=dict)
