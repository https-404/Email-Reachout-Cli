import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from jobreach.config.paths import enrichment_cache_dir
from jobreach.core.models import Lead
from jobreach.utils.files import ensure_parent


def _fetch_title(url: str, timeout: int = 5) -> str | None:
    try:
        request = Request(url, headers={"User-Agent": "JobReach/1.0"})
        with urlopen(request, timeout=timeout) as response:
            html = response.read(8000).decode("utf-8", errors="ignore")
        start = html.lower().find("<title")
        if start == -1:
            return None
        start = html.find(">", start) + 1
        end = html.lower().find("</title>", start)
        if end == -1:
            return None
        return html[start:end].strip()
    except (URLError, TimeoutError, ValueError):
        return None


def enrich_leads(leads: list[Lead]) -> list[Lead]:
    enriched: list[Lead] = []
    cache_dir = enrichment_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    for lead in leads:
        if not lead.website:
            enriched.append(lead)
            continue
        domain = lead.website.replace("https://", "").replace("http://", "").split("/")[0]
        cache_path = cache_dir / f"{domain}.json"
        title = None
        if cache_path.exists():
            title = json.loads(cache_path.read_text(encoding="utf-8")).get("title")
        else:
            url = lead.website if lead.website.startswith("http") else f"https://{lead.website}"
            title = _fetch_title(url)
            ensure_parent(cache_path)
            cache_path.write_text(json.dumps({"title": title}), encoding="utf-8")
        notes = lead.notes or ""
        if title and title not in notes:
            notes = f"{notes} Company site title: {title}".strip()
        enriched.append(lead.model_copy(update={"notes": notes or lead.notes}))
    return enriched
