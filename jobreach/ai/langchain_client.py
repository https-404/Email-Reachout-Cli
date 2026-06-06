import json
import re
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from jobreach.ai.base import AIClient
from jobreach.core.errors import AIProviderError

T = TypeVar("T", bound=BaseModel)


def _build_chat_model(provider: str, model: str, temperature: float):
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model, temperature=temperature)
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, temperature=temperature)
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model, temperature=temperature)
    raise AIProviderError(f"Unsupported provider: {provider}")


class LangChainAIClient(AIClient):
    def __init__(self, provider: str, model: str, temperature: float = 0.4):
        self.provider = provider
        self.model_name = model
        self.model = _build_chat_model(provider, model, temperature)

    def generate_text(self, prompt: str) -> str:
        result = self.model.invoke(prompt)
        return getattr(result, "content", str(result))

    def generate_structured(self, prompt: str, schema: Type[T]) -> T:
        structured_llm = self.model.with_structured_output(schema)
        try:
            return structured_llm.invoke(prompt)
        except Exception:
            try:
                return structured_llm.invoke(prompt)
            except Exception as exc:
                return self._fallback_json(prompt, schema, exc)

    def _fallback_json(self, prompt: str, schema: Type[T], original_error: Exception) -> T:
        json_prompt = (
            f"{prompt}\n\nReturn only valid JSON matching this JSON schema:\n"
            f"{json.dumps(schema.model_json_schema(), indent=2)}"
        )
        raw = self.generate_text(json_prompt)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise AIProviderError(f"Structured output failed: {original_error}") from original_error
        try:
            return schema.model_validate_json(match.group(0))
        except (ValidationError, ValueError) as exc:
            raise AIProviderError(f"Could not validate structured AI response: {exc}") from exc
