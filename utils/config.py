"""Basit JSON tabanli ayar yonetimi."""
import json
from typing import Any

class Config:
    """Uygulama ayarlari."""

    def __init__(self, data: dict | None = None):
        self._data = data or {}

    @classmethod
    def load_from_file(cls, file_path: str) -> "Config":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)

    def save_to_file(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
