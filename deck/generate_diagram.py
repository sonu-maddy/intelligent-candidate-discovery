"""
Generates deck/architecture_diagram.png — a clean, presentation-ready
diagram of the Intelligent Candidate Discovery pipeline, matching the
Mermaid diagram in README.md §2 but rendered as a static image for easy
insertion into the official Google Slides template (slide 7).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Teal Trust palette
TEAL = "#028090"
SEAFOAM = "#00A896"
MINT = "#02C39A"
NAVY = "#1E2761"
AMBER = "#F59E0B"
LIGHT = "#F0F9FB"
WHITE = "#FFFFFF"
TEXT_DARK = "#1E293B"
ARROW_GREY = "#94A3B8"

fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=150)
ax.set_xlim(0, 100)
ax.set_ylim(4, 58)
ax.axis("off")


def box(x, y, w, h, text, facecolor=WHITE, textcolor=TEXT_DARK, fontsize=11,
        edgecolor=TEAL, bold=False, linewidth=1.6):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.6",
        linewidth=linewidth, edgecolor=edgecolor, facecolor=facecolor,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=textcolor, linespacing=1.35,
            fontweight="bold" if bold else "normal")
    return (x, y, w, h)


def vert_arrow(x, y_top, y_bottom, color=ARROW_GREY, lw=2.2):
    ax.annotate("", xy=(x, y_bottom), xytext=(x, y_top),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                 mutation_scale=18, shrinkA=2, shrinkB=2))


def horiz_arrow(x_left, x_right, y, color=ARROW_GREY, lw=2.0):
    ax.annotate("", xy=(x_right, y), xytext=(x_left, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                 mutation_scale=16, shrinkA=2, shrinkB=2))


# Title
ax.text(2, 56, "Intelligent Candidate Discovery — System Architecture",
        fontsize=19, fontweight="bold", color=NAVY, ha="left")

# --- Row 1: Inputs --------------------------------------------------------
y_in = 48.5
inputs = ["Job\nDescriptions", "Candidate\nProfiles", "Behavioral /\nActivity Signals", "Skill\nTaxonomy"]
w_in, gap = 21.5, 2.5
for i, label in enumerate(inputs):
    x = 2 + i * (w_in + gap)
    box(x, y_in, w_in, 5.5, label, facecolor=LIGHT, edgecolor=TEAL, fontsize=11.5, bold=True)

# --- Row 2: Deep Job Understanding ---------------------------------------
y_jd = 38
box(2, y_jd, 38, 6.5,
    "Deep Job Understanding\n(required/preferred skills,\nexperience range, seniority)",
    facecolor=WHITE, edgecolor=TEAL, fontsize=11, bold=True)
box(43, y_jd, 27, 6.5,
    "Hypothetical Ideal\nCandidate Profile\n(synthesized from JD)",
    facecolor=WHITE, edgecolor=TEAL, fontsize=11, bold=True)
horiz_arrow(40, 43, y_jd + 3.25)


# --- Row 3: Contextual relevance + signal integration ---------------------
y_sig = 28
cols = [
    (2, 26, "Contextual Relevance\nTF-IDF + LSA semantic space\n(vs JD & ideal profile)"),
    (30, 23, "Skill-Match Score\n(taxonomy coverage:\nrequired vs preferred)"),
    (55, 21, "Experience-Fit Score\n(trapezoidal curve vs\ntarget experience range)"),
    (78, 20, "Behavioral / Intent Score\n(pool-normalized\nactivity signals)"),
]
for x, w, label in cols:
    box(x, y_sig, w, 7, label, facecolor=WHITE, edgecolor=SEAFOAM, fontsize=10.5, bold=True)


# --- Row 4: Data validation ------------------------------------------------
y_val = 20.5
box(2, y_val, 96, 4.5,
    "Data Validation -- flags sparse / implausible-experience / unsubstantiated-skills /\nduplicate profiles  ->  confidence multiplier + reviewer notes",
    facecolor="#FFF7ED", edgecolor=AMBER, fontsize=10.5, bold=True)

vert_arrow(50, y_sig, y_val + 4.5)

# --- Row 5: Ranker + optional LLM ------------------------------------------
y_rank = 13
box(2, y_rank, 60, 4.5,
    "Weighted Ranker\nfinal_score = 0.35 x semantic + 0.30 x skill_match\n+ 0.15 x experience_fit + 0.20 x behavioral",
    facecolor=NAVY, textcolor=WHITE, edgecolor=NAVY, fontsize=10, bold=True)
box(65, y_rank, 33, 4.5,
    "Optional LLM Refinement\n(grounded; rejects\nungrounded claims)",
    facecolor=MINT, textcolor=WHITE, edgecolor=MINT, fontsize=10, bold=True)
horiz_arrow(62, 65, y_rank + 2.25)

vert_arrow(32, y_val, y_rank + 4.5)

# --- Output label (small caption under ranker) -----------------------------
ax.text(2, 9,
        "Output: outputs/ranked_shortlist.csv -- rank, score breakdown, matched/missing\n"
        "skills, quality flags, justification, justification_source",
        fontsize=10.5, color=NAVY, ha="left", fontweight="bold", linespacing=1.4)

plt.tight_layout()
plt.savefig("architecture_diagram.png", dpi=150, bbox_inches="tight", facecolor="white")
print("Saved architecture_diagram.png")
