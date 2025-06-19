"""Münazara akisinin temel yonetimi."""
from typing import List
from .models import Debate, Turn, Message, Agent
from .api_client import APIClient, APIThread

class DebateManager:
    """Münazara akisini yoneten sinif."""

    def __init__(self, client: APIClient):
        self.client = client
        self.debate: Debate | None = None
        self.history: List[dict] = []

    def start_debate(self, topic: str, agents: List[Agent]) -> None:
        moderator = next((a for a in agents if a.is_moderator), agents[0])
        self.debate = Debate(topic=topic, agents=agents, moderator=moderator)
        self.debate.current_turn = Turn(turn_number=1)

    def agent_turn(self, agent: Agent, prompt: str) -> Message:
        thread = APIThread(self.client, agent, prompt, self.history)
        thread.run()
        content = thread.response or thread.error or ""
        message = Message(agent=agent, content=content)
        if thread.raw_response:
            usage = self.client.extract_token_usage(thread.raw_response)
            message.prompt_tokens = usage.get("prompt_tokens", 0)
            message.completion_tokens = usage.get("completion_tokens", 0)
            message.cost = self.client.calculate_cost(
                agent.model,
                message.prompt_tokens,
                message.completion_tokens,
            )
        self.debate.current_turn.messages.append(message)
        self.history.append({"role": agent.name, "content": content})
        return message

    def end_turn(self) -> None:
        if not self.debate:
            return
        self.debate.turns.append(self.debate.current_turn)
        self.debate.current_turn = Turn(turn_number=len(self.debate.turns) + 1)
