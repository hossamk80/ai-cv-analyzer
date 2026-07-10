# =====================================================================
# BLOCK: AUTOMATED TESTS (tests/test_extraction.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   A safety net. Run `pytest` and it checks that the extraction and
#   scoring logic still behaves correctly after any change. GitHub
#   runs these automatically on every push (see .github/workflows/).
# =====================================================================

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from field_extraction import (
    extract_email,
    extract_experience_years,
    extract_nationality,
    extract_phone,
)
from matching import classify_match, classify_matches, score_cvs


def test_extract_email():
    assert extract_email("contact me at ahmad.ali@example.com please") == "ahmad.ali@example.com"
    assert extract_email("no email here") == ""


def test_extract_saudi_phone_is_normalised():
    assert extract_phone("Mobile: 0501234567") == "+966501234567"
    assert extract_phone("Mobile: +966 50 123 4567") == "+966501234567"


def test_extract_international_phone_fallback():
    assert extract_phone("Phone: +971521234567") == "+971521234567"


def test_extract_experience_years():
    assert extract_experience_years("I have 7 years of experience") == "7"
    assert extract_experience_years("خبرة 10 سنوات") == "10"


def test_extract_nationality_is_short():
    text = "Nationality: Saudi Marital Status Single Address Riyadh"
    result = extract_nationality(text)
    assert result.startswith("Saudi")
    assert len(result.split()) <= 2


def test_scores_share_one_scale():
    jd = "network engineer with cisco and firewall experience"
    cvs = [
        "senior network engineer, cisco certified, firewall and routing experience",
        "professional chef with pastry and baking experience",
    ]
    scores = score_cvs(cvs, jd)
    assert len(scores) == 2
    assert scores[0] > scores[1]  # the network engineer must rank higher


def test_empty_job_description_gives_zero():
    assert score_cvs(["some cv text"], "") == [0.0]


def test_classify_levels():
    assert classify_match(50.0) == "ممتاز"
    assert classify_match(20.0) == "متوسط"
    assert classify_match(5.0) == "ضعيف"


def test_relative_grading():
    # Best score defines 100%; others graded relative to it.
    assert classify_matches([10.0, 8.0, 4.5, 1.0]) == ["ممتاز", "ممتاز", "متوسط", "ضعيف"]
    # All-zero scores must not crash (division by zero guard).
    assert classify_matches([0.0, 0.0]) == ["ضعيف", "ضعيف"]
