from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums, DocumentTypeEnum
import cohere
import logging

class CohereProvider(LLMInterface):
    def __init__(self, api_key: str, 
                 default_input_max_characters: int=3000, 
                 default_max_output_tokens: int=3000,
                 default_generation_temprature: float=0.1):
        
        self.api_key = api_key 
        self.default_input_max_characters = default_input_max_characters
        self.default_max_output_tokens = default_max_output_tokens
        self.default_generation_temprature = default_generation_temprature 
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.client = cohere.Client(api_key=self.api_key)

        self.logger = logging.getLogger(__name__) 

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: str):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        } 
    
    def generate_text(self, prompt: str, chat_history: list=[], max_output_token: int=None, temprature: float=None):
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("generation model id for cohere was not found")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_max_output_tokens
        temprature = temprature if temprature else self.default_generation_temprature
         
        response = self.client.chat(
            model=self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            temprature=temprature,
            max_tokens=max_output_token
        )

        if not response or not response.text:
            self.logger.error("Error while generating text with cohere")
            return None
        
        return response.text
    
    def embed_text(self, text: str, document_type: str=None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("embedding model for openai was not found")
            return None
        
        input_type = CohereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CohereEnums.QUERY.value
        
        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [text],
            input_type = input_type,
        )

        response = self.client.embed( 
            model = self.embedding_model_id, 
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types=['float'] 
        ) 

        if not response or not response.embeddings or not response.embeddings.float_:
            self.logger.error("Error while embedding text with Cohere") 
            return None
        
        return response.embeddings.float_[0]