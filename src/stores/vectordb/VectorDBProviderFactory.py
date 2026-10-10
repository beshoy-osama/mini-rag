from .VectorDBEnums import VectorDBEnums
from .providers import QdrantDBProvider
from helpers.configurations import Settings
from controllers.BaseController import BaseController

class VectorDBProvider:
    def __init__(self, configuration: Settings):
        self.configuration = configuration
        self.base_controller = BaseController()

    def get_vectorDB_provider(self, provider_name: str):

        db_path = self.base_controller.get_or_create_database_path(database_name=self.configuration.VECTORDB_PATH)

        if provider_name == VectorDBEnums.QDRANT.value:
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.configuration.VECTORDB_DISTANCE_METHOD
            )

