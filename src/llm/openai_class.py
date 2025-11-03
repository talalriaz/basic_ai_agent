from src.llm.base import LLMClient, Message
from typing import List, Generator, Any
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

class OpenAIClient(LLMClient):
    def __init__(self, model: str, temperature: float = 0.7, **extra):
        self.client = ChatOpenAI(model=model,temperature=temperature)
        self.model = model
        self.temperature = temperature

    def chat(self, client,messages: List[Message], **kwargs) -> str:
        response = client.invoke(
            input=messages,
            **kwargs,
        )
        return response
    
    def bind_tools(self, client, tools: List[Any]):
        client_tools = client.bind_tools(tools)
        return client_tools
