"""LLM MCP Server — Unified LLM interface for all agents.

Starts as a stub returning mock data. Phase 2 replaces with real Anthropic API calls.
"""

import json
import hashlib
import time
from typing import Optional

from backend.config import Config


class LlmMCP:

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from backend.llm_factory import get_llm_client
                self._client = get_llm_client()
            except (ImportError, ValueError):
                self._client = None
        return self._client

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> dict:
        client = self._get_client()
        if client is None:
            return self._mock_generate(system_prompt, user_prompt)

        for attempt in range(3):
            try:
                response = client.messages.create(
                    model=Config.LLM_MODEL_ID,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return {
                    "content": response.content[0].text,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                    },
                }
            except Exception as e:
                if attempt == 2:
                    return {"error": str(e), "content": ""}
                time.sleep(2 ** attempt)

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: dict,
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> dict:
        client = self._get_client()
        if client is None:
            return self._mock_structured(output_schema)

        schema_instruction = (
            f"\n\nYou MUST respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(output_schema, indent=2)}\n```\n"
            f"Respond ONLY with the JSON object, no other text."
        )

        for attempt in range(3):
            try:
                response = client.messages.create(
                    model=Config.LLM_MODEL_ID,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt + schema_instruction,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                text = response.content[0].text.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                return json.loads(text)
            except json.JSONDecodeError:
                if attempt == 2:
                    return {"error": "Failed to parse LLM response as JSON", "raw": text}
                continue
            except Exception as e:
                if attempt == 2:
                    return {"error": str(e)}
                time.sleep(2 ** attempt)

    def analyze_document(
        self,
        document_content: str,
        extraction_schema: dict,
    ) -> dict:
        system_prompt = (
            "You are a clinical document extraction specialist. "
            "Extract structured data from the provided clinical document. "
            "Be precise and only extract information that is explicitly stated. "
            "If a field cannot be determined from the document, set it to null."
        )
        return self.generate_structured(
            system_prompt=system_prompt,
            user_prompt=f"Extract data from this clinical document:\n\n{document_content}",
            output_schema=extraction_schema,
        )

    # --- Mock implementations for development without API key ---

    def _mock_generate(self, system_prompt: str, user_prompt: str) -> dict:
        mock_hash = hashlib.md5(f"{system_prompt}{user_prompt}".encode()).hexdigest()[:8]
        return {
            "content": f"[Mock LLM response {mock_hash}] Based on the provided information, here is the analysis.",
            "usage": {"input_tokens": 100, "output_tokens": 50},
            "mock": True,
        }

    def _mock_structured(self, schema: dict) -> dict:
        return self._generate_mock_from_schema(schema)

    def _generate_mock_from_schema(self, schema: dict) -> dict:
        if schema.get("type") == "object":
            result = {}
            for key, prop in schema.get("properties", {}).items():
                result[key] = self._generate_mock_value(key, prop)
            return result
        return {}

    def _generate_mock_value(self, key: str, prop: dict):
        ptype = prop.get("type", "string")
        if ptype == "string":
            if "enum" in prop:
                return prop["enum"][0]
            return f"mock_{key}"
        if ptype == "number":
            return 0.85
        if ptype == "integer":
            return 1
        if ptype == "boolean":
            return True
        if ptype == "array":
            items = prop.get("items", {"type": "string"})
            return [self._generate_mock_value(f"{key}_item", items)]
        if ptype == "object":
            return self._generate_mock_from_schema(prop)
        return None
