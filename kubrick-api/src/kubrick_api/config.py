from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config= SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")
    GROQ_API_KEY: str
    GROQ_ROUTING_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"  # still works

    # Tool use → GPT-OSS 120B has strong tool/function calling
    GROQ_TOOL_USE_MODEL: str = "openai/gpt-oss-120b"

    # Image/multimodal → Scout supports vision (up to 5 images)
    GROQ_IMAGE_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # General → GPT-OSS 120B or Llama 3.3 70B for production stability
    GROQ_GENERAL_MODEL: str = "openai/gpt-oss-120b"

    # --- Comet ML & Opik Configuration ---
    OPIK_API_KEY: str | None = Field(default=None, description="API key for Comet ML and Opik services.")
    OPIK_WORKSPACE: str = "default"
    OPIK_PROJECT: str = Field(
        default="kubrick-api",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- Memory Configuration ---
    AGENT_MEMORY_SIZE: int = 20

    # --- MCP Configuration ---
    MCP_SERVER: str = "http://kubrick-mcp:9090/mcp"

    # --- Disable Nest Asyncio ---
    DISABLE_NEST_ASYNCIO: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get the application settings
    """
    return Settings()