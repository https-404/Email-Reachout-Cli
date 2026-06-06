from abc import ABC, abstractmethod


class ModelDiscoveryClient(ABC):
    @abstractmethod
    def list_models(self, api_key: str) -> list[str]:
        pass
