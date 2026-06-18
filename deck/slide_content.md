# Deck Content — Paste into the Official Template

Open the official template link → **File → Make a copy** → rename to your
Team ID/Team Name → paste the content below into each slide. Keep it
concise on-slide (this doc gives you full sentences; trim to bullet
fragments on the actual slide and use speaker notes for the rest).

---

## Slide 1 — Team Name / Problem Statement / Team Leader Name

- **Team Name:** <your team name>
- **Problem Statement:** Data & AI Challenge — Intelligent Candidate Discovery
- **Team Leader Name:** <your name>

---

## Slide 2 — Solution Overview

**What is your proposed solution?**
An explainable, modular candidate-ranking pipeline that scores every
candidate against a job posting across four signal types — contextual
semantic relevance, skill coverage, experience fit, and behavioral/intent
signals — and returns a ranked shortlist with a plain-English justification
for every score.

**What differentiates your approach from traditional candidate matching
systems?**
- Goes beyond keyword matching via a TF-IDF+LSA semantic layer compared
  against both the raw JD *and* a synthesized "ideal candidate" profile —
  catches candidates whose resumes are phrased differently but
  substantively fit ("hidden gems").
- Integrates **behavioral/activity signals** (recency, profile updates,
  upskilling, content engagement) — most systems only look at static resume
  text; we model who's actually reachable *right now*.
- **Fully explainable**: every score is broken into 4 components +
  matched/missing skills + a human-readable justification — no black box.
- **Hallucination-safe by construction**: rule-based justifications are
  built only from pre-computed facts; the optional LLM layer is
  grounding-checked and falls back automatically.
- **Config-driven & swap-friendly**: zero code changes needed to point at a
  new dataset, or to swap the embedding layer for a production model.

---

## Slide 3 — JD Understanding & Candidate Evaluation

**What are the key requirements extracted from the JD?**
- Required vs. preferred **skills** (via a 25-skill taxonomy with
  synonyms/abbreviations — e.g. "ML" ↔ "machine learning")
- **Experience range** (min/max years) via pattern extraction
- **Seniority level** (junior / mid / senior / lead)
- A synthesized **"hypothetical ideal candidate" profile** built from the
  above — used as a second comparison target for semantic matching

**Which candidate signals are most important for determining relevance?
How does your solution evaluate fit beyond keyword matching?**
- *Semantic relevance* (35%): TF-IDF+LSA cosine similarity to both the JD
  text and the hypothetical ideal profile — catches synonymy/related
  terminology with zero exact keyword overlap.
- *Skill coverage* (30%): taxonomy-matched required vs. preferred skills,
  weighted 75/25.
- *Experience fit* (15%): trapezoidal curve — full score in-range, steep
  penalty if under-qualified, gentle penalty if over-qualified.
- *Behavioral/intent* (20%): pool-normalized composite of recency,
  profile-update frequency, recent upskilling, endorsement growth, and
  content engagement — **the signal most systems skip entirely**.

---

## Slide 4 — Ranking Methodology

**How does your system retrieve, score, and rank candidates?**
Every candidate in the pool is scored against every job (a complete
re-score per job, not a coarse pre-filter) — at this candidate-pool scale
this is fast (<2 seconds for ~45 candidates × 3 jobs) and guarantees no
"hidden gem" is filtered out before scoring.

**What models, algorithms, or heuristics are used?**
- TF-IDF + Truncated SVD (LSA) for semantic embeddings (offline,
  no model downloads)
- Rule-based sentence-cue NLP for JD parsing (required vs. preferred
  classification)
- Taxonomy-based skill extraction with word-boundary matching
- Trapezoidal experience-fit curve
- Pool-relative min-max normalization for behavioral signals
- Optional: Claude (LLM) re-ranking/justification refinement for top-N,
  with an automated grounding check

**How are multiple candidate signals combined into a final ranking?**
A weighted linear combination, fully configurable in `config.yaml`:

```
final_score = 0.35 × semantic_score
             + 0.30 × skill_match_score
             + 0.15 × experience_fit_score
             + 0.20 × behavioral_score
```
(× 0.85 confidence discount if the profile is flagged `sparse_profile`)

---

## Slide 5 — Explainability & Data Validation

**How are ranking decisions explained?**
Every candidate gets a 1-sentence justification built ENTIRELY from
pre-computed fields: contextual-fit tier, matched/missing required skills,
years-of-experience-vs-range, and behavioral highlights (e.g. "active in
the last 3 days; completed 1 course in the last 6 months"). This is a
template fill, not free generation — **zero hallucination risk by
construction.**

**How do you prevent hallucinations or unsupported justifications?**
The only free-text generation is the *optional* LLM refinement step. Its
output is automatically re-scanned with the same taxonomy-based skill
extractor used everywhere else; if it asserts any skill outside the
"grounding set" (the JD's required/preferred skills + the candidate's own
detected skills — i.e. everything it was shown), that candidate's LLM
justification is **rejected** and we fall back to the rule-based one. Every
output row carries a `justification_source` (`rule_based`/`llm`) flag.

**How does your solution handle inconsistent, low-quality, or suspicious
profiles?**
A dedicated validation pass flags, per candidate:
- `sparse_profile` (resume <8 words) → score discounted ×0.85, surfaced
- `implausible_experience_value` (negative or >45 years) → surfaced
- `skills_not_substantiated_in_narrative` (keyword-stuffing) → surfaced
- `possible_duplicate_profile` (near-identical text to another candidate,
  possible spam/fraud) → surfaced

Flags are surfaced for **recruiter review**, not silently acted on — a
human stays in the loop, except the one case (sparse data) where our
scoring is genuinely low-confidence.

---

## Slide 6 — End-to-End Workflow

1. **Input:** job descriptions + candidate profiles + behavioral/activity
   signals + skill taxonomy
2. **Deep Job Understanding:** parse each JD → required/preferred skills,
   experience range, seniority → synthesize hypothetical ideal profile
3. **Contextual Relevance:** build shared TF-IDF+LSA space across JDs,
   ideal profiles, and resumes → semantic scores
4. **Signal Integration:** compute skill-match, experience-fit, and
   pool-normalized behavioral/intent scores per candidate
5. **Data Validation:** flag sparse/implausible/duplicate profiles
6. **Ranking:** weighted combination → ranked shortlist + justification per
   candidate
7. **(Optional) LLM Refinement:** grounded re-ranking/justification polish
   for top-N, with automatic hallucination rejection
8. **Output:** `ranked_shortlist.csv` — rank, full score breakdown, matched
   skills, quality flags, justification

*(Use README §2's Mermaid diagram for the visual — see slide 7)*

---

## Slide 7 — System Architecture

Insert the architecture diagram here (see `README.md` §2 for the Mermaid
source — render it at https://mermaid.live or via GitHub's README preview,
screenshot, and paste as an image). A pre-rendered PNG is also included at
`deck/architecture_diagram.png` in this repo for direct use.

---

## Slide 8 — Results & Performance

**What results or insights demonstrate ranking quality?**
On the included 44-candidate / 3-job demo dataset (see README §7):
- A candidate with a **100% required-skill match** but a profile dormant
  for 4+ months ranks **below** several candidates with lower raw skill
  overlap but strong recent activity — demonstrating the
  behavioral/intent signal is doing real work, not just decoration.
- **"Hidden gem" candidates** — titled "Software Developer" with resumes
  that don't use ML-engineer phrasing but describe real ML side-projects
  and recent upskilling — land in the **top third** of the ranking, ahead
  of more than a dozen candidates from adjacent domains.
- Off-domain candidates (Sales, HR, Content) correctly sink to the bottom.
- Planted "suspicious" profiles (sparse, implausible experience,
  duplicate text) are all correctly flagged and surfaced with explanations.

*(Replace with real-dataset numbers once available — see SUBMISSION_GUIDE
§4)*

**How does your solution meet the challenge's runtime and compute
constraints?**
- Fully offline — no model downloads, no GPU required.
- TF-IDF+LSA fit + full scoring of ~45 candidates × 3 jobs runs in
  **under 2 seconds** on a standard CPU.
- Scales near-linearly: O(n_candidates × n_jobs) scoring, O(n_docs) for the
  shared embedding fit (computed once, reused for all jobs).
- Optional LLM step only processes the top-N (default 5) candidates per
  job — bounded, predictable cost.

---

## Slide 9 — Technologies Used

| Technology | Why |
|---|---|
| **Python 3** | Core implementation language |
| **pandas / numpy** | Data loading, feature computation, normalization |
| **scikit-learn** (TfidfVectorizer, TruncatedSVD) | Offline semantic embeddings (TF-IDF + LSA) — no model downloads, fully reproducible |
| **PyYAML** | Config-driven design — data paths, column mapping, ranking weights all externalized |
| **Streamlit** (optional) | Interactive demo dashboard for live evaluation |
| **Anthropic Claude API** (optional) | Grounded LLM re-ranking/justification refinement, with automatic hallucination rejection |

Chosen deliberately for an **offline-first, dependency-light, fully
explainable** baseline that's architected to swap in production-grade
components (sentence embeddings, learning-to-rank) without touching the
rest of the pipeline.

---

## Slide 10 — Submission Assets

- **GitHub repo:** <your repo URL>
- **Demo video:** <link, if recorded — e.g. `streamlit run app.py` walkthrough>
- **Ranked output:** `outputs/ranked_shortlist.csv`

---

## Slide 11 — Closing

Thank you!

**<Team Name>** — Intelligent Candidate Discovery
Contact: <email / LinkedIn>
