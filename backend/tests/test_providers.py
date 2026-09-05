from app.providers.factory import get_llm_provider


def test_ollama_provider():
    provider = get_llm_provider("ollama")

    assert provider is not None
    assert provider.model == "llama3.2:3b"


def test_invalid_provider():
    try:
        get_llm_provider("invalid-provider")
        assert False
    except RuntimeError as exc:
        assert "Unsupported LLM provider" in str(exc)