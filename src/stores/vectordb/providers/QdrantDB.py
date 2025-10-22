from ..VectorDBInterface import VectorDBInterface
import logging
from ..VectorDBEnums import DistanceMethodEnums
from typing import List
from qdrant_client import QdrantClient, models
from models.db_schemes import RetrievedDocument

class QdrantDB(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str):
        self.db_path = db_path
        self.client = None 
        self.distance_method = models.Distance.COSINE

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT_PRODUCT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path) 

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str) -> bool:
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
         
    def create_collection(self, collection_name: str,
                          embedding_size: int,
                          do_reset: bool = False) -> bool:
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            print("embedding info:", embedding_size, self.distance_method)
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True
        return False


    def insert_one(self, collection_name: str, text: str, vector: List,
                   metadata: dict = None,
                   record_id: str = None):
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Can not insert nre record to non-existed collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=[record_id],
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error when inserting record to collection {collection_name}: {e}")
            return False

        return True
    

    def insert_many(self, collection_name: str, texts: List, vectors: List,
                   metadatas: List = None,
                   record_ids: List = None,
                   batch_size: int = 50):
        
        if metadatas is None:
            metadatas = [None] * len(texts)
            
        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i: batch_end]
            batch_vectors = vectors[i: batch_end]
            batch_metadatas = metadatas[i: batch_end]
            batch_record_ids = record_ids[i: batch_end]
            batch_records = [
                models.Record(
                    id=batch_record_ids[x], 
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadatas[x]
                    }
                )
                for x in range(len(batch_texts))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error when inserting batch records to collection {collection_name}: {e}")
                return False

        return True
    
    def search_by_vector(self, collection_name: str, vector: List, limit: int=5):
        # store retrieved documents
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        if not results or len(results) == 0:
            return None
        
        return [
            RetrievedDocument(**{
                "text": hit.payload["text"], 
                "score": hit.score
            })
            for hit in results
        ]