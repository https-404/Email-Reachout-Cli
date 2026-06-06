from typing import Type, TypeVar

from pydantic import BaseModel

from jobreach.ai.base import AIClient

T = TypeVar("T", bound=BaseModel)


class FallbackAIClient(AIClient):
    def __init__(self, clients: list[AIClient]):
        self.clients = clients

    def generate_text(self, prompt: str) -> str:
        last_error: Exception | None = None
        for client in self.clients:
            try:
                return client.generate_text(prompt)
            except Exception as exc:
                last_error = exc
        raise last_error or RuntimeError("No fallback AI clients configured")

    def generate_structured(self, prompt: str, schema: Type[T]) -> T:
        last_error: Exception | None = None
        for client in self.clients:
            try:
                return client.generate_structured(prompt, schema)
            except Exception as exc:
                last_error = exc
        raise last_error or RuntimeError("No fallback AI clients configured")
