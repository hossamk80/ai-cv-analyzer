# =====================================================================
# BLOCK: MAIN DASHBOARD (src/dashboard.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   The entry point — run it with:  streamlit run src/dashboard.py
#
#   It is intentionally SHORT. It only wires the pieces together:
#     config.py           -> all settings
#     i18n.py             -> Arabic/English sentences + language picker
#     extract_cv_data.py  -> reads + scores the CV files
#     ui_components.py    -> draws each section of the page
# =====================================================================

import os
import sys
import tempfile

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from analytics_ui import render_analytics_dashboard, render_candidate_analysis
from config import ALLOW_ANY_PATH, DATA_ROOT, DEFAULT_JOB_DESCRIPTION, PAGE_TITLE
from extract_cv_data import build_matching_text, load_candidates
from i18n import apply_page_direction, render_language_picker, t
from text_extraction import ocr_available
from ui_components import render_contact_panel, render_cv_preview, render_filters, render_results

# ---------------------------------------------------------------------
# 1. PAGE SETUP + LANGUAGE + PAGE DIRECTION
# ---------------------------------------------------------------------
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
render_language_picker()
apply_page_direction()  # Arabic reads right-to-left, English left-to-right
st.title(f"📄 {t('app_title')}")

if not ocr_available():
    st.sidebar.warning(f"⚠️ {t('warn_no_ocr')}")

# ---------------------------------------------------------------------
# 2. CHOOSE WHERE THE CVS COME FROM: project folder OR upload
# ---------------------------------------------------------------------
source = st.sidebar.radio(
    t("source_label"),
    options=["folder", "upload"],
    format_func=lambda key: t(f"source_{key}"),
)

cv_folder = None
upload_signature = ""  # changes whenever the uploaded files change

if source == "upload":
    uploaded_files = st.sidebar.file_uploader(
        t("upload_label"),
        type=["pdf", "doc", "docx", "png", "jpg", "jpeg", "txt"],
        accept_multiple_files=True,
        help=t("upload_hint"),
    )
    if not uploaded_files:
        st.info(t("upload_empty"))
        st.stop()
    # Each visitor gets a private temporary folder for their uploads.
    if "upload_dir" not in st.session_state:
        st.session_state["upload_dir"] = tempfile.mkdtemp(prefix="cv_uploads_")
    cv_folder = st.session_state["upload_dir"]
    for old in os.listdir(cv_folder):          # drop files removed by the user
        os.remove(os.path.join(cv_folder, old))
    for uploaded in uploaded_files:
        safe_name = os.path.basename(uploaded.name)
        with open(os.path.join(cv_folder, safe_name), "wb") as f:
            f.write(uploaded.getbuffer())
    upload_signature = "|".join(sorted(f"{u.name}:{u.size}" for u in uploaded_files))
else:
    # On a server, visitors may NOT type arbitrary paths — that would
    # let them browse the server's disk. They can only pick sub-folders
    # of the approved data folder (DATA_ROOT, default ./data). On your
    # own PC set CV_ANALYZER_ALLOW_ANY_PATH=1 to unlock free path input.
    if ALLOW_ANY_PATH:
        base_folder = st.sidebar.text_input("📁", value=DATA_ROOT)
    else:
        base_folder = DATA_ROOT

    if not os.path.isdir(base_folder):
        st.sidebar.error(t("path_missing", path=base_folder))
        st.info(t("path_hint"))
        st.stop()

    subfolders = sorted(f.name for f in os.scandir(base_folder) if f.is_dir())
    if subfolders:
        choice = st.sidebar.selectbox(t("subfolder_label"), [t("root_folder")] + subfolders)
        cv_folder = base_folder if choice == t("root_folder") else os.path.join(base_folder, choice)
    else:
        cv_folder = base_folder

# ---------------------------------------------------------------------
# 3. MATCHING REQUIREMENTS: job description + structured criteria
# ---------------------------------------------------------------------
st.markdown(t("jd_header"))
job_description = st.text_area(t("jd_label"), value=DEFAULT_JOB_DESCRIPTION, height=120)

# Extra criteria typed by the recruiter. They join the matching with
# more weight than the free text (see build_matching_text).
crit_cols = st.columns(3)
req_education = crit_cols[0].text_input(t("crit_education"), placeholder=t("crit_education_ph"))
req_certs = crit_cols[1].text_input(t("crit_certs"), placeholder=t("crit_certs_ph"))
req_skills = crit_cols[2].text_input(t("crit_skills"), placeholder=t("crit_skills_ph"))

matching_text = build_matching_text(job_description, req_education, req_certs, req_skills)

# ---------------------------------------------------------------------
# 4. LOAD & SCORE THE CVS (cached so repeat visits are instant)
# ---------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_load(folder_path: str, jd: str, signature: str):
    # `signature` is part of the cache key: when the uploaded files
    # change, the analysis re-runs instead of showing stale results.
    records, warnings = load_candidates(folder_path, jd)
    return pd.DataFrame(records), warnings

with st.spinner(t("spinner")):
    df, load_warnings = cached_load(cv_folder, matching_text, upload_signature)

for warning in load_warnings:
    st.sidebar.warning(f"⚠️ {t(warning.pop('key'), **warning)}")

if df.empty:
    st.warning(t("no_cvs"))
    st.info(t("no_cvs_hint"))
    st.stop()

st.sidebar.success(t("loaded_n", n=len(df)))
if st.sidebar.button(t("reanalyze")):
    st.cache_data.clear()
    st.rerun()

# ---------------------------------------------------------------------
# 5. FILTERS -> RESULTS -> ANALYTICS -> CANDIDATE ANALYSIS -> CONTACT
# ---------------------------------------------------------------------
filtered_df = render_filters(df)
render_results(df, filtered_df)

if filtered_df.empty:
    st.warning(t("no_results"))
else:
    # Charts about the whole filtered pool
    render_analytics_dashboard(filtered_df)
    # Pick a candidate, then see their analytical summary vs the job
    selected_row = render_contact_panel(filtered_df)
    render_candidate_analysis(selected_row, filtered_df, matching_text)
    render_cv_preview(selected_row)
