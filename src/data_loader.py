"""
data_loader.py
---------------
Loads jobs, candidates, and behavioral signal CSVs and applies the
configurable column_map so the rest of the pipeline can rely on a
fixed set of internal field names regardless of the source schema.
"""

import json
import pandas as pd


def _rename_with_map(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Rename df columns from real-dataset names -> internal names.

    `mapping` is {internal_name: real_column_name}. We invert it to build
    a rename dict, and only rename columns that actually exist (so the
    pipeline degrades gracefully if a real dataset is missing an optional
    field rather than crashing).
    """
    rename_dict = {}
    for internal_name, real_name in mapping.items():
        if real_name in df.columns:
            rename_dict[real_name] = internal_name
    return df.rename(columns=rename_dict)


def load_jobs(path: str, column_map: dict) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _rename_with_map(df, column_map)
    required = ["job_id", "title", "description"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"jobs file is missing required column '{col}' after applying column_map")
    df["description"] = df["description"].fillna("")
    return df


def load_candidates(path: str, column_map: dict) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _rename_with_map(df, column_map)
    required = ["candidate_id", "profile_summary"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"candidates file is missing required column '{col}' after applying column_map")

    # Optional columns get safe defaults if absent in the real dataset
    if "name" not in df.columns:
        df["name"] = df["candidate_id"]
    if "current_title" not in df.columns:
        df["current_title"] = ""
    if "years_experience" not in df.columns:
        df["years_experience"] = 0
    if "skills" not in df.columns:
        df["skills"] = ""

    df["profile_summary"] = df["profile_summary"].fillna("")
    df["skills"] = df["skills"].fillna("")
    df["current_title"] = df["current_title"].fillna("")
    df["years_experience"] = pd.to_numeric(df["years_experience"], errors="coerce").fillna(0)
    return df


def load_signals(path: str, column_map: dict, candidate_ids) -> pd.DataFrame:
    """Loads behavioral signals. If the file is missing or a candidate has no
    row, behavioral scoring falls back to neutral defaults (0.5 normalized)
    rather than crashing -- the pipeline must still run on partial data."""
    try:
        df = pd.read_csv(path)
        df = _rename_with_map(df, column_map)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["candidate_id"])

    if "candidate_id" not in df.columns:
        df["candidate_id"] = []

    numeric_cols = [
        "profile_completeness_pct", "last_active_days_ago",
        "applications_last_30_days", "profile_updates_last_90_days",
        "courses_completed_last_6_months", "skill_endorsements_growth_pct",
        "content_engagement_score",
    ]
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = pd.NA

    # Ensure every candidate has a row (fill missing candidates with NaN -> handled downstream)
    all_ids = pd.DataFrame({"candidate_id": list(candidate_ids)})
    df = all_ids.merge(df, on="candidate_id", how="left")
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_skills_taxonomy(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)
    taxonomy.pop("_comment", None)
    return taxonomy
