"""
generate_sample_data.py
------------------------
Generates a realistic SYNTHETIC dataset (job postings, candidate profiles,
and behavioral/activity signals) so the pipeline can be run and demoed
end-to-end before the official India Runs dataset is plugged in.

Swap this out for the real challenge dataset by pointing config.yaml's
`data.jobs_path`, `data.candidates_path`, and `data.signals_path` at the
official files (and adjusting `column_map` if column names differ).
"""

import csv
import random
import os

random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(__file__))

# ---------------------------------------------------------------------------
# JOB POSTINGS
# ---------------------------------------------------------------------------
JOBS = [
    {
        "job_id": "J001",
        "title": "Machine Learning Engineer",
        "location": "Bengaluru",
        "description": (
            "We are looking for a Machine Learning Engineer to join our AI platform team. "
            "Must have strong hands-on experience with Python, machine learning and deep "
            "learning (transformers, BERT/LLMs preferred). Required: 2-5 years of experience "
            "building and deploying ML models, solid SQL skills, and experience with NLP. "
            "Nice to have: experience with AWS or GCP, MLOps, and data pipelines (Spark/Airflow). "
            "You'll work on building intelligent ranking and recommendation systems used by "
            "millions of users across India. We value people who keep learning and experimenting "
            "with the latest in AI."
        ),
    },
    {
        "job_id": "J002",
        "title": "Data Analyst",
        "location": "Remote (India)",
        "description": (
            "Seeking a Data Analyst with 1-3 years of experience to support hiring and growth "
            "analytics. Required: strong SQL, Excel, and data visualization skills (Tableau or "
            "Power BI). Statistics and A/B testing experience preferred. Python is a nice-to-have "
            "for automating reports. You will work closely with product and growth teams to "
            "surface insights from large datasets and present them clearly to stakeholders."
        ),
    },
    {
        "job_id": "J003",
        "title": "Product Manager - AI Hiring Platform",
        "location": "Gurugram",
        "description": (
            "We need a Product Manager with 3-6 years of experience to own the roadmap for our "
            "AI-powered candidate discovery product. Required: strong product management "
            "fundamentals, stakeholder management, and excellent communication skills. A working "
            "understanding of machine learning / NLP concepts is required so you can collaborate "
            "effectively with the ML team. Experience with go-to-market strategy and user research "
            "is a plus. You'll define how millions of Indian job seekers and recruiters experience "
            "AI-driven matching."
        ),
    },
]

# ---------------------------------------------------------------------------
# CANDIDATE PROFILES
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Ananya", "Diya", "Priya", "Saanvi", "Aadhya", "Kiara",
    "Myra", "Anika", "Ira", "Riya", "Rohan", "Karthik", "Sneha", "Pooja",
    "Neha", "Rahul", "Vikram", "Sanjay", "Megha", "Tanvi", "Nikhil", "Aisha",
]
LAST_NAMES = [
    "Sharma", "Verma", "Iyer", "Nair", "Reddy", "Gupta", "Joshi", "Patel",
    "Singh", "Kumar", "Das", "Mehta", "Rao", "Pillai", "Chatterjee", "Bose",
]
CITIES = ["Bengaluru", "Gurugram", "Hyderabad", "Pune", "Mumbai", "Noida", "Chennai", "Remote (India)"]

CURRENT_TITLES_ML = ["Software Developer", "Data Science Intern", "ML Engineer", "Backend Developer", "Research Assistant"]
CURRENT_TITLES_DA = ["Business Analyst", "Operations Analyst", "Data Analyst", "MIS Executive", "Finance Analyst"]
CURRENT_TITLES_PM = ["Associate Product Manager", "Business Analyst", "Product Analyst", "Program Manager", "Consultant"]

SKILL_PHRASES_ML = [
    "Python", "pandas", "scikit-learn", "deep learning", "neural networks",
    "NLP", "transformers", "SQL", "AWS", "PyTorch", "data pipelines", "Airflow",
]
SKILL_PHRASES_DA = [
    "SQL", "Excel", "Tableau", "Power BI", "statistics", "A/B testing", "Python", "data cleaning",
]
SKILL_PHRASES_PM = [
    "product management", "stakeholder management", "roadmap planning", "go-to-market",
    "user research", "communication", "machine learning fundamentals", "NLP",
]

RESUME_TEMPLATES = [
    "{name} is a {title} based in {city} with {exp} years of experience. "
    "Core strengths include {skills}. {extra}",
    "{title} with {exp} years of experience, currently based in {city}. "
    "Has worked extensively with {skills}. {extra}",
    "{name}, {title} ({exp} yrs, {city}). Skilled in {skills}. {extra}",
]

EXTRA_SNIPPETS_STRONG = [
    "Recently completed an advanced certification and built a side project applying these skills to real-world problems.",
    "Active open-source contributor and frequently writes about emerging trends in the field.",
    "Led a small team on a recent project and is looking to take on more ownership.",
    "Has been actively upskilling through online courses over the past few months.",
]
EXTRA_SNIPPETS_WEAK = [
    "Profile has not been updated in a while.",
    "Looking for a role similar to current responsibilities.",
    "No recent learning activity recorded.",
    "",
]


def make_resume(name, title, exp, city, skills, strong_signal):
    extra = random.choice(EXTRA_SNIPPETS_STRONG if strong_signal else EXTRA_SNIPPETS_WEAK)
    template = random.choice(RESUME_TEMPLATES)
    return template.format(name=name, title=title, exp=exp, city=city, skills=", ".join(skills), extra=extra).strip()


def gen_candidate(cid, profile_type, hidden_gem=False, low_intent=False):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    city = random.choice(CITIES)

    if profile_type == "ml":
        title = random.choice(CURRENT_TITLES_ML)
        exp = random.randint(1, 6)
        if hidden_gem:
            # Strong substantive skills but title/keywords don't scream "ML Engineer"
            skills = ["Python", "pandas", "scikit-learn", "personal ML side-projects", "SQL"]
            title = "Software Developer"
        else:
            n = random.randint(4, len(SKILL_PHRASES_ML))
            skills = random.sample(SKILL_PHRASES_ML, n)
    elif profile_type == "da":
        title = random.choice(CURRENT_TITLES_DA)
        exp = random.randint(1, 4)
        n = random.randint(3, len(SKILL_PHRASES_DA))
        skills = random.sample(SKILL_PHRASES_DA, n)
    elif profile_type == "pm":
        title = random.choice(CURRENT_TITLES_PM)
        exp = random.randint(2, 7)
        n = random.randint(3, len(SKILL_PHRASES_PM))
        skills = random.sample(SKILL_PHRASES_PM, n)
    else:  # irrelevant / off-domain
        title = random.choice(["Sales Executive", "HR Generalist", "Content Writer", "Operations Manager"])
        exp = random.randint(1, 8)
        skills = random.sample(["sales", "lead generation", "content writing", "HR operations", "recruitment"], 3)

    strong_signal = not low_intent
    resume = make_resume(name, title, exp, city, skills, strong_signal)

    return {
        "candidate_id": cid,
        "name": name,
        "current_title": title,
        "years_experience": exp,
        "location": city,
        "skills": "; ".join(skills),
        "profile_summary": resume,
        "_profile_type": profile_type,
        "_low_intent": low_intent,
    }


def gen_behavioral_signals(cid, low_intent):
    if low_intent:
        return {
            "candidate_id": cid,
            "profile_completeness_pct": random.randint(40, 65),
            "last_active_days_ago": random.randint(60, 180),
            "applications_last_30_days": 0,
            "profile_updates_last_90_days": 0,
            "courses_completed_last_6_months": 0,
            "skill_endorsements_growth_pct": random.randint(-5, 5),
            "content_engagement_score": round(random.uniform(0.0, 0.2), 2),
        }
    else:
        return {
            "candidate_id": cid,
            "profile_completeness_pct": random.randint(75, 100),
            "last_active_days_ago": random.randint(0, 14),
            "applications_last_30_days": random.randint(0, 5),
            "profile_updates_last_90_days": random.randint(1, 4),
            "courses_completed_last_6_months": random.randint(0, 3),
            "skill_endorsements_growth_pct": random.randint(5, 40),
            "content_engagement_score": round(random.uniform(0.3, 0.95), 2),
        }


def main():
    candidates = []
    signals = []

    cid_counter = 1

    def add(profile_type, count, hidden_gem=False, low_intent=False):
        nonlocal cid_counter
        for _ in range(count):
            cid = f"C{cid_counter:03d}"
            cid_counter += 1
            cand = gen_candidate(cid, profile_type, hidden_gem=hidden_gem, low_intent=low_intent)
            candidates.append(cand)
            signals.append(gen_behavioral_signals(cid, low_intent))

    # Strong, obvious matches
    add("ml", 8)
    add("da", 8)
    add("pm", 8)

    # "Hidden gems" -- weak keyword overlap but strong substance + high intent
    add("ml", 3, hidden_gem=True, low_intent=False)

    # Keyword-stuffed but disengaged candidates (stale profiles)
    add("ml", 3, low_intent=True)
    add("da", 2, low_intent=True)
    add("pm", 2, low_intent=True)

    # Off-domain / irrelevant candidates for contrast
    add("other", 6)

    # --- Deliberately "suspicious" profiles, to demo data_validation.py ---

    # 1) Sparse profile: almost no information to assess
    cid = f"C{cid_counter:03d}"; cid_counter += 1
    candidates.append({
        "candidate_id": cid, "name": "Rohit Sharma", "current_title": "Engineer",
        "years_experience": 2, "location": "Pune", "skills": "Python",
        "profile_summary": "Engineer looking for opportunities.",
        "_profile_type": "ml", "_low_intent": False,
    })
    signals.append(gen_behavioral_signals(cid, low_intent=False))

    # 2) Implausible years_experience value (likely a data-entry error)
    cid = f"C{cid_counter:03d}"; cid_counter += 1
    candidates.append({
        "candidate_id": cid, "name": "Sunita Rao", "current_title": "Data Analyst",
        "years_experience": 60, "location": "Hyderabad",
        "skills": "SQL; Excel; Power BI; statistics",
        "profile_summary": (
            "Sunita Rao, Data Analyst (60 yrs, Hyderabad). Skilled in SQL, Excel, "
            "Power BI, statistics. Recently completed an advanced certification."
        ),
        "_profile_type": "da", "_low_intent": False,
    })
    signals.append(gen_behavioral_signals(cid, low_intent=False))

    # 3) & 4) Near-duplicate profiles (copy-pasted text, possible spam/fraud)
    duplicate_text = (
        "Experienced professional with 3 years of experience in Python, SQL, "
        "machine learning, and data visualization. Passionate about AI and "
        "looking for new opportunities."
    )
    for nm in ["Arjun Kapoor", "Arjun Kapoor"]:
        cid = f"C{cid_counter:03d}"; cid_counter += 1
        candidates.append({
            "candidate_id": cid, "name": nm, "current_title": "Data Scientist",
            "years_experience": 3, "location": "Bengaluru",
            "skills": "Python; SQL; machine learning; data visualization",
            "profile_summary": duplicate_text,
            "_profile_type": "ml", "_low_intent": False,
        })
        signals.append(gen_behavioral_signals(cid, low_intent=False))

    # Write candidates.csv
    cand_fields = ["candidate_id", "name", "current_title", "years_experience", "location", "skills", "profile_summary"]
    with open(os.path.join(OUT_DIR, "candidates.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cand_fields)
        writer.writeheader()
        for c in candidates:
            writer.writerow({k: c[k] for k in cand_fields})

    # Write jobs.csv
    job_fields = ["job_id", "title", "location", "description"]
    with open(os.path.join(OUT_DIR, "jobs.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=job_fields)
        writer.writeheader()
        for j in JOBS:
            writer.writerow(j)

    # Write behavioral_signals.csv
    sig_fields = list(signals[0].keys())
    with open(os.path.join(OUT_DIR, "behavioral_signals.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sig_fields)
        writer.writeheader()
        for s in signals:
            writer.writerow(s)

    print(f"Generated {len(JOBS)} jobs, {len(candidates)} candidates, {len(signals)} behavioral signal rows.")


if __name__ == "__main__":
    main()
