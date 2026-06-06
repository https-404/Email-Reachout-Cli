from jobreach.utils.text import compact_whitespace


def normalize_cv_text(text: str) -> str:
    return compact_whitespace(text)
