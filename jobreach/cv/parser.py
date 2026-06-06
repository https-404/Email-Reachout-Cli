from pathlib import Path

from jobreach.core.errors import CVParseError
from jobreach.cv.normalizer import normalize_cv_text


def parse_cv(path: str) -> str:
    source = Path(path)
    if not source.exists():
        raise CVParseError(f"CV file not found: {path}")

    suffix = source.suffix.lower()
    try:
        if suffix == ".txt":
            text = source.read_text(encoding="utf-8")
        elif suffix == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(str(source))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif suffix == ".docx":
            from docx import Document

            document = Document(str(source))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        else:
            raise CVParseError("Unsupported CV format. Use .txt, .pdf, or .docx")
    except CVParseError:
        raise
    except Exception as exc:
        raise CVParseError(f"Could not parse CV: {exc}") from exc

    normalized = normalize_cv_text(text)
    if not normalized:
        raise CVParseError("CV text is empty after parsing")
    return normalized
