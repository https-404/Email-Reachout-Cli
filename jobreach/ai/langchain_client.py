import json
import os
import re
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from jobreach.ai.base import AIClient
from jobreach.core.errors import AIProviderError

T = TypeVar("T", bound=BaseModel)


def _build_chat_model(provider: str, model: str, api_key: str, temperature: float):
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=temperature)
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model, api_key=api_key, temperature=temperature)
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model, api_key=api_key, temperature=temperature)
    if provider == "openrouter":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
            base_url="https://openrouter.ai/api/v1",
        )
    if provider == "groq":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
            base_url="https://api.groq.com/openai/v1",
        )
    if provider == "deepseek":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
            base_url="https://api.deepseek.com/v1",
        )
    if provider == "ollama":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            api_key=api_key or "ollama",
            temperature=temperature,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        )
    raise AIProviderError(f"Unsupported provider: {provider}")


class LangChainAIClient(AIClient):
    def __init__(self, provider: str, model: str, api_key: str, temperature: float = 0.4):
        self.provider = provider
        self.model_name = model
        self.model = _build_chat_model(provider, model, api_key, temperature)

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
