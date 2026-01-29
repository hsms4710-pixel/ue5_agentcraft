"""LLM client adapters for the agent (DeepSeek-compatible).

This client prefers using the OpenAI-compatible Python SDK (`from openai import OpenAI`) if
it is installed and available, because DeepSeek exposes an OpenAI-compatible interface.
If the SDK is not available, a requests-based fallback is used.

Environment variables supported:
- DEEPSEEK_API_KEY: API key (required)
- DEEPSEEK_API_URL or DEEPSEEK_BASE_URL: Base URL for DeepSeek (e.g. https://api.deepseek.com)
- DEEPSEEK_MODEL: Model name (default: deepseek-chat)

Note: do NOT commit API keys in source control. Set them in your environment or a secure
secrets store. Example (PowerShell):
    $env:DEEPSEEK_API_KEY = "sk-..."
    $env:DEEPSEEK_API_URL = "https://api.deepseek.com"
"""

import os
import json
from typing import Optional

# Prefer OpenAI SDK if present (DeepSeek is OpenAI-compatible)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Fallback HTTP client
try:
    import requests
except Exception:
    requests = None


DEFAULT_BASE_URL = os.environ.get("DEEPSEEK_API_URL") or os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"
DEFAULT_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")


class DeepseekClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None, timeout: int = 15):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set in environment")

        self.base_url = (base_url or os.environ.get("DEEPSEEK_API_URL") or os.environ.get("DEEPSEEK_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.environ.get("DEEPSEEK_MODEL") or DEFAULT_MODEL
        self.timeout = timeout

        # Initialize preferred client (OpenAI SDK) if available
        if OpenAI is not None:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
            if requests is None:
                raise RuntimeError("Either `openai` SDK or `requests` library is required but not available in the environment")

    def generate(self, system_prompt: str, user_input: str, max_tokens: int = 1024, temperature: float = 0.2, stream: bool = False) -> str:
        """Send prompt to DeepSeek and return the text response.

        Uses OpenAI SDK when available to call the Chat Completions API in a compatible format:

            client.chat.completions.create(model=..., messages=[...])

        If the SDK is unavailable, uses a direct HTTP POST to `{base_url}/v1/chat/completions`.
        """
        # Build messages in OpenAI chat format
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        if self.client is not None:
            # Use OpenAI-compatible SDK
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
            )
            # Response shape: resp.choices[0].message.content
            try:
                choice = resp.choices[0]
                # New SDK may return message object
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    return choice.message.content
                # Fallback shapes
                if 'text' in choice:
                    return choice['text']
            except Exception:
                # Fallback to stringified resp
                return str(resp)

        # Fallback: direct HTTP call
        endpoint = self.base_url
        # Ensure URL includes /v1 prefix for chat completions
        if not endpoint.endswith('/v1'):
            endpoint = endpoint + '/v1'
        url = endpoint + '/chat/completions'

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        # Extract content from standard OpenAI-compatible response
        if isinstance(data, dict) and "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            first = data["choices"][0]
            # choices[0].message.content
            if isinstance(first, dict):
                msg = first.get("message") or first.get("delta") or {}
                if isinstance(msg, dict) and "content" in msg:
                    return msg["content"].strip()
                # legacy 'text'
                if "text" in first and isinstance(first["text"], str):
                    return first["text"].strip()

        # Last resort: return raw text
        return resp.text
