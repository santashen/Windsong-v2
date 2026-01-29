from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMService(ABC):
    """LLM service base class for future extensibility."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass


class OpenAICompatibleService(BaseLLMService):
    """OpenAI-compatible API implementation (works with vveai.com proxy)."""

    def __init__(self, api_url: str, api_key: str, model: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        import httpx

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "stream": False,
                },
                timeout=180.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def get_model_name(self) -> str:
        return self.model
