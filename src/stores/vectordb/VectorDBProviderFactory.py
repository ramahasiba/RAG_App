from .providers import QdrantDB
from .VectorDBEnums import VectorDBEnums
from controllers.BaseController import BaseController

class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str): 
        if provider == VectorDBEnums.QDRANT.value:
            return QdrantDB(
                db_path=self.config.VECTOR_DB_PATH,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )
        
        return None
