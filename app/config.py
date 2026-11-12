from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-haiku-5.5"
    email_smtp_server: str = "smtp.gmail.com"
    email_address: str = ""
    email_app_password: str = ""
    notify_to: str = ""

    max_message_chars: int = 2000
    max_history_messages: int = 40
    max_response_tokens: int = 1000
    rate_limit_per_minute: int = 10
    rate_limit_per_day: int = 100
    # Only behind a proxy that sets X-Real-IP / X-Forwarded-For itself (Vercel).
    trust_proxy_headers: bool = False
    # Set by Vercel: production, preview or development.
    vercel_env: str = ""


settings = Settings()
