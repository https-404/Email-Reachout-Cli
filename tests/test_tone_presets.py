from jobreach.ai.tone_presets import TONE_PRESETS, get_tone_preset, list_tone_preset_ids


def test_tone_presets_registered():
    ids = list_tone_preset_ids()
    assert "default" in ids
    assert "formal_hr" in ids
    assert get_tone_preset("default")["instruction"]
    assert TONE_PRESETS["startup_founder"]["label"]
