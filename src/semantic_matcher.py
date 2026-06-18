"""
semantic_matcher.py
--------------------
"Contextual Relevance" layer -- goes beyond keyword overlap.

We build dense "semantic embeddings" for every job description, every
hypothetical-ideal-candidate profile, and every candidate resume using
TF-IDF + Latent Semantic Analysis (TruncatedSVD). This is a fully offline,
dependency-light technique that still captures co-occurrence-based semantic
structure (synonymy, related terminology) far better than raw keyword
matching -- e.g. a resume mentioning "neural networks, PyTorch, BERT" will
land close to a JD asking for "deep learning / NLP" even with zero exact
keyword overlap.

NOTE FOR PRODUCTION / FURTHER IMPROVEMENT:
This module is intentionally swappable. In an environment with access to a
sentence-embedding model (e.g. via the Anthropic/OpenAI embeddings API or a
local sentence-transformers model), replace `fit_transform` below with calls
to that model -- the rest of the pipeline only depends on getting back a
[n_documents x n_dims] float matrix, so no other file needs to change.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


class SemanticSpace:
    """Fits a shared TF-IDF + LSA space across all documents passed in, then
    exposes cosine-similarity lookups between any two embedded documents."""

    def __init__(self, n_components: int = 50, random_state: int = 42):
        self.n_components = n_components
        self.random_state = random_state
        self.vectorizer = None
        self.svd = None
        self._doc_ids = None
        self._embeddings = None

    def fit(self, doc_ids: list, texts: list):
        n_docs = len(texts)
        # n_components can't exceed n_docs - 1 for TruncatedSVD
        n_components = max(1, min(self.n_components, n_docs - 1))

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )
        tfidf = self.vectorizer.fit_transform(texts)

        self.svd = TruncatedSVD(n_components=n_components, random_state=self.random_state)
        embeddings = self.svd.fit_transform(tfidf)

        self._doc_ids = list(doc_ids)
        self._embeddings = embeddings
        return self

    def get(self, doc_id):
        idx = self._doc_ids.index(doc_id)
        return self._embeddings[idx]

    def similarity(self, doc_id_a, doc_id_b) -> float:
        vec_a = self.get(doc_id_a).reshape(1, -1)
        vec_b = self.get(doc_id_b).reshape(1, -1)
        sim = cosine_similarity(vec_a, vec_b)[0, 0]
        # Clip to [0, 1] -- LSA cosine similarities can be slightly negative
        return float(np.clip(sim, 0.0, 1.0))


def build_semantic_space(jobs_df, candidates_df, parsed_jds: dict, hypothetical_profiles: dict) -> SemanticSpace:
    """Builds one shared semantic space containing:
      - every job's raw description  (id: "job::<job_id>")
      - every job's hypothetical ideal profile (id: "ideal::<job_id>")
      - every candidate's resume text (id: "cand::<candidate_id>")
    Fitting everything jointly ensures all documents share the same
    vocabulary / latent space so similarities are directly comparable.
    """
    doc_ids, texts = [], []

    for _, job in jobs_df.iterrows():
        doc_ids.append(f"job::{job['job_id']}")
        texts.append(job["description"])

        doc_ids.append(f"ideal::{job['job_id']}")
        texts.append(hypothetical_profiles[job["job_id"]])

    for _, cand in candidates_df.iterrows():
        doc_ids.append(f"cand::{cand['candidate_id']}")
        combined = f"{cand['current_title']}. Skills: {cand['skills']}. {cand['profile_summary']}"
        texts.append(combined)

    space = SemanticSpace(n_components=50)
    space.fit(doc_ids, texts)
    return space


def semantic_score(space: SemanticSpace, job_id: str, candidate_id: str) -> float:
    """Combines similarity to the raw JD and similarity to the
    "hypothetical ideal candidate" profile (averaged), which helps catch
    substantively-strong candidates whose phrasing differs from the JD."""
    sim_to_jd = space.similarity(f"job::{job_id}", f"cand::{candidate_id}")
    sim_to_ideal = space.similarity(f"ideal::{job_id}", f"cand::{candidate_id}")
    return 0.5 * sim_to_jd + 0.5 * sim_to_ideal
