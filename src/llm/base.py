from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Generator, Any
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

Message = Dict[str, str]

class LLMClient(ABC):

    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> str:
        """Invoke the LLM with a list of messages and return the response as a string."""
        pass

    @abstractmethod
    def bind_tools(self, tools: List[Any]):
        """Bind tools to the LLM client and return a new instance."""
        pass