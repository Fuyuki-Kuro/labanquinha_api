# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Variáveis de Desenvolvimento
    MONGO_URI: str
    DATABASE_NAME: str

    # --- ADICIONE AS VARIÁVEIS DE TESTE AQUI ---
    MONGO_URI_TEST: str
    DATABASE_NAME_TEST: str

    # Variáveis de Segurança (JWT)
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Carrega as variáveis do arquivo .env
    model_config = SettingsConfigDict(env_file=".env")

# Cria uma instância única das configurações para ser usada na aplicação
settings = Settings()