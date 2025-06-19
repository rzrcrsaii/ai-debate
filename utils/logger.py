"""Basit loglama."""
import logging

class Logger:
    """Uygulama loglama sinifi."""

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ai-debate")

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)

    def log_module_transition(self, from_module: str, to_module: str) -> None:
        self.info(f"Modul gecisi: {from_module} -> {to_module}")

    def log_api_call(self, agent, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        self.info(
            f"API cagri: agent={agent.name} model={model} prompt={prompt_tokens} completion={completion_tokens}"
        )
