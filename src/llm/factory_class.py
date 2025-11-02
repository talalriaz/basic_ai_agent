# src/llm/factory.py
from typing import Dict, Any
from src.llm.base import LLMClient
from src.llm.openai_class import OpenAIClient
import os, dotenv
dotenv.load_dotenv()

PROVIDERS: Dict[str, type] = {
    "openai": OpenAIClient,
}

def create_llm(config: Dict[str, Any]) -> LLMClient:
    """
    Factory function to create an LLM client based on the provider specified in the config.
    """
    provider = config.get("provider").lower()
    client_cls = PROVIDERS.get(provider)
    if not client_cls:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    if provider == "openai" and "api_key" not in config:
        config["api_key"] = os.getenv("OPENAI_API_KEY")
    return client_cls(**config)