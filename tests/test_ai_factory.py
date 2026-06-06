import pytest

from jobreach.ai.factory import AIClientFactory
from jobreach.core.errors import AIProviderError


def test_ai_factory_rejects_unknown_provider():
    with pytest.raises(AIProviderError):
        AIClientFactory.create("bad", "model")
