"""
TF-IDF cosine similarity service.

Used to compare a resume's text against a job description.

This module uses scikit-learn's TfidfVectorizer.  The approach is:
  1. Fit a TF-IDF matrix on [resume_text, job_text].
  2. Calculate cosine similarity between the two vectors.
  3. Return a 0–100 score.

Limitations (we are transparent about these):
  - TF-IDF is keyword-frequency-based; it does not understand synonyms or
    context the way a language model would.
  - The score measures textual similarity, NOT hiring suitability.
  - Results are relative and depend heavily on document length.
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SimilarityResult:
    score: float = 0.0          # 0–100
    method: str = "tfidf_cosine"
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    top_job_keywords: list[str] = field(default_factory=list)
    note: str = (
        "This score reflects textual keyword similarity between your resume "
        "and the job description. It is not a prediction of hiring outcome."
    )


def compute_similarity(resume_text: str, job_text: str) -> SimilarityResult:
    """
    Compute TF-IDF cosine similarity between resume and job description.

    Returns SimilarityResult with a 0-100 score.
    """
    if not resume_text.strip() or not job_text.strip():
        return SimilarityResult(score=0.0)

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
        from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
        import numpy as np

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )

        corpus = [resume_text, job_text]
        tfidf_matrix = vectorizer.fit_transform(corpus)

        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        score = round(float(similarity) * 100, 1)

        # Extract top job keywords (by TF-IDF weight in the job doc)
        feature_names = vectorizer.get_feature_names_out()
        job_vector = tfidf_matrix[1].toarray()[0]
        top_indices = np.argsort(job_vector)[::-1][:30]
        top_job_keywords = [feature_names[i] for i in top_indices if job_vector[i] > 0]

        # Determine which top job keywords appear in resume text
        resume_lower = resume_text.lower()
        matched = []
        missing = []
        for kw in top_job_keywords:
            if kw.lower() in resume_lower:
                matched.append(kw)
            else:
                missing.append(kw)

        return SimilarityResult(
            score=score,
            matched_keywords=matched[:20],
            missing_keywords=missing[:20],
            top_job_keywords=top_job_keywords[:20],
        )

    except ImportError:
        logger.error("scikit-learn is not installed; cannot compute similarity")
        return SimilarityResult(
            score=0.0,
            note="scikit-learn is not available. Install it to enable similarity scoring.",
        )
    except Exception as exc:
        logger.exception("TF-IDF similarity failed: %s", exc)
        return SimilarityResult(score=0.0)
