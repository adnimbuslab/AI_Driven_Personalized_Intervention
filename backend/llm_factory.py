"""Shared LLM client factory. All agents use this single entry point.

Change LLM_MODEL_ID and LLM_PROVIDER env vars to swap models — zero code changes.
"""

from backend.config import Config

_client = None


def get_llm_client():
    global _client
    if _client is not None:
        return _client

    provider = Config.LLM_PROVIDER
    if provider == "anthropic":
        import anthropic
        api_key = Config.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        _client = anthropic.Anthropic(api_key=api_key)
        return _client

    raise ValueError(f"Unsupported LLM provider: {provider}")


def get_model_id() -> str:
    return Config.LLM_MODEL_ID


def reset_client():
    """Reset the cached client (useful for testing)."""
    global _client
    _client = None
