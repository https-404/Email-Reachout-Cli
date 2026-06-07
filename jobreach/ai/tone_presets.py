TONE_PRESETS = {
    "default": {
        "label": "Default",
        "preferred_tone": "confident, concise, friendly",
        "instruction": "Use a confident, concise, and friendly tone suitable for job outreach.",
    },
    "formal_hr": {
        "label": "Formal HR",
        "preferred_tone": "professional, respectful, formal",
        "instruction": "Use a professional and formal tone appropriate for HR or recruiting inboxes.",
    },
    "startup_founder": {
        "label": "Startup founder",
        "preferred_tone": "direct, energetic, builder-minded",
        "instruction": "Use a direct, energetic tone suited for founders or early-stage startup leaders.",
    },
    "agency_recruiter": {
        "label": "Agency recruiter",
        "preferred_tone": "warm, polished, relationship-oriented",
        "instruction": "Use a warm, polished tone suited for agency recruiters and talent partners.",
    },
}


def get_tone_preset(preset_id: str) -> dict:
    return TONE_PRESETS.get(preset_id, TONE_PRESETS["default"])


def list_tone_preset_ids() -> list[str]:
    return list(TONE_PRESETS.keys())
