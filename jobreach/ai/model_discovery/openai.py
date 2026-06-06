from jobreach.ai.model_discovery.base import ModelDiscoveryClient


CHAT_PREFIXES = ("gpt-", "o1", "o3", "o4", "chatgpt")


class OpenAIModelDiscoveryClient(ModelDiscoveryClient):
    def list_models(self, api_key: str) -> list[str]:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.models.list()
        model_ids = [model.id for model in response.data]
        chat_models = [
            model_id
            for model_id in model_ids
            if any(model_id.startswith(prefix) for prefix in CHAT_PREFIXES)
        ]
        return sorted(set(chat_models or model_ids))
