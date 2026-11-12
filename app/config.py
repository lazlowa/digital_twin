from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-haiku-5.5"
    email_smtp_server: str = "smtp.gmail.com"
    email_address: str = ""
    email_app_password: str = ""
    notify_to: str = ""


settings = Settings()
