from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str 
    PINECONE_API_KEY: str
    OPENAI_API_KEY: str
    APP_NAME: str  

    FILE_ALLOWED_EXTENSIONS: list[str] = []
    MAX_FILE_SIZE: int  # in MB
    FILE_DEFAULT_CHUNK_SIZE: int 

    MONGODB_URL: str
    MONGODB_DATABASE: str
    
    GENERATION_BACKEND: str 
    EMBEDDING_BACKEND: str 
    
    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: str = None

    INPUT_DEFAULT_MAX_CHARACTERS: int = 1024
    GENERATION_DEFAULT_MAX_TOKENS: int = 200
    GENERATION_DEFAULT_TEMPRATURE: float = 0.1
    
    # ---------- Vector DB Config ----------
    VECTOR_DB_BACKEND: str = "QDRANT"
    VECTOR_DB_PATH: str = "qdrant_db"
    VECTOR_DB_DISTANCE_METHOD: str = "COSINE" 

    # ---------- Template Config ----------
    DEFAULT_LANG: str = "en"

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()