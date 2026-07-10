# =====================================================================
# BLOCK: CV LOADER (src/extract_cv_data.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   The "assembly line". It walks a folder of CV files and, for each
#   one, uses the specialist modules to build one candidate record:
#
#     text_extraction.py  -> reads the file into text
#     field_extraction.py -> pulls email / phone / location / ...
#     matching.py         -> scores everyone against the job description
#
#   The dashboard only ever calls load_candidates(folder, jd).
# =====================================================================

import glob
import os
from datetime import datetime

from config import SUPPORTED_EXTENSIONS
from field_extraction import (
    clean_text,
    extract_email,
    extract_experience_years,
    extract_languages,
    extract_location,
    extract_nationality,
    extract_phone,
    infer_candidate_role,
)
from matching import classify_match, classify_matches, score_cvs
from text_extraction import extract_text


def extract_cv_record(filepath: str) -> dict | None:
    """Read ONE file and return its candidate fields (without a score).

    Returns None when the file is unreadable or contains no text.
    """
    text = clean_text(extract_text(filepath))
    if not text.strip():
        return None
    return {
        # NOTE: the name comes from the FILE NAME, because reliably
        # finding a person's name inside free-form CV text needs an
        # NLP model. Name your files "First Last.pdf" for best results.
        "name": os.path.splitext(os.path.basename(filepath))[0],
        "file": filepath,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": extract_location(text),
        "nationality": extract_nationality(text),
        "experience_years": extract_experience_years(text),
        "languages": extract_languages(text),
        "candidate_role": infer_candidate_role(text),
        "extracted_at": datetime.now(),
        "_text": text,  # kept temporarily for scoring; dropped later
    }


def load_candidates(folder_path: str, job_description: str) -> tuple[list[dict], list[str]]:
    """Read every supported CV in a folder and score them all together.

    Returns (records, warnings):
      records  - one dict per successfully-read CV, ready for a table
      warnings - one dict per skipped file: {"key": ..., "file": ...}.
                 The dashboard translates the key into the visitor's
                 language (see i18n.py), so no sentences live here.
    """
    records, warnings = [], []

    for filepath in sorted(glob.glob(os.path.join(folder_path, "*"))):
        if not os.path.isfile(filepath):
            continue
        ext = os.path.splitext(filepath)[1].lower()
        name = os.path.basename(filepath)
        if ext not in SUPPORTED_EXTENSIONS:
            warnings.append({"key": "warn_unsupported", "file": name, "ext": ext})
            continue
        try:
            record = extract_cv_record(filepath)
        except Exception as exc:
            warnings.append({"key": "warn_error", "file": name, "err": str(exc)})
            continue
        if record is None:
            warnings.append({"key": "warn_empty", "file": name})
            continue
        records.append(record)

    # Score ALL CVs in one pass so the scores share the same scale,
    # then grade each candidate relative to the best match found.
    scores = score_cvs([r["_text"] for r in records], job_description)
    levels = classify_matches(scores)
    for record, score, level in zip(records, scores, levels):
        record["match_score"] = score
        record["match_level"] = level
        del record["_text"]

    return records, warnings


def extract_all_data(filepath: str, job_description: str) -> dict | None:
    """Backward-compatible helper: process a single file with a score.

    Prefer load_candidates() — it scores all CVs on one shared scale.
    """
    record = extract_cv_record(filepath)
    if record is None:
        return None
    score = score_cvs([record.pop("_text")], job_description)[0]
    record["match_score"] = score
    record["match_level"] = classify_match(score)
    return record
