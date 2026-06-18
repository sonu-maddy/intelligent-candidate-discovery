"""
behavioral_scoring.py
------------------------
"Signal Integration" -- activity/behavioral component, and arguably the
most differentiating part of this challenge's brief ("...subtle behavioral
signals are lost in the noise").

Computes an "intent & momentum" score (0-1) per candidate from raw activity
signals such as profile recency, application velocity, recent upskilling,
and content engagement. The intuition (grounded in how real talent
platforms like LinkedIn / Eightfold operationalize "intent signals", per
our research): a candidate who is actively updating their profile, recently
completed relevant courses, and engages with career-related content is
substantially more "in-market" and reachable right now than an
equally-skilled candidate with a stale, dormant profile -- even if the
stale-profile candidate's resume text matches the JD keyword-for-keyword.

All inputs are min-max normalized ACROSS THE CANDIDATE POOL FOR THIS RUN so
the score is always meaningfully spread across 0-1 regardless of the raw
units. Missing values default to the pool median (neutral, doesn't punish
candidates whose behavioral data wasn't captured).
"""

import pandas as pd
import numpy as np

# Each signal: (column, direction, weight)
# direction = "higher_is_better" or "lower_is_better"
SIGNAL_SPEC = [
    ("profile_completeness_pct", "higher_is_better", 0.15),
    ("last_active_days_ago", "lower_is_better", 0.25),
    ("applications_last_30_days", "higher_is_better", 0.10),
    ("profile_updates_last_90_days", "higher_is_better", 0.15),
    ("courses_completed_last_6_months", "higher_is_better", 0.15),
    ("skill_endorsements_growth_pct", "higher_is_better", 0.10),
    ("content_engagement_score", "higher_is_better", 0.10),
]


def _normalize(series: pd.Series, direction: str) -> pd.Series:
    series = series.astype(float)
    median = series.median()
    series = series.fillna(median)

    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(0.5, index=series.index)  # no variance -> neutral

    norm = (series - lo) / (hi - lo)
    if direction == "lower_is_better":
        norm = 1.0 - norm
    return norm


def compute_behavioral_scores(signals_df: pd.DataFrame) -> pd.Series:
    """Returns a Series indexed like signals_df with a single
    `behavioral_score` in [0, 1] per candidate."""
    total_weight = sum(w for _, _, w in SIGNAL_SPEC)
    score = pd.Series(0.0, index=signals_df.index)

    for col, direction, weight in SIGNAL_SPEC:
        norm = _normalize(signals_df[col], direction)
        score += weight * norm

    score = score / total_weight
    return score.clip(0.0, 1.0)


def behavioral_highlights(signal_row: pd.Series) -> list:
    """Returns a short list of human-readable highlights for the
    justification text, e.g. 'active in the last 3 days',
    'completed 2 courses in the last 6 months'."""
    highlights = []

    last_active = signal_row.get("last_active_days_ago")
    if pd.notna(last_active):
        if last_active <= 14:
            highlights.append(f"active in the last {int(last_active)} days")
        elif last_active >= 60:
            highlights.append(f"inactive for {int(last_active)} days")

    courses = signal_row.get("courses_completed_last_6_months")
    if pd.notna(courses) and courses > 0:
        highlights.append(f"completed {int(courses)} relevant course(s) in the last 6 months")

    updates = signal_row.get("profile_updates_last_90_days")
    if pd.notna(updates) and updates > 0:
        highlights.append(f"updated profile {int(updates)}x in the last 90 days")

    engagement = signal_row.get("content_engagement_score")
    if pd.notna(engagement) and engagement >= 0.5:
        highlights.append("high engagement with career-related content")

    return highlights
