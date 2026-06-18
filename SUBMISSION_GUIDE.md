# Submission Guide — India Runs Track 1 (Data & AI Challenge)

This file is for YOU (the participant) — delete it or move it to `/docs`
before final submission if you want a leaner repo, or keep it as a
`SUBMISSION_GUIDE.md` (judges generally don't mind extra context).

---

## 1. What the portal actually asks for (confirmed from the submission form)

The submission form requires **three uploads**, not just code:

| # | Required | Where it is in this repo |
|---|---|---|
| 1 | **GitHub repo URL** (public) | Push everything in this folder — see §3 |
| 2 | **Deck/PPT converted to PDF** — using the **mandatory official template** | Build from `deck/india_runs_deck.pptx` (see §2) → export to PDF |
| 3 | **Ranked output file** (CSV/XLSX) | `outputs/ranked_shortlist.csv` (also export an `.xlsx` if you prefer) |

**Submission closes: Thursday, 2 July 2026, 11:59 PM IST.** (The general
event landing page said 28 June — the actual Track 1 module/portal says
**2 July**. Go with 2 July, but don't cut it close.)

---

## 2. The mandatory deck — structure (from the official template)

The official template ("Idea Submission Template | Redrob") has **11
slides** with fixed prompts. **You must make a copy of this exact template**
(don't build your own from scratch) — Team ID and team name must match what
was given in your intro session.

| Slide | Prompt(s) | Map to this repo |
|---|---|---|
| 1 | Team Name / Problem Statement / Team Leader Name | Fill in your details + "Intelligent Candidate Discovery" |
| 2 | Solution Overview — what's your solution, what differentiates it | README §1, §8 |
| 3 | JD Understanding & Candidate Evaluation — key requirements extracted, which signals matter, fit beyond keywords | README §3.1, §3.3 |
| 4 | Ranking Methodology — retrieve/score/rank, models/algorithms, how signals combine | README §3.2-3.4 (include the weighted formula) |
| 5 | Explainability & Data Validation — how decisions are explained, anti-hallucination, handling bad/suspicious profiles | README §3.6 |
| 6 | End-to-End Workflow — JD input -> ranked output | README §2 (architecture diagram) |
| 7 | System Architecture | README §2 (Mermaid diagram - screenshot it rendered, e.g. from GitHub's README preview or mermaid.live) |
| 8 | Results & Performance — ranking quality evidence, runtime/compute | README §7 (worked example) + note runtime (TF-IDF/LSA on ~45 candidates runs in <2 seconds, scales linearly) |
| 9 | Technologies Used — what & why | requirements.txt: pandas, scikit-learn (TF-IDF/LSA), PyYAML; optional anthropic + streamlit |
| 10 | Submission Assets — GitHub link, video, etc. | Your repo URL + demo video link if you record one |
| 11 | (closing slide) | Thank-you / contact |

I've drafted full slide-by-slide content for you — see
`deck/slide_content.md` — written so you can paste it straight into the
official template. **Open the official template link, File -> Make a copy,
then copy this content in** (I can't edit the Google Slides file directly
since I don't have access to your Google account).

---

## 3. Pushing this to GitHub

```bash
cd intelligent-candidate-discovery
git init
git add .
git commit -m "Intelligent Candidate Discovery - India Runs Track 1 submission"

# Create an EMPTY repo on github.com first (no README/license), then:
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

Make sure the repo is **public** so judges can access it without requesting
permission.

---

## 4. Real dataset -- action needed before final submission

The official dataset is `India_runs_data_and_ai_challenge.zip` on Google
Drive, behind a view page this assistant can't download (no Google Drive
access in this sandbox, and it requires being signed in as a registered
participant).

**To finish this properly:**

1. Download `India_runs_data_and_ai_challenge.zip` yourself from the link
   in your dashboard.
2. Either (a) upload it back to this chat and I'll inspect the real columns
   and rewire `config.yaml`'s `column_map` for you, or (b) do it yourself
   per README §5 -- it's a config-only change, no code edits needed for
   column mapping.
3. Check the **official output-format spec** inside that zip -- if the
   required CSV/XLSX column names differ from `outputs/ranked_shortlist.csv`,
   rename them in the `rows.append({...})` block near the bottom of
   `src/ranker.py` (~15 lines, clearly marked) and add an `.xlsx` export if
   required (pandas: `df.to_excel(...)`).
4. Re-run `python run.py` to regenerate `outputs/ranked_shortlist.csv`
   against real data, and commit that file.

---

## 5. What we found in research -- and how this submission is positioned

- **Most submissions will do *some* form of embedding-based resume<->JD
  similarity** (Sentence-BERT or an LLM embedding call) -- this is the
  default "obvious" approach. Pure semantic similarity alone is table
  stakes, not a differentiator.

- **Few submissions will seriously address "behavioral/activity signals"**
  -- explicitly called out in the brief, but the hardest part to build
  because it requires inventing a feature set and normalization strategy,
  not just calling an embedding API. **This is this submission's strongest
  differentiator** -- README §3.3c.

- **Slide 5 of the official deck (Explainability & Data Validation,
  anti-hallucination, suspicious profiles) is a strong rubric signal** --
  most quick LLM-wrapper submissions won't have a real answer to "how do you
  prevent hallucinations" beyond "we used a good prompt." This submission
  has a concrete, code-level answer (README §3.6): rule-based justifications
  are hallucination-proof by construction, and the optional LLM step has an
  automated grounding check that rejects ungrounded claims.

- **The "hidden gems" framing in the brief is a strong hint about the
  evaluation rubric.** README §7's worked example explicitly demonstrates
  hidden-gem detection and demotion of keyword-stuffed-but-dormant
  profiles -- **point judges directly at this section** in slide 8 and any
  demo video.

### To push further toward "Grand Champion" / "Elite Builders"

In priority order, with ~2 weeks until 2 July:

1. **Run it on the real dataset** (§4) and update README §7 / deck slide 8
   with real numbers -- concrete evidence beats synthetic demos.
2. **Record a 2-3 minute demo video** of `streamlit run app.py` -- link it on
   deck slide 10. Evaluation panels skim code; a video makes the story land
   fast.
3. **Enable the LLM re-ranking step** (`llm_rerank.enabled: true` +
   `ANTHROPIC_API_KEY`) and show a before/after justification comparison on
   slide 5 -- demonstrates classical IR + modern LLM integration with
   graceful degradation.
4. **Add 1-2 unit tests** under a `tests/` folder for scoring functions
   (`experience_fit_score`, `skill_match_score`) -- cheap, signals
   engineering maturity.
5. **Extend `skills_taxonomy.json`** if the real dataset covers domains not
   in the current ~25-skill taxonomy.

---

## 6. Key dates (Track 1)

- Submission closes: **Thu, 2 July 2026, 11:59 PM IST**
- Evaluation phase: 3 - 16 July 2026
- Grand Finale (virtual): 22 July 2026

Don't wait until the last day -- submission portals routinely see traffic
spikes near deadlines.
