from .BaseDataModel import BaseDataModel
from .db_schemes.project import Project
from .enums.DataBaseEnums import DataBaseEnums


class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = db_client[DataBaseEnums.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.initialize_collection_with_indexes()
        return instance

    async def initialize_collection_with_indexes(self):
        """Initialize indexes for the project collection."""
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnums.COLLECTION_PROJECT_NAME.value not in all_collections:
            await self.db_client.create_collection(DataBaseEnums.COLLECTION_PROJECT_NAME.value)
        indexes = Project.get_indexes()
        await self.collection.create_indexes(indexes)

    async def create_project(self, project: Project):
        """Create a new project in the database."""
        project_data = project.model_dump(by_alias=True, exclude_unset=True)

        result = await self.collection.insert_one(project_data)

        project.id = result.inserted_id

        return project      # return project with updated _id

    async def get_project_or_create_one(self, project_id: str):
        """Get a project by its ID or create a new one if it doesn't exist."""
        project = await self.collection.find_one({"project_id": project_id})

        if project is None:
            new_project = Project(project_id=project_id)
            new_project = await self.create_project(project=new_project)
            return new_project

        return Project(**project)

    async def get_all_projects(self):
        """Get all projects from the database."""
        projects_cursor = self.collection.find()
        projects = []
        async for project in projects_cursor:
            projects.append(Project(**project))
        return projects
