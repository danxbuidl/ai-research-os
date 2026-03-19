from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    agent_name = "base_agent"

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        raise NotImplementedError
