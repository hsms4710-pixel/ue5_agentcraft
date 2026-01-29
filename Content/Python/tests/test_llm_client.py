import sys
import types
import os

# Ensure Content/Python is on sys.path for tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent_core.llm import DeepseekClient


def test_deepseek_client_with_openai_sdk(monkeypatch):
    # Create a fake openai module with OpenAI class
    module = types.ModuleType("openai")

    class FakeOpenAI:
        def __init__(self, api_key=None, base_url=None):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda **kwargs: types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="sdk response"))])
                )
            )

    module.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", module)

    client = DeepseekClient(api_key="fake", base_url="https://api.deepseek.com", model="deepseek-chat")
    r = client.generate("sys", "user")
    assert "sdk response" in r


def test_deepseek_client_requests_fallback(monkeypatch):
    # Remove openai if present
    if "openai" in sys.modules:
        del sys.modules["openai"]

    class FakeResponse:
        def __init__(self):
            pass

        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "http response"}}]}

        @property
        def text(self):
            return "http raw"

    def fake_post(url, headers=None, json=None, timeout=None):
        return FakeResponse()

    fake_requests = types.ModuleType("requests")
    fake_requests.post = fake_post
    monkeypatch.setitem(sys.modules, "requests", fake_requests)

    client = DeepseekClient(api_key="fake", base_url="https://api.deepseek.com", model="deepseek-chat")
    r = client.generate("sys", "user")
    assert "http response" in r
