from .VectorDBEnums import VectorDBEnums
from .providers import QdrantDBProvider
from ...helpers.configurations import Settings
from ...controllers.BaseController import BaseController

class VectorDBProvider:
    def __init__(self, configuration: Settings):
        self.configuration = configuration
        self.base_controller = BaseController()

    def get_vectorDB_(self, provider_name: str):

        db_path = self.base_controller.get_or_create_database_path(database_name=self.configuration.VectorDB_path)

        if provider_name == VectorDBEnums.QDRANT.value:
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.configuration.VectorDB_DistanceMethod
            )

