"""
pipeline.py
------------
Orchestrates the full Intelligent Candidate Discovery pipeline:

  1. Load jobs, candidates, behavioral signals, skill taxonomy (data_loader)
  2. Deep Job Understanding: parse each JD into structured requirements
     and a "hypothetical ideal candidate" profile (job_understanding)
  3. Build a shared semantic embedding space across all JDs, ideal
     profiles, and candidate resumes (semantic_matcher)
  4. Compute pool-normalized behavioral/intent scores (behavioral_scoring)
  5. Compute candidate data-quality flags -- sparse profiles, implausible
     experience values, possible duplicate/spam profiles (data_validation)
  6. For each job, score every candidate across all four signal types and
     produce a ranked top-K shortlist with explanations (ranker)
  7. (Optional) Refine the top justifications per job with an LLM pass,
     grounded against a per-candidate skill set so hallucinated claims are
     rejected (llm_rerank + data_validation) -- skipped gracefully if no
     API key is configured
  8. Write the combined ranked shortlist to outputs/ranked_shortlist.csv
"""

import pandas as pd

from . import data_loader
from . import job_understanding
from . import semantic_matcher
from . import behavioral_scoring
from . import data_validation
from . import ranker
from . import llm_rerank


def run_pipeline(config: dict) -> pd.DataFrame:
    cm = config["column_map"]
    paths = config["data"]

    jobs_df = data_loader.load_jobs(paths["jobs_path"], cm["jobs"])
    candidates_df = data_loader.load_candidates(paths["candidates_path"], cm["candidates"])
    signals_df = data_loader.load_signals(
        paths["signals_path"], cm["signals"], candidates_df["candidate_id"]
    )
    taxonomy = data_loader.load_skills_taxonomy(paths["skills_taxonomy_path"])

    print(f"Loaded {len(jobs_df)} jobs, {len(candidates_df)} candidates, "
          f"{len(signals_df)} behavioral signal rows.")

    # --- Step 2: Deep Job Understanding ---------------------------------
    parsed_jds = {}
    hypothetical_profiles = {}
    for _, job in jobs_df.iterrows():
        parsed = job_understanding.parse_job_description(job["description"], job["title"], taxonomy)
        parsed_jds[job["job_id"]] = parsed
        hypothetical_profiles[job["job_id"]] = job_understanding.build_hypothetical_ideal_profile(
            job["title"], parsed
        )
        print(f"\n[Job Understanding] {job['job_id']} - {job['title']}")
        print(f"  Required skills : {list(parsed['required_skills'].keys())}")
        print(f"  Preferred skills: {list(parsed['preferred_skills'].keys())}")
        print(f"  Experience range: {parsed['min_years']}-{parsed['max_years']} yrs, "
              f"seniority={parsed['seniority']}")

    # --- Step 3: Shared semantic embedding space ------------------------
    semantic_space = semantic_matcher.build_semantic_space(
        jobs_df, candidates_df, parsed_jds, hypothetical_profiles
    )

    # --- Step 4: Behavioral/intent scores (pool-normalized) -------------
    behavioral_scores = behavioral_scoring.compute_behavioral_scores(signals_df)

    # --- Step 5: Data-quality flags (sparse/implausible/duplicate) ------
    quality_flags = data_validation.compute_quality_flags(candidates_df)
    n_flagged = (quality_flags != "").sum()
    if n_flagged:
        print(f"\n[Data Validation] {n_flagged} of {len(candidates_df)} candidate "
              f"profile(s) flagged for review (sparse/implausible/duplicate).")

    # --- Step 6: Rank candidates per job ---------------------------------
    weights = config["ranking_weights"]
    top_k = config["top_k_per_job"]

    all_shortlists = []
    for _, job in jobs_df.iterrows():
        shortlist = ranker.rank_candidates_for_job(
            job_row=job,
            parsed_jd=parsed_jds[job["job_id"]],
            candidates_df=candidates_df,
            signals_df=signals_df,
            taxonomy=taxonomy,
            semantic_space=semantic_space,
            behavioral_scores=behavioral_scores,
            weights=weights,
            top_k=top_k,
            quality_flags=quality_flags,
        )

        # --- Step 7: Optional LLM re-ranking / justification refinement ---
        llm_cfg = config.get("llm_rerank", {})
        if llm_cfg.get("enabled") and llm_rerank.llm_available():
            top_n = llm_cfg.get("top_n_to_rerank", 5)
            rows_for_llm = shortlist.head(top_n).to_dict("records")
            jd_skill_names = set(parsed_jds[job["job_id"]]["required_skills"].keys()) | \
                set(parsed_jds[job["job_id"]]["preferred_skills"].keys())
            refined = llm_rerank.rerank_top_candidates(
                job["title"], job["description"], rows_for_llm,
                llm_cfg.get("model", "claude-sonnet-4-6"), taxonomy, jd_skill_names,
            )
            if refined:
                shortlist["justification"] = shortlist.apply(
                    lambda r: refined.get(r["candidate_id"], r["justification"]), axis=1
                )
                shortlist["justification_source"] = shortlist["candidate_id"].apply(
                    lambda cid: "llm" if cid in refined else "rule_based"
                )
            else:
                shortlist["justification_source"] = "rule_based"
        else:
            shortlist["justification_source"] = "rule_based"

        all_shortlists.append(shortlist)
        print(f"\n[Ranking] Top {min(3, len(shortlist))} for {job['job_id']} - {job['title']}:")
        for _, row in shortlist.head(3).iterrows():
            print(f"  #{row['rank']} {row['candidate_name']} ({row['candidate_id']}) "
                  f"- score {row['final_score']}")

    final_df = pd.concat(all_shortlists, ignore_index=True)

    # --- Step 8: Write output --------------------------------------------
    final_df.to_csv(paths["output_path"], index=False)
    print(f"\nWrote ranked shortlist for {len(jobs_df)} job(s) -> {paths['output_path']}")

    return final_df
