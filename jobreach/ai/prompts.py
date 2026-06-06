PROFILE_EXTRACTION_PROMPT = """
You are extracting a structured candidate profile from a CV.

Return only the requested structured data.

CV TEXT:
{{ cv_text }}
"""

EMAIL_GENERATION_PROMPT = """
Write a short cold job outreach email.

Use only the provided candidate profile and lead data.

Rules:
- Do not invent company facts.
- Do not claim there is a job opening unless job_url or role is provided.
- Do not say "I noticed" unless website, notes, or job_url provides real context.
- Do not mention fake company news, funding, posts, products, or hiring plans.
- Keep the body under 140 words.
- Use a confident, polite, non-desperate tone.
- End with a soft call to action.
- Return structured output with subject and body.

Candidate profile:
{{ profile_json }}

Lead:
{{ lead_json }}

Recipient type:
{{ recipient_type }}

Recipient instruction:
{{ recipient_instruction }}
"""

QUALITY_EVALUATION_PROMPT = """
Evaluate this cold job outreach email.

Return:
- personalization_score from 1 to 10
- risk as low, medium, or high
- warnings
- reason

Check for:
- invented company facts
- too much length
- weak CTA
- missing candidate relevance
- claims about job openings without job_url or role
- suspicious language

Candidate profile:
{{ profile_json }}

Lead:
{{ lead_json }}

Draft:
{{ draft_json }}
"""
