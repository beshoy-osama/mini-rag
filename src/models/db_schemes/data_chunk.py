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


    @classmethod
    def get_indexes(cls):
        return [
            IndexModel(
                [('chunk_project_id', ASCENDING)],
                unique=False,
                name='chunk_project_id_unique',
            )
        ]

    class Config:
        arbitrary_types_allowed = True