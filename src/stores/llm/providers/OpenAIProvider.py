from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str, api_url: str=None,
                 default_input_max_characters: int=3000, 
                 default_max_output_tokens: int=3000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_max_output_tokens = default_max_output_tokens
        self.default_generation_temperature = default_generation_temperature 
        
        self.generation_model_id = None
        self.embedding_model_id = None

        self.embedding_size = None
        self.client = OpenAI(
            api_key = self.api_key,
            # base_url = self.api_url if self.api_url and len(self.api_url) else None
        )

        self.enums = OpenAIEnums 
        self.logger = logging.getLogger(__name__) 

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: str):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_history: list=[], max_output_token: int=None, temperature: float=None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("generation model id for openai was not found")
            return None
        
        max_output_token = max_output_token if max_output_token is not None else self.default_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )

        response = self.client.chat.completions.create(
            model = self.generation_model_id, 
            messages = chat_history,
            max_tokens=max_output_token,
            temperature=temperature
        ) 
        
        if (
            not response
            or not getattr(response, "choices", None)
            or len(response.choices) == 0
            or not getattr(response.choices[0], "message", None)
            or not getattr(response.choices[0].message, "content", None)
        ):
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message.content
    def embed_text(self, text: str, document_type: str=None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("embedding model for openai was not found")
            return None
        
        response = self.client.embeddings.create(
            model = self.embedding_model_id, 
            input = text 
        ) 

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        return response.data[0].embedding
     
    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()
        
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        } 