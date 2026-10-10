from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId
from pymongo import ASCENDING, IndexModel

from datetime import datetime, timezone

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config: dict = Field(default=None)
    asset_pushed_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def get_indexes(cls):
        return [
            IndexModel([("asset_project_id", ASCENDING)],
                        name="asset_project_id_index",
                        unique=False),

            IndexModel([("asset_project_id", ASCENDING),
                        ("asset_name", ASCENDING)],
                        name="asset_project_id_asset_name_index",
                        unique=True),

        ]

    class Config:
        arbitrary_types_allowed = True