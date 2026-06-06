from jobreach.ai.model_discovery.base import ModelDiscoveryClient


class GeminiModelDiscoveryClient(ModelDiscoveryClient):
    def list_models(self, api_key: str) -> list[str]:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        models: list[str] = []
        for model in genai.list_models():
            name = getattr(model, "name", "") or ""
            if name.startswith("models/"):
                name = name.split("/", 1)[1]
            methods = getattr(model, "supported_generation_methods", []) or []
            if "generateContent" in methods or not methods:
                models.append(name)
        return sorted(set(models))
