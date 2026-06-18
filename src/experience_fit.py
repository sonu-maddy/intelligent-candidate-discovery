"""
experience_fit.py
-------------------
"Signal Integration" -- career-metadata component.

Scores how well a candidate's years-of-experience fits the JD's target
range. Uses a trapezoidal scoring curve rather than a hard cutoff:

  - Below min_years: score decreases linearly with the shortfall.
  - Within [min_years, max_years]: full score (1.0).
  - Above max_years: score decreases gently (overqualification is a much
    softer penalty than underqualification, since it mainly raises
    flight-risk/compensation considerations rather than capability gaps --
    but it's still useful to surface for the recruiter).
"""


def experience_fit_score(years_experience: float, min_years: int, max_years: int) -> float:
    years_experience = max(0.0, float(years_experience))

    if min_years <= years_experience <= max_years:
        return 1.0

    if years_experience < min_years:
        shortfall = min_years - years_experience
        # Lose 0.25 per year short, floor at 0
        return max(0.0, 1.0 - 0.25 * shortfall)

    # Overqualified
    excess = years_experience - max_years
    # Lose 0.1 per year over, floor at 0.5 (still plausibly hireable)
    return max(0.5, 1.0 - 0.10 * excess)
