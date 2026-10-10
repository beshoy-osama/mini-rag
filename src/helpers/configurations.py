from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str 
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGO_URL: str
    MONGODB_DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str 
    OPENAI_API_URL: str 

    COHERE_API_KEY: str

    GEMINI_API_KEY: str 

    GENERATION_MODEL_ID: str 
    EMBEDDING_MODEL_ID: str 
    EMBEDDING_MODEL_SIZE: int 
    INPUT_DAFAULT_MAX_CHARACTERS: int 
    GENERATION_DAFAULT_MAX_TOKENS: int 
    GENERATION_DAFAULT_TEMPERATURE: float 

    VECTORDB_BACKEND : str
    VECTORDB_PATH : str
    VECTORDB_DISTANCE_METHOD : str = None

    DEFAULT_LANGUAGE: str 
    ENGLISH_LANGUAGE: str 
    ARABIC_LANGUAGE: str 


    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

def get_settings() -> Settings:
    return Settings()
