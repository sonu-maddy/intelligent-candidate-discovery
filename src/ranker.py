"""
ranker.py
----------
Combines the four signal types into a single ranked shortlist per job:

  final_score = w_semantic   * semantic_score
               + w_skill_match * skill_match_score
               + w_experience  * experience_fit_score
               + w_behavioral  * behavioral_score

All four sub-scores are already in [0, 1], so `final_score` is also in
[0, 1] (assuming weights sum to 1) and is reported scaled to 0-100 for
readability in the output file.

This module also generates a short, rule-based natural-language
justification per (job, candidate) pair -- this is what an LLM re-ranker
(see llm_rerank.py) can optionally refine further.
"""

import pandas as pd

from . import skill_match
from . import experience_fit
from . import semantic_matcher
from . import behavioral_scoring
from . import data_validation


def _build_justification(candidate_row, skill_result: dict, exp_score: float,
                          behavioral_hl: list, semantic_val: float,
                          quality_flags: str) -> str:
    parts = []

    if semantic_val >= 0.6:
        parts.append("strong overall contextual fit with the role")
    elif semantic_val >= 0.35:
        parts.append("moderate contextual fit with the role")
    else:
        parts.append("limited contextual overlap with the role as written")

    if skill_result["matched_required"]:
        parts.append(
            "covers required skills: " + ", ".join(skill_result["matched_required"])
        )
    if skill_result["missing_required"]:
        parts.append(
            "gaps in: " + ", ".join(skill_result["missing_required"])
        )

    parts.append(f"{candidate_row['years_experience']:g} yrs experience "
                  f"({'within' if exp_score >= 1.0 else 'outside'} target range)")

    if behavioral_hl:
        parts.append("; ".join(behavioral_hl))

    text = "; ".join(parts).capitalize() + "."

    if "sparse_profile" in quality_flags:
        text += " Note: profile data is minimal -- score discounted for low confidence; recommend manual review."
    if "possible_duplicate_profile" in quality_flags:
        text += " Note: profile text closely matches another candidate's -- flagged for review."

    return text


def rank_candidates_for_job(
    job_row,
    parsed_jd: dict,
    candidates_df: pd.DataFrame,
    signals_df: pd.DataFrame,
    taxonomy: dict,
    semantic_space,
    behavioral_scores: pd.Series,
    weights: dict,
    top_k: int,
    quality_flags: pd.Series = None,
) -> pd.DataFrame:
    """Returns a DataFrame of the top_k ranked candidates for a single job,
    with full score breakdowns and justifications.

    `quality_flags` (optional) is a Series indexed like candidates_df, as
    produced by data_validation.compute_quality_flags(). If not provided,
    it is computed on the fly.
    """

    if quality_flags is None:
        quality_flags = data_validation.compute_quality_flags(candidates_df)

    rows = []
    signals_by_cand = signals_df.set_index("candidate_id")

    for idx, cand in candidates_df.iterrows():
        cand_id = cand["candidate_id"]

        sem = semantic_matcher.semantic_score(semantic_space, job_row["job_id"], cand_id)

        cand_skills = skill_match.extract_candidate_skills(cand, taxonomy)
        skm = skill_match.skill_match_score(cand_skills, parsed_jd)

        exp = experience_fit.experience_fit_score(
            cand["years_experience"], parsed_jd["min_years"], parsed_jd["max_years"]
        )

        beh = float(behavioral_scores.loc[idx])

        raw_final = (
            weights["semantic"] * sem
            + weights["skill_match"] * skm["score"]
            + weights["experience_fit"] * exp
            + weights["behavioral"] * beh
        )

        flags_str = quality_flags.loc[idx]
        final = raw_final * data_validation.confidence_multiplier(flags_str)

        signal_row = signals_by_cand.loc[cand_id] if cand_id in signals_by_cand.index else pd.Series(dtype=float)
        beh_hl = behavioral_scoring.behavioral_highlights(signal_row)

        justification = _build_justification(cand, skm, exp, beh_hl, sem, flags_str)

        rows.append({
            "job_id": job_row["job_id"],
            "job_title": job_row["title"],
            "candidate_id": cand_id,
            "candidate_name": cand["name"],
            "current_title": cand["current_title"],
            "years_experience": cand["years_experience"],
            "final_score": round(final * 100, 2),
            "semantic_score": round(sem * 100, 2),
            "skill_match_score": round(skm["score"] * 100, 2),
            "experience_fit_score": round(exp * 100, 2),
            "behavioral_score": round(beh * 100, 2),
            "matched_required_skills": ", ".join(skm["matched_required"]),
            "missing_required_skills": ", ".join(skm["missing_required"]),
            "candidate_detected_skills": ", ".join(sorted(cand_skills)),
            "data_quality_flags": flags_str,
            "justification": justification,
        })

    result = pd.DataFrame(rows).sort_values("final_score", ascending=False).reset_index(drop=True)
    result.insert(0, "rank", range(1, len(result) + 1))
    return result.head(top_k)
