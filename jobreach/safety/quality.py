from jobreach.core.models import CandidateProfile, EmailDraft, Lead


def _word_count(text: str) -> int:
    return len(text.split())


def _has_cta(body: str) -> bool:
    lowered = body.lower()
    phrases = ("would you", "could you", "open to", "available", "forward", "connect", "chat", "call")
    return any(phrase in lowered for phrase in phrases) and "?" in body


def _mentions_relevance(body: str, profile: CandidateProfile) -> bool:
    lowered = body.lower()
    candidates = profile.skills + profile.target_roles + profile.projects
    return any(item and item.lower() in lowered for item in candidates)


def check_email_quality(draft: EmailDraft, profile: CandidateProfile, lead: Lead) -> EmailDraft:
    warnings: list[str] = []
    serious = False
    body_lower = draft.body.lower()

    if not draft.subject.strip():
        warnings.append("missing subject")
        serious = True
    if not draft.body.strip():
        warnings.append("missing body")
        serious = True
    if _word_count(draft.body) > 160:
        warnings.append("body over 160 words")
    if "i saw your job posting" in body_lower and not lead.job_url:
        warnings.append("mentions job posting without job_url")
        serious = True
    if "i noticed" in body_lower and not (lead.website or lead.job_url or lead.notes):
        warnings.append('uses "I noticed" without context')
        serious = True
    if "recent" in body_lower and "recent" not in (lead.notes or "").lower():
        warnings.append("mentions recent context not present in notes")
        serious = True
    if not _has_cta(draft.body):
        warnings.append("missing soft CTA")
    relevance = _mentions_relevance(draft.body, profile)
    if not relevance:
        warnings.append("missing candidate relevance")

    score = 5
    if lead.company:
        score += 1
    if lead.role or lead.job_url:
        score += 1
    if relevance:
        score += 1
    if lead.recipient_name:
        score += 1
    if _has_cta(draft.body):
        score += 1
    if serious:
        score -= 2
    if _word_count(draft.body) > 160:
        score -= 1

    draft.warnings = warnings
    draft.personalization_score = max(1, min(10, score))
    draft.risk = "high" if serious else "medium" if warnings else "low"
    if warnings:
        draft.quality_reason = f"Score {draft.personalization_score}/10 — {', '.join(warnings)}"
    else:
        draft.quality_reason = f"Score {draft.personalization_score}/10 — looks good"
    return draft
