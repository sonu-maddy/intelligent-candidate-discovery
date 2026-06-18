"""
app.py
-------
Optional interactive demo dashboard for the Intelligent Candidate Discovery
pipeline. This is a bonus on top of the core CLI deliverable (run.py) --
useful for live-demoing the system during evaluation/finale presentations.

Run with:
    streamlit run app.py

Lets a recruiter:
  - pick a job posting
  - see the parsed "Deep Job Understanding" breakdown
  - browse the ranked shortlist with full score breakdowns
  - drill into any candidate's justification and signal details
"""

import yaml
import pandas as pd
import streamlit as st

from src import data_loader, job_understanding, semantic_matcher, behavioral_scoring, ranker

st.set_page_config(page_title="Intelligent Candidate Discovery", layout="wide")


@st.cache_data
def load_everything(config_path="config.yaml"):
    config = yaml.safe_load(open(config_path))
    cm, paths = config["column_map"], config["data"]

    jobs_df = data_loader.load_jobs(paths["jobs_path"], cm["jobs"])
    candidates_df = data_loader.load_candidates(paths["candidates_path"], cm["candidates"])
    signals_df = data_loader.load_signals(paths["signals_path"], cm["signals"], candidates_df["candidate_id"])
    taxonomy = data_loader.load_skills_taxonomy(paths["skills_taxonomy_path"])

    parsed_jds, hypothetical = {}, {}
    for _, job in jobs_df.iterrows():
        parsed = job_understanding.parse_job_description(job["description"], job["title"], taxonomy)
        parsed_jds[job["job_id"]] = parsed
        hypothetical[job["job_id"]] = job_understanding.build_hypothetical_ideal_profile(job["title"], parsed)

    space = semantic_matcher.build_semantic_space(jobs_df, candidates_df, parsed_jds, hypothetical)
    behavioral_scores = behavioral_scoring.compute_behavioral_scores(signals_df)

    return config, jobs_df, candidates_df, signals_df, taxonomy, parsed_jds, space, behavioral_scores


config, jobs_df, candidates_df, signals_df, taxonomy, parsed_jds, space, behavioral_scores = load_everything()

st.title("🔎 Intelligent Candidate Discovery")
st.caption("India Runs · Track 1 · Redrob AI — AI brain for modern hiring")

job_options = {f"{row['job_id']} — {row['title']}": row["job_id"] for _, row in jobs_df.iterrows()}
selected_label = st.selectbox("Select a job posting", list(job_options.keys()))
job_id = job_options[selected_label]
job_row = jobs_df[jobs_df.job_id == job_id].iloc[0]
parsed = parsed_jds[job_id]

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Job Description")
    st.write(job_row["description"])

with col2:
    st.subheader("🧠 Deep Job Understanding")
    st.markdown(f"**Seniority:** {parsed['seniority'].title()}")
    st.markdown(f"**Target experience:** {parsed['min_years']}–{parsed['max_years']} years")
    st.markdown("**Required skills:**")
    st.write(", ".join(parsed["required_skills"].keys()) or "—")
    st.markdown("**Preferred skills:**")
    st.write(", ".join(parsed["preferred_skills"].keys()) or "—")

st.divider()

top_k = st.slider("Number of candidates to show", 5, min(40, len(candidates_df)), 10)

shortlist = ranker.rank_candidates_for_job(
    job_row=job_row,
    parsed_jd=parsed,
    candidates_df=candidates_df,
    signals_df=signals_df,
    taxonomy=taxonomy,
    semantic_space=space,
    behavioral_scores=behavioral_scores,
    weights=config["ranking_weights"],
    top_k=top_k,
)

st.subheader(f"📋 Ranked Shortlist — {job_row['title']}")

for _, row in shortlist.iterrows():
    with st.expander(f"#{row['rank']} · {row['candidate_name']} ({row['current_title']}) — "
                      f"Score: {row['final_score']}/100"):
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("**Score breakdown**")
            score_df = pd.DataFrame({
                "Component": ["Semantic", "Skill Match", "Experience Fit", "Behavioral / Intent"],
                "Score": [row["semantic_score"], row["skill_match_score"],
                          row["experience_fit_score"], row["behavioral_score"]],
            }).set_index("Component")
            st.bar_chart(score_df)
        with c2:
            st.markdown(f"**Years of experience:** {row['years_experience']:g}")
            st.markdown(f"**Matched required skills:** {row['matched_required_skills'] or '—'}")
            st.markdown(f"**Missing required skills:** {row['missing_required_skills'] or '—'}")
            st.markdown("**Justification:**")
            st.info(row["justification"])
            st.caption(f"Source: {row['justification_source']}")

st.divider()
st.caption(
    "This dashboard runs on synthetic sample data (see README §11). "
    "Swap in the official dataset via config.yaml — no code changes needed."
)
