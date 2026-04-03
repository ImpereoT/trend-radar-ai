from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    openai_api_key: str = Field(validation_alias="OPENROUTER_API_KEY")
    openai_api_base: str = Field(validation_alias="OPENAI_API_BASE")
    model_id: str = Field(validation_alias="MODEL_ID")

    # Пути для хранения
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    storage_dir: str = os.path.join(base_dir, "storage")
    reports_dir: str = os.path.join(storage_dir, "reports")
    charts_dir: str = os.path.join(storage_dir, "charts")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Создаем папки при импорте конфига
for d in [settings.reports_dir, settings.charts_dir]:
    os.makedirs(d, exist_ok=True)
