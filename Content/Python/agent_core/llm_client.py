"""Adapter module for LLM client.

Keeps the API stable under the name `llm_client`.
"""
from agent_core.llm import DeepseekClient

# Expose a simple factory
def make_client(api_key=None, base_url=None, model=None, timeout=15):
    return DeepseekClient(api_key=api_key, base_url=base_url, model=model, timeout=timeout)
