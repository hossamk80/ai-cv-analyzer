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
    # Levels are internal codes; i18n.py turns them into ممتاز/Excellent.
    assert classify_match(50.0) == "excellent"
    assert classify_match(20.0) == "fair"
    assert classify_match(5.0) == "poor"


def test_relative_grading():
    # Best score defines 100%; others graded relative to it.
    assert classify_matches([10.0, 8.0, 4.5, 1.0]) == ["excellent", "excellent", "fair", "poor"]
    # All-zero scores must not crash (division by zero guard).
    assert classify_matches([0.0, 0.0]) == ["poor", "poor"]


def test_legacy_doc_extraction():
    import shutil

    import pytest

    from text_extraction import extract_text

    if shutil.which("antiword") is None:
        pytest.skip("antiword not installed")
    doc = os.path.join(os.path.dirname(__file__), "..", "data", "Youssef_SalahOCP_812641489.doc")
    if not os.path.exists(doc):
        pytest.skip("sample .doc not present")
    assert "Youssef" in extract_text(doc)


def test_translations_have_matching_keys():
    from i18n import TEXTS

    assert set(TEXTS["ar"].keys()) == set(TEXTS["en"].keys())
