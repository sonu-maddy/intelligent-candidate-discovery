"""
job_understanding.py
---------------------
"Deep Job Understanding" layer.

Parses a free-text job description into a structured representation:
  - required_skills / nice_to_have_skills (mapped onto the skill taxonomy)
  - min_years / max_years of experience
  - seniority level (junior / mid / senior / lead)

This is done with transparent, explainable rule-based NLP (regex +
taxonomy lookups + cue-phrase detection) so it works fully offline with
no model downloads. It is intentionally modular: `parse_job_description`
is the single function the rest of the pipeline calls, so it can be
swapped for an LLM-based structured extractor (see llm_rerank.py for the
pattern) without touching any other module.
"""

import re

# Cue phrases that signal a "must-have" vs "nice-to-have" skill mention
REQUIRED_CUES = [
    "required", "must have", "must-have", "should have", "need to have",
    "strong experience", "solid", "proficiency in", "mandatory",
]
PREFERRED_CUES = [
    "nice to have", "nice-to-have", "preferred", "bonus", "good to have",
    "plus", "added advantage", "is a plus",
]

SENIORITY_KEYWORDS = {
    "lead": ["lead", "principal", "head of", "director", "staff engineer"],
    "senior": ["senior", "sr.", "sr "],
    "junior": ["junior", "jr.", "entry level", "entry-level", "intern", "fresher"],
}

EXPERIENCE_RANGE_RE = re.compile(r"(\d+)\s*[-–to]+\s*(\d+)\s*\+?\s*years?")
EXPERIENCE_MIN_RE = re.compile(r"(\d+)\s*\+?\s*years?")


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _find_skill_mentions(text: str, taxonomy: dict) -> dict:
    """Returns {canonical_skill: matched_surface_form} for every taxonomy
    skill whose surface form appears in `text` as a whole word/phrase
    (word-boundary matched, so e.g. "excel" does not match inside
    "excellent", and "ml" does not match inside "html")."""
    text_lower = text.lower()
    found = {}
    for canonical, surface_forms in taxonomy.items():
        for form in surface_forms:
            pattern = r"\b" + re.escape(form.lower()) + r"\b"
            if re.search(pattern, text_lower):
                found[canonical] = form
                break
    return found


def _classify_sentence(sentence_lower: str) -> str:
    """Classifies a whole sentence as 'required' or 'preferred' based on
    which type of cue phrase appears FIRST in the sentence. This handles the
    common JD pattern "Must have X, Y, Z (sub-detail preferred)" correctly,
    where the dominant directive ("must have") comes before a narrower
    parenthetical caveat ("preferred") about one specific sub-item.

    If a sentence has no cue phrases at all, it defaults to 'required'
    (skills mentioned in plain descriptive sentences are treated as
    expected-but-unflagged requirements)."""
    earliest_required = min((sentence_lower.find(c) for c in REQUIRED_CUES
                              if c in sentence_lower), default=-1)
    earliest_preferred = min((sentence_lower.find(c) for c in PREFERRED_CUES
                               if c in sentence_lower), default=-1)

    if earliest_required == -1 and earliest_preferred == -1:
        return "required"
    if earliest_required == -1:
        return "preferred"
    if earliest_preferred == -1:
        return "required"
    return "required" if earliest_required < earliest_preferred else "preferred"


def _extract_experience_range(text: str):
    text_lower = text.lower()
    m = EXPERIENCE_RANGE_RE.search(text_lower)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = EXPERIENCE_MIN_RE.search(text_lower)
    if m:
        val = int(m.group(1))
        return val, val + 3  # assume a soft +3yr ceiling if only a floor is given
    return 0, 99  # no constraint found -> don't penalize experience


def _extract_seniority(text: str) -> str:
    text_lower = text.lower()
    for level, keywords in SENIORITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return level
    return "mid"


def parse_job_description(description: str, title: str, taxonomy: dict) -> dict:
    """Returns a structured dict describing what the job is looking for.

    {
      "required_skills": {canonical_skill: surface_form, ...},
      "preferred_skills": {canonical_skill: surface_form, ...},
      "min_years": int,
      "max_years": int,
      "seniority": "junior" | "mid" | "senior" | "lead",
    }
    """
    full_text = f"{title}. {description}"
    skill_mentions = _find_skill_mentions(full_text, taxonomy)

    # Classify each sentence as 'required' or 'preferred', then collect the
    # skills mentioned within each. A skill that appears in ANY 'required'
    # sentence is treated as required, even if it also appears in a separate
    # 'preferred' sentence elsewhere (required takes precedence).
    required_skills, preferred_skills = {}, {}
    sentences = SENTENCE_SPLIT_RE.split(full_text)
    for sentence in sentences:
        sentence_lower = sentence.lower()
        bucket = _classify_sentence(sentence_lower)
        sentence_skills = _find_skill_mentions(sentence, taxonomy)
        for canonical, surface_form in sentence_skills.items():
            if bucket == "required":
                required_skills[canonical] = surface_form
            elif canonical not in required_skills:
                preferred_skills[canonical] = surface_form

    # Anything detected in the full text but not assigned to either bucket
    # (shouldn't normally happen given the default-required rule, but kept
    # as a safety net) falls back to 'required'.
    for canonical, surface_form in skill_mentions.items():
        if canonical not in required_skills and canonical not in preferred_skills:
            required_skills[canonical] = surface_form

    # required takes precedence if a skill ended up in both buckets
    preferred_skills = {k: v for k, v in preferred_skills.items() if k not in required_skills}

    min_years, max_years = _extract_experience_range(full_text)
    seniority = _extract_seniority(full_text)

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "min_years": min_years,
        "max_years": max_years,
        "seniority": seniority,
    }


def build_hypothetical_ideal_profile(job_title: str, parsed_jd: dict) -> str:
    """Builds a short synthetic "ideal candidate" text from the parsed JD.

    Idea (inspired by ConFit v2's "hypothetical resume" technique): rather
    than only comparing the raw JD text to each resume, we also construct a
    dense, skills-forward description of what an ideal candidate would look
    like, and compare resumes against THAT too. This helps surface
    candidates whose resumes are phrased very differently from the JD but
    who substantively cover the same ground -- i.e. the "hidden gems" this
    challenge asks us to find.
    """
    all_skills = list(parsed_jd["required_skills"].values()) + list(parsed_jd["preferred_skills"].values())
    seniority = parsed_jd["seniority"]
    years = parsed_jd["min_years"]
    return (
        f"A {seniority}-level {job_title} with approximately {years}+ years of relevant "
        f"experience. Demonstrated, hands-on expertise in: {', '.join(all_skills)}. "
        f"Track record of applying these skills to real projects."
    )
