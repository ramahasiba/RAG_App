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
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()