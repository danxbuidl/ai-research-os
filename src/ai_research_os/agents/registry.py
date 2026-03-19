from __future__ import annotations

from typing import Type

from ai_research_os.agents.base import BaseAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Type[BaseAgent]] = {}

    def register(self, agent_cls: Type[BaseAgent]) -> None:
        self._agents[agent_cls.agent_name] = agent_cls

    def get(self, name: str) -> Type[BaseAgent]:
        return self._agents[name]
