"""Shared LLM client factory. All agents use this single entry point.

Change LLM_MODEL_ID and LLM_PROVIDER env vars to swap models — zero code changes.
"""

import requests as _requests
from backend.config import Config

_client = None


class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def generate(self, model, prompt, system="", temperature=0.3, max_tokens=4096):
        resp = _requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
            timeout=180,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "content": data.get("response", ""),
            "usage": {
                "input_tokens": data.get("prompt_eval_count", 0),
                "output_tokens": data.get("eval_count", 0),
            },
        }


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

    if provider == "ollama":
        _client = OllamaClient(base_url=Config.OLLAMA_BASE_URL)
        return _client

    raise ValueError(f"Unsupported LLM provider: {provider}")


def get_model_id() -> str:
    return Config.LLM_MODEL_ID


def reset_client():
    """Reset the cached client (useful for testing)."""
    global _client
    _client = None
