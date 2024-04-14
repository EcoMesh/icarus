from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rethinkdb_host: str = "localhost"
    rethinkdb_port: int = 28015
    rethinkdb_database: str = "test"

    model_config = {"env_file": ".env"}


settings = Settings()
