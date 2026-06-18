"""
data_validation.py
--------------------
"Explainability & Data Validation" layer.

Two responsibilities:

1. PROFILE QUALITY FLAGS — detect candidates whose data is too sparse,
   internally inconsistent, or suspiciously duplicated to be scored with
   normal confidence. These candidates are NOT silently dropped (a human
   recruiter should always make the final call) -- instead they're flagged
   in the output, and in the one case where our scoring is genuinely
   unreliable (near-empty profile text), the final score is mildly
   discounted with a clear note in the justification.

2. LLM JUSTIFICATION GROUNDING CHECK — a guardrail used by llm_rerank.py to
   catch hallucinated claims. Every RULE-BASED justification is built ONLY
   from already-computed factual fields (matched/missing skills, scores,
   behavioral highlights) with zero free-text generation, so it is
   hallucination-proof by construction. The optional LLM refinement step is
   the only place free text is generated, so `validate_llm_justification`
   re-runs taxonomy-based skill extraction on the LLM's own output text and
   checks it doesn't assert any skill outside the "grounding set" (the JD's
   required/preferred skills plus the candidate's own detected skills --
   i.e. everything the LLM was actually told about). If it does, the LLM
   output is rejected for that candidate and the pipeline falls back to the
   rule-based justification.
"""

import re
from collections import defaultdict

import pandas as pd

MIN_PROFILE_WORDS = 8           # below this, profile_summary is "too sparse to assess"
MAX_PLAUSIBLE_YEARS = 45         # above this, years_experience is "implausible"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).lower().strip())


def detect_duplicate_profiles(candidates_df: pd.DataFrame) -> dict:
    """Returns {candidate_id: [other_candidate_ids_with_near_identical_text]}
    for any candidates whose profile_summary text is (near-)identical to
    another candidate's -- a common signal of copy-pasted or
    auto-generated/spam profiles. Uses exact match after whitespace/case
    normalization, which is fast and catches the most common case (verbatim
    duplicates); documented as the place to add fuzzy matching (e.g.
    SimHash/MinHash) for production-scale data."""
    groups = defaultdict(list)
    for _, row in candidates_df.iterrows():
        key = _normalize_text(row["profile_summary"])
        if len(key) > 0:
            groups[key].append(row["candidate_id"])

    duplicates = {}
    for ids in groups.values():
        if len(ids) > 1:
            for cid in ids:
                duplicates[cid] = [other for other in ids if other != cid]
    return duplicates


def flag_candidate(candidate_row, duplicates: dict) -> list:
    """Returns a list of short, human-readable quality flags for a single
    candidate. Empty list = no issues detected."""
    flags = []

    summary = str(candidate_row.get("profile_summary", "")).strip()
    word_count = len(summary.split())
    if word_count < MIN_PROFILE_WORDS:
        flags.append("sparse_profile")

    years = candidate_row.get("years_experience", 0)
    try:
        years = float(years)
        if years < 0 or years > MAX_PLAUSIBLE_YEARS:
            flags.append("implausible_experience_value")
    except (TypeError, ValueError):
        flags.append("invalid_experience_value")

    skills_field = str(candidate_row.get("skills", "")).lower()
    if skills_field.strip() and summary:
        listed = [s.strip() for s in re.split(r"[;,]", skills_field) if s.strip()]
        summary_lower = summary.lower()
        unsubstantiated = [s for s in listed if s and s not in summary_lower]
        # Only flag if the MAJORITY of listed skills are absent from the
        # narrative -- a few is normal, all of them suggests keyword-stuffing
        if listed and len(unsubstantiated) / len(listed) > 0.8:
            flags.append("skills_not_substantiated_in_narrative")

    cand_id = candidate_row["candidate_id"]
    if cand_id in duplicates:
        flags.append("possible_duplicate_profile")

    return flags


def compute_quality_flags(candidates_df: pd.DataFrame) -> pd.Series:
    """Returns a Series of comma-separated flag strings, indexed like
    candidates_df (empty string = clean profile)."""
    duplicates = detect_duplicate_profiles(candidates_df)
    return candidates_df.apply(
        lambda row: ", ".join(flag_candidate(row, duplicates)), axis=1
    )


def confidence_multiplier(flags_str: str) -> float:
    """Maps quality flags to a score confidence multiplier. Only
    'sparse_profile' (genuinely insufficient data to assess fit) discounts
    the score -- other flags are surfaced for recruiter review without
    silently changing the ranking, since they may have legitimate
    explanations (e.g. a career-changer's narrative genuinely won't mention
    skills from a previous, unrelated role)."""
    if "sparse_profile" in flags_str:
        return 0.85
    return 1.0


# ---------------------------------------------------------------------------
# LLM justification grounding check (used by llm_rerank.py)
# ---------------------------------------------------------------------------

def _extract_taxonomy_terms(text: str, taxonomy: dict) -> set:
    """Word-boundary taxonomy skill extraction -- same primitive used in
    job_understanding.py / skill_match.py, reused here to check what skills
    an arbitrary piece of text (here, LLM output) actually asserts."""
    text_lower = text.lower()
    found = set()
    for canonical, surface_forms in taxonomy.items():
        for form in surface_forms:
            pattern = r"\b" + re.escape(form.lower()) + r"\b"
            if re.search(pattern, text_lower):
                found.add(canonical)
                break
    return found


def validate_llm_justification(justification: str, grounding_skills: set, taxonomy: dict) -> bool:
    """Returns True if `justification` is safe to use, i.e. every taxonomy
    skill it mentions is contained in `grounding_skills` -- the union of
    (a) the job's required + preferred skills, and (b) the candidate's own
    detected skills. This is everything the LLM was actually shown in its
    prompt, so any skill mentioned OUTSIDE this set was not grounded in the
    data provided and is treated as a potential hallucination.

    Returns False (reject) if the justification is empty, or asserts any
    skill outside the grounding set.
    """
    if not justification or not justification.strip():
        return False

    mentioned = _extract_taxonomy_terms(justification, taxonomy)
    grounding_lower = {s.lower() for s in grounding_skills}
    hallucinated = {m for m in mentioned if m.lower() not in grounding_lower}

    return len(hallucinated) == 0
