"""OpenRouter API ile iletisim icin temel siniflar."""
import requests
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class APIClient(ABC):
    """Soyut API istemcisi."""

    BASE_URL: str = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def format_messages(self, system_prompt: str, prompt: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """API icin mesajlari formatlar."""

    def async_request(self, agent, prompt: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Senkrondan cok basit bir islem. Gercek uygulamada asenkron olacak."""
        payload = self.format_messages(agent.system_prompt, prompt, conversation_history)
        headers = {"Authorization": f"Bearer {agent.api_key}"}
        response = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def parse_response(self, response: Dict[str, Any]) -> str:
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")

    def extract_token_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        return response.get("usage", {"prompt_tokens": 0, "completion_tokens": 0})

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        # Basit bir maliyet hesabi (gercek uygulamada daha detayli olacaktir)
        return (prompt_tokens + completion_tokens) * 0.00001

class APIThread:
    """Yalnizca yer tutucu; gercek uygulamada QThread kullanilacak."""

    def __init__(self, client: APIClient, agent, prompt: str, history: List[Dict[str, str]]):
        self.client = client
        self.agent = agent
        self.prompt = prompt
        self.history = history
        self.response: Optional[str] = None
        self.raw_response: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

    def run(self) -> None:
        try:
            res = self.client.async_request(self.agent, self.prompt, self.history)
            self.raw_response = res
            self.response = self.client.parse_response(res)
        except Exception as exc:  # pylint: disable=broad-except
            self.error = str(exc)
