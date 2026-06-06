from jobreach.ai.base import AIClient
from jobreach.ai.langchain_client import LangChainAIClient
from jobreach.core.constants import SUPPORTED_AI_PROVIDERS
from jobreach.core.errors import AIProviderError


class AIClientFactory:
    @staticmethod
    def create(provider: str, model: str, temperature: float = 0.4) -> AIClient:
        if provider not in SUPPORTED_AI_PROVIDERS:
            raise AIProviderError(f"Unsupported provider: {provider}")
        return LangChainAIClient(provider=provider, model=model, temperature=temperature)
