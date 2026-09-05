from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a complete response."""
        raise NotImplementedError

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Stream a response token by token."""
        raise NotImplementedError