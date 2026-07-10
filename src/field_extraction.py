# =====================================================================
# BLOCK: FIELD EXTRACTION (src/field_extraction.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   One job only: take the raw TEXT of a CV (already extracted by
#   text_extraction.py) and pull out structured fields: email, phone,
#   location, nationality, years of experience, languages, job role.
#
#   The lists of cities / roles / languages it recognises live in
#   config.py — edit them there, not here.
# =====================================================================

import re

from config import KNOWN_LANGUAGES, KNOWN_LOCATIONS, KNOWN_ROLES


def clean_text(text: str) -> str:
    """Remove strange symbols and squeeze repeated spaces."""
    text = re.sub(r"[^\w\s@.\-+:/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_email(text: str) -> str:
    # Requires a real domain ending (".com", ".sa", ...) so broken
    # strings like "name@word" are not accepted as emails.
    match = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Find a Saudi mobile number and return it as +9665XXXXXXXX.

    If no Saudi number exists, fall back to any international number
    written with a + prefix (e.g. +971..., +20...), returned as found.
    """
    compact = text.replace(" ", "").replace("-", "")
    # A number only counts as Saudi with a clear Saudi prefix (+966,
    # 00966, 966) or the local 05... form. The old pattern also matched
    # the middle of foreign numbers, e.g. +971 52... became +96652...
    saudi = re.search(r"(?:\+966|00966|966)(5\d{8})", compact)
    if saudi:
        return "+966" + saudi.group(1)
    local = re.search(r"(?<!\d)0(5\d{8})(?!\d)", compact)
    if local:
        return "+966" + local.group(1)
    intl = re.search(r"\+\d{8,15}", compact)
    return intl.group(0) if intl else ""


def extract_location(text: str) -> str:
    match = re.search(KNOWN_LOCATIONS, text)
    return match.group(0) if match else ""


def extract_nationality(text: str) -> str:
    match = re.search(r"(?i)(nationality|الجنسية)\s*[:\-]?\s*([\w ]+)", text)
    if not match:
        return ""
    # Keep only the first two words after "Nationality:"; the old code
    # swallowed whole sentences ("Saudi Marital Status Single ...").
    return " ".join(match.group(2).strip().split()[:2])


def extract_experience_years(text: str) -> str:
    match = re.search(r"(\d{1,2})\+?\s*(?:years?|سنة|سنوات)", text, re.IGNORECASE)
    return match.group(1) if match else ""


def extract_languages(text: str) -> str:
    found = re.findall(KNOWN_LANGUAGES, text)
    return " / ".join(sorted({lang.capitalize() for lang in found}))


def infer_candidate_role(text: str) -> str:
    for role in KNOWN_ROLES:
        if re.search(re.escape(role), text, re.IGNORECASE):
            return role
    match = re.search(r"(?i)(?:position|role|مسمى وظيفي|عملت كـ)[:\-]?\s*([\w \-]+)", text)
    if match:
        return " ".join(match.group(1).strip().split()[:4])
    return ""
