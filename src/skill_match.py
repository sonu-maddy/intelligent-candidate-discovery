"""
skill_match.py
---------------
"Signal Integration" -- skill-coverage component.

Computes an explainable skill-match score between a candidate and a parsed
job description, using the shared skill taxonomy so that synonyms /
abbreviations (e.g. "ML" vs "machine learning", "JS" vs "javascript") are
correctly matched even when the exact phrasing differs.

Required skills are weighted more heavily than nice-to-have skills, and the
function also returns the lists of matched / missing skills so the ranker
can build a human-readable justification for each candidate.
"""

import re


def extract_candidate_skills(candidate_row, taxonomy: dict) -> set:
    """Returns the set of canonical taxonomy skills found anywhere in the
    candidate's skills field, title, and profile summary. Uses
    word-boundary matching (consistent with job_understanding.py) so short
    surface forms like "excel" or "ml" don't false-positive inside longer
    words like "excellent" or "html"."""
    text = " ".join([
        str(candidate_row.get("skills", "")),
        str(candidate_row.get("current_title", "")),
        str(candidate_row.get("profile_summary", "")),
    ]).lower()

    found = set()
    for canonical, surface_forms in taxonomy.items():
        for form in surface_forms:
            pattern = r"\b" + re.escape(form.lower()) + r"\b"
            if re.search(pattern, text):
                found.add(canonical)
                break
    return found


def skill_match_score(candidate_skills: set, parsed_jd: dict, required_weight: float = 0.75) -> dict:
    """Returns a dict with the overall score (0-1) plus matched/missing
    skill lists for explainability.

    score = required_weight * (required matched / total required)
          + (1 - required_weight) * (preferred matched / total preferred)

    If a JD has no required (or no preferred) skills detected, that term is
    dropped and the remaining weight is renormalized so the score still
    spans 0-1.
    """
    required = set(parsed_jd["required_skills"].keys())
    preferred = set(parsed_jd["preferred_skills"].keys())

    matched_required = candidate_skills & required
    matched_preferred = candidate_skills & preferred
    missing_required = required - candidate_skills
    missing_preferred = preferred - candidate_skills

    components = []
    if required:
        components.append((required_weight, len(matched_required) / len(required)))
    if preferred:
        components.append((1 - required_weight, len(matched_preferred) / len(preferred)))

    if not components:
        score = 0.5  # no detectable skill requirements in JD -> neutral
    else:
        total_weight = sum(w for w, _ in components)
        score = sum(w * v for w, v in components) / total_weight

    return {
        "score": score,
        "matched_required": sorted(matched_required),
        "matched_preferred": sorted(matched_preferred),
        "missing_required": sorted(missing_required),
        "missing_preferred": sorted(missing_preferred),
    }
