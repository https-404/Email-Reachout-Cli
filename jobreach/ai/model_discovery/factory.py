from jobreach.ai.model_discovery.anthropic import AnthropicModelDiscoveryClient
from jobreach.ai.model_discovery.base import ModelDiscoveryClient
from jobreach.ai.model_discovery.gemini import GeminiModelDiscoveryClient
from jobreach.ai.model_discovery.openai import OpenAIModelDiscoveryClient
from jobreach.core.errors import AIProviderError


class ModelDiscoveryFactory:
    @staticmethod
    def create(provider: str) -> ModelDiscoveryClient:
        clients = {
            "openai": OpenAIModelDiscoveryClient,
            "gemini": GeminiModelDiscoveryClient,
            "anthropic": AnthropicModelDiscoveryClient,
        }
        if provider not in clients:
            raise AIProviderError(f"Unsupported provider: {provider}")
        return clients[provider]()
