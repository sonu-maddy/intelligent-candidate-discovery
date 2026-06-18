const pptxgen = require("pptxgenjs");

// ---- Palette: "Teal Trust" + Navy contrast ---------------------------------
const NAVY = "1E2761";
const TEAL = "028090";
const SEAFOAM = "00A896";
const MINT = "02C39A";
const AMBER = "F59E0B";
const LIGHT = "F0F9FB";
const WHITE = "FFFFFF";
const TEXT_DARK = "1E293B";
const GREY = "64748B";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "India Runs Submission";
pres.title = "Intelligent Candidate Discovery";

const W = 13.33, H = 7.5;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function titleBar(slide, text, opts = {}) {
  slide.addText(text, {
    x: 0.6, y: 0.4, w: W - 1.2, h: 0.9,
    fontSize: 32, bold: true, color: NAVY, fontFace: "Cambria",
    align: "left", margin: 0,
    ...opts,
  });
}

function pageNum(slide, n) {
  slide.addText(`${n} / 11`, {
    x: W - 1.2, y: H - 0.5, w: 0.9, h: 0.35,
    fontSize: 10, color: GREY, align: "right", fontFace: "Calibri",
  });
}

function bulletCard(slide, x, y, w, h, title, body, accent) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: LIGHT },
    shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 45, opacity: 0.08 },
  });
  slide.addShape(pres.shapes.OVAL, {
    x: x + 0.25, y: y + 0.25, w: 0.32, h: 0.32,
    fill: { color: accent },
  });
  slide.addText(title, {
    x: x + 0.7, y: y + 0.18, w: w - 0.9, h: 0.45,
    fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", margin: 0, valign: "middle",
  });
  slide.addText(body, {
    x: x + 0.3, y: y + 0.75, w: w - 0.6, h: h - 0.9,
    fontSize: 12, color: TEXT_DARK, fontFace: "Calibri", margin: 0, valign: "top",
    lineSpacingMultiple: 1.05,
  });
}

// ---------------------------------------------------------------------------
// Slide 1 — Title
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addShape(pres.shapes.OVAL, {
    x: 9.8, y: -2.2, w: 6, h: 6, fill: { color: TEAL, transparency: 70 },
  });
  s.addShape(pres.shapes.OVAL, {
    x: -2, y: 4.2, w: 5, h: 5, fill: { color: MINT, transparency: 80 },
  });

  s.addText("INDIA RUNS  ·  TRACK 1 — THE DATA & AI CHALLENGE", {
    x: 0.8, y: 1.0, w: 11, h: 0.5,
    fontSize: 14, color: SEAFOAM, bold: true, charSpacing: 3, fontFace: "Calibri",
  });
  s.addText("Intelligent Candidate Discovery", {
    x: 0.8, y: 1.6, w: 11.5, h: 1.6,
    fontSize: 48, bold: true, color: WHITE, fontFace: "Cambria",
  });
  s.addText("Beyond keyword filters: an explainable, signal-driven candidate ranking engine.", {
    x: 0.8, y: 3.0, w: 11, h: 0.6,
    fontSize: 16, color: "CADCFC", italic: true, fontFace: "Calibri",
  });

  const fields = [
    ["Team Name", "<your team name>"],
    ["Problem Statement", "Data & AI Challenge — Intelligent Candidate Discovery"],
    ["Team Leader Name", "<your name>"],
  ];
  let fy = 4.3;
  fields.forEach(([label, value]) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.8, y: fy, w: 11.5, h: 0.85, rectRadius: 0.07,
      fill: { color: WHITE, transparency: 92 },
    });
    s.addText(label.toUpperCase(), {
      x: 1.1, y: fy, w: 3, h: 0.85, valign: "middle",
      fontSize: 12, bold: true, color: SEAFOAM, charSpacing: 2, fontFace: "Calibri", margin: 0,
    });
    s.addText(value, {
      x: 4.2, y: fy, w: 8, h: 0.85, valign: "middle",
      fontSize: 15, color: WHITE, fontFace: "Calibri", margin: 0,
    });
    fy += 1.0;
  });
}

// ---------------------------------------------------------------------------
// Slide 2 — Solution Overview
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "Solution Overview");

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 1.5, w: 5.6, h: 5.3, rectRadius: 0.08,
    fill: { color: NAVY },
  });
  s.addText("What is the proposed solution?", {
    x: 0.95, y: 1.78, w: 5, h: 0.5, fontSize: 16, bold: true, color: SEAFOAM, fontFace: "Calibri", margin: 0,
  });
  s.addText(
    "An explainable, modular candidate-ranking pipeline that scores every " +
    "candidate against a job posting across four signal types — contextual " +
    "semantic relevance, skill coverage, experience fit, and behavioral / " +
    "intent signals — and returns a ranked shortlist with a plain-English " +
    "justification for every score.",
    {
      x: 0.95, y: 2.45, w: 4.9, h: 3.8, fontSize: 14, color: WHITE, fontFace: "Calibri",
      margin: 0, lineSpacingMultiple: 1.25,
    }
  );

  s.addText("What differentiates this approach from traditional matching systems?", {
    x: 6.5, y: 1.5, w: 6.2, h: 0.5, fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });

  const diffs = [
    ["Beyond keywords", "Semantic match vs the JD AND a synthesized 'ideal candidate' profile — surfaces 'hidden gems' phrased differently from the posting.", TEAL],
    ["Behavioral / intent signals", "Models who is reachable right now via activity recency, upskilling, and engagement — most systems skip this entirely.", SEAFOAM],
    ["Fully explainable", "Every score = 4 components + matched/missing skills + a plain-English justification. No black box.", MINT],
    ["Hallucination-safe", "Rule-based justifications are template-filled from facts; the optional LLM layer is grounding-checked with automatic fallback.", AMBER],
    ["Config-driven", "Zero code changes to point at a new dataset, or to swap the embedding layer for a production model.", GREY],
  ];
  let dy = 2.05;
  diffs.forEach(([t, d, c]) => {
    s.addShape(pres.shapes.OVAL, { x: 6.5, y: dy + 0.05, w: 0.22, h: 0.22, fill: { color: c } });
    s.addText(t, { x: 6.9, y: dy - 0.08, w: 5.8, h: 0.35, fontSize: 13, bold: true, color: NAVY, fontFace: "Calibri", margin: 0 });
    s.addText(d, { x: 6.9, y: dy + 0.27, w: 5.95, h: 0.65, fontSize: 11, color: TEXT_DARK, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.0 });
    dy += 0.96;
  });

  pageNum(s, 2);
}

// ---------------------------------------------------------------------------
// Slide 3 — JD Understanding & Candidate Evaluation
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "JD Understanding & Candidate Evaluation");

  s.addText("Key requirements extracted from every JD", {
    x: 0.6, y: 1.45, w: 6.2, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });

  const reqs = [
    ["Required vs. preferred skills", "via a 25-skill taxonomy with synonyms/abbreviations (e.g. \"ML\" ↔ \"machine learning\"), classified using sentence-level cue detection."],
    ["Experience range", "min/max years extracted via pattern matching (e.g. \"2-5 years\", \"3+ years\")."],
    ["Seniority level", "junior / mid / senior / lead, via keyword detection."],
    ["Hypothetical ideal candidate profile", "a synthesized skills-forward description used as a SECOND comparison target for semantic matching."],
  ];
  let ry = 1.95;
  reqs.forEach(([t, d]) => {
    s.addShape(pres.shapes.OVAL, { x: 0.6, y: ry + 0.05, w: 0.22, h: 0.22, fill: { color: TEAL } });
    s.addText(t, { x: 1.0, y: ry - 0.08, w: 5.9, h: 0.35, fontSize: 13, bold: true, color: NAVY, fontFace: "Calibri", margin: 0 });
    s.addText(d, { x: 1.0, y: ry + 0.27, w: 5.95, h: 0.75, fontSize: 11.5, color: TEXT_DARK, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.05 });
    ry += 1.18;
  });

  // Right: weight chart
  s.addText("How candidate fit is evaluated beyond keyword matching", {
    x: 7.1, y: 1.45, w: 5.7, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  s.addText(
    "Four complementary signals, combined into final_score. Behavioral/intent " +
    "(20%) is the signal most systems skip — it captures who is reachable right now.",
    { x: 7.1, y: 1.9, w: 5.7, h: 0.7, fontSize: 11.5, color: TEXT_DARK, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.05 }
  );

  s.addChart(pres.charts.DOUGHNUT, [{
    name: "Weight",
    labels: ["Semantic relevance (35%)", "Skill coverage (30%)", "Behavioral / intent (20%)", "Experience fit (15%)"],
    values: [35, 30, 20, 15],
  }], {
    x: 7.1, y: 2.55, w: 5.7, h: 4.3,
    chartColors: [TEAL, SEAFOAM, AMBER, MINT],
    showLegend: true, legendPos: "b", legendFontSize: 11,
    showPercent: true, dataLabelColor: WHITE, dataLabelFontSize: 11,
    holeSize: 55,
  });

  pageNum(s, 3);
}

// ---------------------------------------------------------------------------
// Slide 4 — Ranking Methodology
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "Ranking Methodology");

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 1.5, w: 12.1, h: 1.3, rectRadius: 0.08, fill: { color: NAVY },
  });
  s.addText([
    { text: "final_score  =  ", options: { color: WHITE, bold: true } },
    { text: "0.35 × semantic", options: { color: TEAL, bold: true } },
    { text: "  +  ", options: { color: WHITE } },
    { text: "0.30 × skill_match", options: { color: SEAFOAM, bold: true } },
    { text: "  +  ", options: { color: WHITE } },
    { text: "0.15 × experience_fit", options: { color: MINT, bold: true } },
    { text: "  +  ", options: { color: WHITE } },
    { text: "0.20 × behavioral", options: { color: AMBER, bold: true } },
  ], {
    x: 0.6, y: 1.5, w: 12.1, h: 0.85, align: "center", valign: "middle",
    fontSize: 20, fontFace: "Consolas", margin: 0,
  });
  s.addText("(× 0.85 confidence discount if the profile is flagged sparse_profile — see slide 5)", {
    x: 0.6, y: 2.35, w: 12.1, h: 0.4, align: "center", fontSize: 11.5, italic: true, color: "CADCFC",
    fontFace: "Calibri", margin: 0,
  });

  s.addText("How candidates are retrieved, scored & ranked", {
    x: 0.6, y: 3.2, w: 6.0, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  s.addText(
    "Every candidate in the pool is scored against every job — a complete " +
    "re-score, not a coarse pre-filter. At this scale (~45 candidates × 3 jobs) " +
    "this runs in under 2 seconds, and guarantees no 'hidden gem' is filtered " +
    "out before scoring.",
    { x: 0.6, y: 3.65, w: 6.0, h: 1.5, fontSize: 12.5, color: TEXT_DARK, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.15 }
  );

  s.addText("Models, algorithms & heuristics used", {
    x: 7.0, y: 3.2, w: 5.7, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  const methods = [
    "TF-IDF + Truncated SVD (LSA) for semantic embeddings — offline, no model downloads",
    "Rule-based sentence-cue NLP for required vs. preferred skill classification",
    "Taxonomy-based skill extraction with word-boundary matching",
    "Trapezoidal experience-fit curve (steep penalty if under-qualified, gentle if over)",
    "Pool-relative min-max normalization for behavioral signals",
    "Optional: grounded Claude re-ranking for top-N, with hallucination rejection",
  ];
  s.addText(methods.map((m, i) => ({
    text: m, options: { bullet: { code: "25CF", color: TEAL }, breakLine: i < methods.length - 1, color: TEXT_DARK }
  })), {
    x: 7.0, y: 3.65, w: 5.7, h: 3.4, fontSize: 12, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.15, paraSpaceAfter: 6,
  });

  pageNum(s, 4);
}

// ---------------------------------------------------------------------------
// Slide 5 — Explainability & Data Validation
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "Explainability & Data Validation");

  bulletCard(s, 0.6, 1.5, 3.95, 2.55,
    "How decisions are explained",
    "Every justification is built ENTIRELY from pre-computed fields: " +
    "contextual-fit tier, matched/missing required skills, experience-vs-range, " +
    "and behavioral highlights. A template fill, not free generation — " +
    "zero hallucination risk by construction.",
    TEAL);

  bulletCard(s, 4.7, 1.5, 3.95, 2.55,
    "Preventing hallucinations",
    "The optional LLM step's output is re-scanned with the same taxonomy " +
    "skill extractor used everywhere else. If it asserts a skill outside the " +
    "'grounding set' (JD skills + candidate's own detected skills), that " +
    "justification is REJECTED and the rule-based one is used instead.",
    SEAFOAM);

  bulletCard(s, 8.8, 1.5, 3.95, 2.55,
    "Human stays in the loop",
    "Every output row carries a justification_source (rule_based / llm) " +
    "flag. Quality flags below are SURFACED for recruiter review, not " +
    "silently acted on — except the sparse-profile score discount, where " +
    "confidence is genuinely low.",
    MINT);

  s.addText("Handling inconsistent, low-quality, or suspicious profiles", {
    x: 0.6, y: 4.3, w: 12, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });

  const flagRows = [
    [{ text: "Flag", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Trigger", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Effect", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["sparse_profile", "Resume text under 8 words — too little to assess", "Final score discounted ×0.85, noted in justification"],
    ["implausible_experience_value", "years_experience negative or > 45", "Surfaced for review (no auto-penalty)"],
    ["skills_not_substantiated_in_narrative", ">80% of listed skills never appear in the resume narrative", "Surfaced for review (possible keyword-stuffing)"],
    ["possible_duplicate_profile", "Resume text near-identical to another candidate's", "Surfaced for review, noted in justification (possible spam/fraud)"],
  ];
  s.addTable(flagRows, {
    x: 0.6, y: 4.8, w: 12.1, h: 2.2,
    colW: [3.4, 4.8, 3.9],
    fontSize: 11.5, fontFace: "Calibri", color: TEXT_DARK,
    border: { pt: 0.5, color: "E2E8F0" },
    fill: { color: LIGHT },
    valign: "middle",
    autoPage: false,
  });

  pageNum(s, 5);
}

// ---------------------------------------------------------------------------
// Slide 6 — End-to-End Workflow
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "End-to-End Workflow");
  s.addText("From job description input to a ranked, explainable shortlist", {
    x: 0.6, y: 1.2, w: 12, h: 0.4, fontSize: 14, italic: true, color: GREY, fontFace: "Calibri", margin: 0,
  });

  const steps = [
    ["1", "Input", "Job descriptions, candidate profiles, behavioral signals, skill taxonomy", TEAL],
    ["2", "Deep Job Understanding", "Parse each JD → required/preferred skills, experience range, seniority → synthesize ideal profile", TEAL],
    ["3", "Contextual Relevance", "Shared TF-IDF + LSA space across JDs, ideal profiles & resumes → semantic scores", SEAFOAM],
    ["4", "Signal Integration", "Skill-match, experience-fit, and pool-normalized behavioral/intent scores per candidate", SEAFOAM],
    ["5", "Data Validation", "Flag sparse / implausible / duplicate profiles → confidence multiplier + reviewer notes", AMBER],
    ["6", "Ranking", "Weighted combination → ranked shortlist + plain-English justification per candidate", MINT],
    ["7", "Optional LLM Refinement", "Grounded re-ranking / justification polish for top-N, with automatic hallucination rejection", MINT],
    ["8", "Output", "ranked_shortlist.csv — rank, full score breakdown, matched skills, quality flags, justification", NAVY],
  ];

  const colW = 6.0, rowH = 1.25, gapX = 0.33, gapY = 0.12;
  steps.forEach(([num, t, d, c], i) => {
    const col = Math.floor(i / 4);
    const row = i % 4;
    const x = 0.6 + col * (colW + gapX);
    const y = 1.78 + row * (rowH + gapY);

    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y, w: colW, h: rowH, rectRadius: 0.07,
      fill: { color: LIGHT },
      shadow: { type: "outer", color: "000000", blur: 5, offset: 2, angle: 45, opacity: 0.07 },
    });
    s.addShape(pres.shapes.OVAL, { x: x + 0.18, y: y + (rowH - 0.42) / 2, w: 0.42, h: 0.42, fill: { color: c } });
    s.addText(num, {
      x: x + 0.18, y: y + (rowH - 0.42) / 2, w: 0.42, h: 0.42, align: "center", valign: "middle",
      fontSize: 14, bold: true, color: WHITE, fontFace: "Calibri", margin: 0,
    });
    s.addText(t, {
      x: x + 0.78, y: y + 0.10, w: colW - 0.95, h: 0.38,
      fontSize: 13, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
    });
    s.addText(d, {
      x: x + 0.78, y: y + 0.48, w: colW - 0.95, h: rowH - 0.55,
      fontSize: 10.5, color: TEXT_DARK, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.0,
    });
  });

  pageNum(s, 6);
}

// ---------------------------------------------------------------------------
// Slide 7 — System Architecture
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "System Architecture");
  s.addImage({
    path: "architecture_diagram.png",
    x: 0.4, y: 1.35, w: 12.53, h: 5.85,
    sizing: { type: "contain", w: 12.53, h: 5.85 },
  });
  pageNum(s, 7);
}

// ---------------------------------------------------------------------------
// Slide 8 — Results & Performance
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "Results & Performance");

  const stats = [
    ["Top 1/3", "Hidden-gem candidates (off-title, real ML substance) rank in the top third — ahead of a dozen+ adjacent-domain candidates", TEAL],
    ["< 2 sec", "Full pipeline run: ~45 candidates × 3 jobs, fit + score, on a standard CPU — fully offline, no GPU/model downloads", SEAFOAM],
    ["100%", "Of ranking decisions are explainable — every score = 4 components + matched/missing skills + plain-English justification", MINT],
  ];
  let sx = 0.6;
  stats.forEach(([num, d, c]) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: sx, y: 1.5, w: 3.95, h: 2.4, rectRadius: 0.08, fill: { color: c },
    });
    s.addText(num, { x: sx, y: 1.65, w: 3.95, h: 0.95, align: "center", fontSize: 40, bold: true, color: WHITE, fontFace: "Cambria", margin: 0 });
    s.addText(d, { x: sx + 0.25, y: 2.6, w: 3.45, h: 1.25, align: "center", fontSize: 11, color: WHITE, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.05 });
    sx += 4.15;
  });

  s.addText("What the included 44-candidate / 3-job demo dataset shows", {
    x: 0.6, y: 4.15, w: 12, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
  });
  const findings = [
    "A candidate with a 100% required-skill match but a profile dormant for 4+ months ranks below several candidates with lower raw skill overlap but strong recent activity — the behavioral signal is doing real work, not decoration.",
    "Off-domain candidates (Sales, HR, Content) correctly sink to the bottom of every job's ranking.",
    "Planted 'suspicious' profiles (sparse, implausible experience, duplicate text) are all correctly flagged and surfaced with explanations.",
    "Replace with real-dataset numbers once available (see SUBMISSION_GUIDE §4).",
  ];
  s.addText(findings.map((f, i) => ({
    text: f, options: { bullet: { code: "25CF", color: SEAFOAM }, breakLine: i < findings.length - 1, color: TEXT_DARK }
  })), {
    x: 0.6, y: 4.6, w: 12.1, h: 2.4, fontSize: 12.5, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.15, paraSpaceAfter: 6,
  });

  pageNum(s, 8);
}

// ---------------------------------------------------------------------------
// Slide 9 — Technologies Used
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "Technologies Used");

  const techRows = [
    [{ text: "Technology", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Why", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["Python 3", "Core implementation language"],
    ["pandas / numpy", "Data loading, feature computation, normalization"],
    ["scikit-learn (TfidfVectorizer, TruncatedSVD)", "Offline semantic embeddings (TF-IDF + LSA) — no model downloads, fully reproducible"],
    ["PyYAML", "Config-driven design — data paths, column mapping, ranking weights all externalized"],
    ["Streamlit (optional)", "Interactive demo dashboard for live evaluation"],
    ["Anthropic Claude API (optional)", "Grounded LLM re-ranking / justification refinement, with automatic hallucination rejection"],
  ];
  s.addTable(techRows, {
    x: 0.6, y: 1.5, w: 8.3, h: 5.3,
    colW: [3.6, 4.7],
    fontSize: 12.5, fontFace: "Calibri", color: TEXT_DARK,
    border: { pt: 0.5, color: "E2E8F0" },
    fill: { color: LIGHT },
    valign: "middle",
    autoPage: false,
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 9.15, y: 1.5, w: 3.6, h: 5.3, rectRadius: 0.08, fill: { color: NAVY },
  });
  s.addText("Why this stack?", {
    x: 9.45, y: 1.8, w: 3.0, h: 0.4, fontSize: 15, bold: true, color: SEAFOAM, fontFace: "Calibri", margin: 0,
  });
  s.addText(
    "Chosen deliberately for an offline-first, dependency-light, fully " +
    "explainable baseline — architected so production-grade components " +
    "(sentence embeddings, learning-to-rank) can be swapped in without " +
    "touching the rest of the pipeline.\n\n" +
    "Every swap point is documented in the README (§3.2, §3.5).",
    { x: 9.45, y: 2.35, w: 3.0, h: 4.2, fontSize: 12, color: WHITE, fontFace: "Calibri", margin: 0, lineSpacingMultiple: 1.25 }
  );

  pageNum(s, 9);
}

// ---------------------------------------------------------------------------
// Slide 10 — Submission Assets
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBar(s, "Submission Assets");

  const assets = [
    ["GitHub Repository", "<your repo URL — make sure it's public>", TEAL],
    ["Demo Video", "<link, if recorded — e.g. streamlit run app.py walkthrough>", SEAFOAM],
    ["Ranked Output File", "outputs/ranked_shortlist.csv", MINT],
  ];
  let ay = 1.7;
  assets.forEach(([t, d, c]) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.6, y: ay, w: 12.1, h: 1.5, rectRadius: 0.08,
      fill: { color: LIGHT },
      shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 45, opacity: 0.07 },
    });
    s.addShape(pres.shapes.OVAL, { x: 0.95, y: ay + 0.5, w: 0.5, h: 0.5, fill: { color: c } });
    s.addText(t, {
      x: 1.75, y: ay + 0.18, w: 6, h: 0.5, fontSize: 16, bold: true, color: NAVY, fontFace: "Calibri", margin: 0,
    });
    s.addText(d, {
      x: 1.75, y: ay + 0.68, w: 10.5, h: 0.6, fontSize: 13, color: TEXT_DARK, fontFace: "Consolas", margin: 0,
    });
    ay += 1.75;
  });

  pageNum(s, 10);
}

// ---------------------------------------------------------------------------
// Slide 11 — Closing
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  s.addShape(pres.shapes.OVAL, { x: -2.5, y: -2.5, w: 6, h: 6, fill: { color: TEAL, transparency: 70 } });
  s.addShape(pres.shapes.OVAL, { x: 10, y: 3.5, w: 6, h: 6, fill: { color: MINT, transparency: 80 } });

  s.addText("Thank You", {
    x: 0.8, y: 2.4, w: 11.7, h: 1.4, align: "center",
    fontSize: 48, bold: true, color: WHITE, fontFace: "Cambria",
  });
  s.addText("Intelligent Candidate Discovery — India Runs, Track 1", {
    x: 0.8, y: 3.7, w: 11.7, h: 0.6, align: "center",
    fontSize: 16, color: SEAFOAM, fontFace: "Calibri",
  });
  s.addText("<Team Name>   ·   <contact email / LinkedIn>", {
    x: 0.8, y: 4.5, w: 11.7, h: 0.5, align: "center",
    fontSize: 13, color: "CADCFC", fontFace: "Calibri",
  });
}

pres.writeFile({ fileName: "india_runs_deck.pptx" }).then(() => console.log("Saved india_runs_deck.pptx"));
