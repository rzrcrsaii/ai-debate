import sys
import os

# Provide a stub for the requests module since the environment may not have it
import types
requests_stub = types.SimpleNamespace(post=lambda *a, **k: None)
sys.modules.setdefault('requests', requests_stub)

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.models import Agent
from core.debate_manager import DebateManager
from core.api_client import APIClient

class DummyAPIClient(APIClient):
    def format_messages(self, system_prompt, prompt, conversation_history):
        return {}

    def async_request(self, agent, prompt, conversation_history):
        return {"choices": [{"message": {"content": f"reply to {prompt}"}}], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}


def test_debate_flow():
    client = DummyAPIClient(api_key="test")
    manager = DebateManager(client)
    agents = [
        Agent(name="A", api_key="key1", model="gpt", system_prompt=""),
        Agent(name="B", api_key="key2", model="gpt", system_prompt=""),
        Agent(name="M", api_key="key3", model="gpt", system_prompt="", is_moderator=True),
    ]
    manager.start_debate("topic", agents)
    msg = manager.agent_turn(agents[0], "hello")
    assert "reply to hello" in msg.content
    manager.end_turn()

