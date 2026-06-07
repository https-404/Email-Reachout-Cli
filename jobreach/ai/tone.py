from jobreach.ai.tone_presets import get_tone_preset


def apply_tone_to_profile(profile, tone_preset: str):
    preset = get_tone_preset(tone_preset)
    updated = profile.model_copy(update={"preferred_tone": preset["preferred_tone"]})
    return updated, preset["instruction"]
