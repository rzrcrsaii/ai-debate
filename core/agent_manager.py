"""Ajanlari yoneten sinif."""
import json
from typing import List, Optional
from .models import Agent

class AgentManager:
    """Ajanlarin olusturulmasi ve yonetimi icin merkezi sinif."""

    def __init__(self):
        self.agents: List[Agent] = []

    def load_agents_from_file(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            agent = Agent(**item)
            self.add_agent(agent)

    def create_agent(self, name: str, api_key: str, model: str, system_prompt: str, is_moderator: bool = False) -> Agent:
        agent = Agent(name=name, api_key=api_key, model=model, system_prompt=system_prompt, is_moderator=is_moderator)
        self.add_agent(agent)
        return agent

    def add_agent(self, agent: Agent) -> None:
        self.agents.append(agent)

    def remove_agent(self, name: str) -> None:
        self.agents = [a for a in self.agents if a.name != name]

    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def get_moderator(self) -> Optional[Agent]:
        for agent in self.agents:
            if agent.is_moderator:
                return agent
        return None

    def save_agents_to_file(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([agent.__dict__ for agent in self.agents], f, ensure_ascii=False, indent=2)
