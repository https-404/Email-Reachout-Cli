from abc import ABC, abstractmethod
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AIClient(ABC):
    provider: str | None = None
    model_name: str | None = None

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema: Type[T]) -> T:
        pass
