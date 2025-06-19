"""Temel veri yapilari."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class Agent:
    """Münazarada yer alan ajani temsil eder."""

    name: str
    api_key: str
    model: str
    system_prompt: str
    is_moderator: bool = False
    token_usage: Dict[str, int] = field(default_factory=lambda: {"prompt": 0, "completion": 0})
    cost: float = 0.0

@dataclass
class Message:
    """Münazara sirasinda gonderilen mesaj."""

    agent: Agent
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0

@dataclass
class Turn:
    """Münazarada bir turu temsil eder."""

    turn_number: int
    messages: List[Message] = field(default_factory=list)
    summary: Optional[Message] = None
    is_last_turn: bool = False
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0

@dataclass
class Debate:
    """Bir münazara oturumunu temsil eder."""

    topic: str
    agents: List[Agent]
    moderator: Agent
    turns: List[Turn] = field(default_factory=list)
    current_turn: Optional[Turn] = None
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost: float = 0.0
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
