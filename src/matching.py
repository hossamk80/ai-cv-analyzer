# =====================================================================
# BLOCK: MATCHING & SCORING (src/matching.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   One job only: compare CV texts against the job description and
#   produce a match score (0–100) plus a level (ممتاز / متوسط / ضعيف).
#
# WHY THIS IS BETTER THAN THE OLD VERSION:
#   1. The old code built a separate vocabulary for EACH CV, so two
#      candidates' scores were not comparable with each other. Now all
#      CVs are scored together against one shared vocabulary, so
#      ranking candidate A above candidate B actually means something.
#   2. The old code removed only ENGLISH stop-words while your CVs and
#      job descriptions are largely ARABIC. Arabic is now normalised
#      (أ/إ/آ -> ا, ة -> ه, ى -> ي, diacritics removed) and Arabic
#      stop-words are ignored too, so Arabic matching works properly.
#   3. Thresholds moved to config.py and were set to realistic values.
# =====================================================================

import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    LEVEL_EXCELLENT,
    LEVEL_FAIR,
    LEVEL_POOR,
    RELATIVE_EXCELLENT,
    RELATIVE_FAIR,
    SCORE_EXCELLENT,
    SCORE_FAIR,
    STOP_WORDS,
)

_ARABIC_DIACRITICS = re.compile(r"[ؗ-ًؚ-ْ]")


def normalize_arabic(text: str) -> str:
    """Unify Arabic letter variants so 'مهندس' matches 'مُهَندس' etc."""
    text = _ARABIC_DIACRITICS.sub("", text)
    text = re.sub("[أإآ]", "ا", text)
    text = text.replace("ة", "ه").replace("ى", "ي")
    return text


def score_cvs(cv_texts: list[str], job_description: str) -> list[float]:
    """Return one score (0–100) per CV, all measured on the same scale."""
    if not job_description or not job_description.strip() or not cv_texts:
        return [0.0] * len(cv_texts)

    documents = [normalize_arabic(t.lower()) for t in [job_description, *cv_texts]]
    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS, ngram_range=(1, 2))
    tfidf = vectorizer.fit_transform(documents)

    # Row 0 is the job description; rows 1.. are the CVs.
    similarities = cosine_similarity(tfidf[0:1], tfidf[1:])[0]
    return [round(float(s) * 100, 2) for s in similarities]


def explain_match(cv_text: str, matching_text: str, max_terms: int = 15) -> tuple[list[str], list[str]]:
    """Explain WHY a CV scored what it did.

    Compares the meaningful words of the job requirements against the
    CV text (both Arabic-normalised) and returns two lists:
      matched  - requirement words found in the CV
      missing  - requirement words NOT found in the CV
    """
    cv_norm = normalize_arabic(cv_text.lower())
    terms, seen = [], set()
    for token in re.findall(r"[\w+#.]+", normalize_arabic(matching_text.lower())):
        token = token.strip(".")
        if len(token) < 3 or token in STOP_WORDS or token in seen:
            continue
        seen.add(token)
        terms.append(token)
    matched = [term for term in terms if term in cv_norm]
    missing = [term for term in terms if term not in cv_norm]
    return matched[:max_terms], missing[:max_terms]


def classify_matches(scores: list[float]) -> list[str]:
    """Grade every candidate RELATIVE to the best match in the batch.

    Raw TF-IDF scores are naturally small (a short job description vs a
    long CV), so a fixed cut-off would label everyone "weak". Instead:
    the strongest candidate defines 100%, and the rest are graded by
    how close they come to that (thresholds in config.py).
    """
    best = max(scores, default=0.0)
    if best <= 0:
        return [LEVEL_POOR] * len(scores)
    levels = []
    for score in scores:
        ratio = score / best
        if ratio >= RELATIVE_EXCELLENT:
            levels.append(LEVEL_EXCELLENT)
        elif ratio >= RELATIVE_FAIR:
            levels.append(LEVEL_FAIR)
        else:
            levels.append(LEVEL_POOR)
    return levels


def classify_match(score: float) -> str:
    """Legacy absolute grading — kept for the old one-file helper."""
    if score >= SCORE_EXCELLENT:
        return LEVEL_EXCELLENT
    if score >= SCORE_FAIR:
        return LEVEL_FAIR
    return LEVEL_POOR
