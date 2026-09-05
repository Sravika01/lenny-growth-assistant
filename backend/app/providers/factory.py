from app.config import settings
from app.providers.base import LLMProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import CloudProvider


def get_llm_provider(
    provider_name: str | None = None,
) -> LLMProvider:

    provider = (
        provider_name
        or settings.default_llm_provider
    ).lower()

    if provider == "ollama":
        return OllamaProvider()

    if provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        return CloudProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    raise RuntimeError(
        f"Unsupported LLM provider: {provider}"
    )