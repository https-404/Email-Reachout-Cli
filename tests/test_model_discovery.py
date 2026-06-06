from jobreach.ai.model_discovery.anthropic import AnthropicModelDiscoveryClient


def test_anthropic_model_discovery_fallback():
    client = AnthropicModelDiscoveryClient()
    models = client.list_models("invalid-key-should-fallback")
    assert "claude-3-5-haiku-latest" in models
