import json
import os
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict

class BaseTool(ABC):
    """Standard base class for all skills/tools.

    Subclasses should set `name` and `description` and implement `run`.
    """
    name: str = ""
    description: str = ""

    def __init__(self, config_path: Optional[str] = None):
        self.config: Dict[str, Any] = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

    @abstractmethod
    def run(self, **kwargs):
        """Execute the tool with keyword arguments."""
        raise NotImplementedError()

    @classmethod
    def load_definition(cls, def_path: str):
        """Load a JSON Schema definition for the tool (if present)."""
        if def_path and os.path.exists(def_path):
            with open(def_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        return None
