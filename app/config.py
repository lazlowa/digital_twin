from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = ""
    openrouter_model: str = ""
    gmail_address: str = ""
    gmail_app_password: str = ""
    notify_to: str = ""


settings = Settings()
