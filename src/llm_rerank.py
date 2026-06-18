"""
llm_rerank.py
--------------
OPTIONAL "intelligent re-ranking" layer.

The four signal scores in ranker.py are explainable and fast, but a final
LLM pass over the TOP-N rule-based candidates for each job can catch nuance
that pure scoring misses -- e.g. recognizing that "built 3 ML side projects
using transformers" substantively satisfies a "2+ years deep learning
experience" requirement even for a candidate with only 1 year of formal
experience, or writing a sharper, recruiter-ready justification.

This module is fully OPTIONAL and OFF by default (see config.yaml ->
llm_rerank.enabled). If `ANTHROPIC_API_KEY` is not set in the environment,
or the `anthropic` package isn't installed, or the API call fails for any
reason, the pipeline automatically falls back to the rule-based ranking and
justifications already produced by ranker.py -- the run never breaks
because of this optional step.

Design note: this is the natural place to plug in the "structured
extraction via LLM" approach from the Zero-Shot Resume-Job Matching
research (Chain-of-Thought prompting to segment resumes/JDs before
matching) if you want to go further -- e.g. call this same client from
job_understanding.py to replace the rule-based JD parser.

ANTI-HALLUCINATION GUARDRAIL: every LLM-written justification is re-scanned
with the same taxonomy-based skill extractor used elsewhere in this codebase
(see data_validation.validate_llm_justification). If the LLM asserts a skill
that wasn't in the JD's required/preferred list OR the candidate's own
detected skills -- i.e. a skill it wasn't actually shown -- that candidate's
LLM justification is rejected and the rule-based one is kept instead.
"""

import json
import os


def llm_available() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except ImportError:
        return False


def rerank_top_candidates(job_title: str, job_description: str, shortlist_rows: list,
                           model: str, taxonomy: dict, jd_skill_names: set) -> dict:
    """`shortlist_rows` is a list of dicts (already-scored top candidates for
    one job, as produced by ranker.py, including the `candidate_detected_skills`
    column). `jd_skill_names` is the set of canonical skill names (required +
    preferred) for this job.

    Returns {candidate_id: refined_justification} only for candidates whose
    LLM-written justification PASSES the grounding check (see
    data_validation.validate_llm_justification) -- i.e. it doesn't assert any
    skill the LLM wasn't actually told about for that candidate/job. Any
    candidate whose LLM output fails this check, or if the whole call fails
    for any reason, is simply omitted from the returned dict -- the caller
    (pipeline.py) keeps the rule-based justification for those candidates.
    """
    if not llm_available():
        return {}

    try:
        import anthropic
        client = anthropic.Anthropic()

        candidate_summaries = [
            {
                "candidate_id": row["candidate_id"],
                "current_title": row["current_title"],
                "years_experience": row["years_experience"],
                "detected_skills": row.get("candidate_detected_skills", ""),
                "matched_required_skills": row["matched_required_skills"],
                "missing_required_skills": row["missing_required_skills"],
                "rule_based_score": row["final_score"],
                "rule_based_justification": row["justification"],
            }
            for row in shortlist_rows
        ]

        prompt = (
            "You are helping a recruiter understand an AI-generated candidate shortlist.\n\n"
            f"Job title: {job_title}\n"
            f"Job description: {job_description}\n\n"
            "For each candidate below, write a single, sharp, recruiter-facing sentence "
            "(max 30 words) explaining why they could be a strong fit for THIS specific "
            "role, building ONLY on the fields provided for that candidate. Do not invent "
            "skills, certifications, or experience not present in the provided fields. "
            "Be honest about gaps.\n\n"
            f"Candidates:\n{json.dumps(candidate_summaries, indent=2)}\n\n"
            "Respond ONLY with a JSON object mapping candidate_id -> justification string. "
            "No other text."
        )

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        text = "".join(block.text for block in response.content if block.type == "text")
        text = text.strip().strip("`")
        if text.startswith("json"):
            text = text[4:].strip()

        raw_results = json.loads(text)

        # --- Anti-hallucination grounding check (per candidate) -----------
        from . import data_validation
        rows_by_id = {row["candidate_id"]: row for row in shortlist_rows}
        validated = {}
        for cand_id, justification in raw_results.items():
            row = rows_by_id.get(cand_id)
            if row is None:
                continue
            cand_skills = {s.strip() for s in row.get("candidate_detected_skills", "").split(",") if s.strip()}
            grounding_skills = jd_skill_names | cand_skills
            if data_validation.validate_llm_justification(justification, grounding_skills, taxonomy):
                validated[cand_id] = justification
            # else: silently drop -> caller keeps the rule-based justification

        return validated

    except Exception:
        # Any failure (network, auth, parsing) -> graceful no-op fallback
        return {}
