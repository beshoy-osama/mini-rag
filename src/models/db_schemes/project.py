from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId
from pymongo import ASCENDING, IndexModel

class Project(BaseModel):

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)

    @field_validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')

        return value

    @classmethod
    def get_indexes(cls):
        return [
            IndexModel(
                [('project_id', ASCENDING)],
                unique=True,
                name='project_id_unique',
            )
        ]

    class Config:
        arbitrary_types_allowed = True