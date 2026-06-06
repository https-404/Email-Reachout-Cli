from jobreach.ai.model_discovery.base import ModelDiscoveryClient
from jobreach.ai.provider_registry import get_provider


class AnthropicModelDiscoveryClient(ModelDiscoveryClient):
    def list_models(self, api_key: str) -> list[str]:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            if hasattr(client, "models") and hasattr(client.models, "list"):
                response = client.models.list()
                data = getattr(response, "data", response)
                models = [getattr(item, "id", str(item)) for item in data]
                if models:
                    return sorted(set(models))
        except Exception:
            pass
        return list(get_provider("anthropic").recommended_models)
