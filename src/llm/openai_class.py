from src.llm.base import LLMClient, Message
from typing import List, Generator, Any
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

class OpenAIClient(LLMClient):
    def __init__(self, model: str, temperature: float = 0.7, **extra):
        self.client = ChatOpenAI(model=model,temperature=temperature)
        self.model = model
        self.temperature = temperature

    def chat(self, messages: List[Message], **kwargs) -> str:
        response = self.client.invoke(
            input=messages,
            **kwargs,
        )
        return response
    
    def bind_tools(self, tools: List[Any]):
        self.client = self.client.bind_tools(tools)
