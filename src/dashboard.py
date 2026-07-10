# =====================================================================
# BLOCK: MAIN DASHBOARD (src/dashboard.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   The entry point — run it with:  streamlit run src/dashboard.py
#
#   It is intentionally SHORT. It only wires the pieces together:
#     config.py           -> all settings and default texts
#     extract_cv_data.py  -> reads + scores the CV folder
#     ui_components.py    -> draws each section of the page
#
#   If you want to change a specific part, open the file named above
#   for that part — you rarely need to edit this file at all.
# =====================================================================

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from config import ALLOW_ANY_PATH, DATA_ROOT, DEFAULT_JOB_DESCRIPTION, PAGE_TITLE
from extract_cv_data import load_candidates
from ui_components import render_contact_panel, render_cv_preview, render_filters, render_results

# ---------------------------------------------------------------------
# 1. PAGE SETUP
# ---------------------------------------------------------------------
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title(f"📄 {PAGE_TITLE}")

# ---------------------------------------------------------------------
# 2. CHOOSE THE CV FOLDER (safely)
# ---------------------------------------------------------------------
# On a server, visitors may NOT type arbitrary paths — that would let
# them browse the server's disk. They can only pick sub-folders of the
# approved data folder (DATA_ROOT, default ./data). On your own PC set
# CV_ANALYZER_ALLOW_ANY_PATH=1 to unlock free path input (config.py).
if ALLOW_ANY_PATH:
    base_folder = st.sidebar.text_input("📁 مسار مجلد السير الذاتية الأساسي", value=DATA_ROOT)
else:
    base_folder = DATA_ROOT

if not os.path.isdir(base_folder):
    st.sidebar.error(f"❌ المسار المحدد غير موجود: {base_folder}")
    st.info("⚠️ أنشئ مجلد data وأضف ملفات السير الذاتية فيه ثم أعد تحميل الصفحة")
    st.stop()

subfolders = sorted(f.name for f in os.scandir(base_folder) if f.is_dir())
if subfolders:
    choice = st.sidebar.selectbox("📁 اختر المجلد الفرعي للمشروع", ["(المجلد الرئيسي)"] + subfolders)
    cv_folder = base_folder if choice == "(المجلد الرئيسي)" else os.path.join(base_folder, choice)
else:
    cv_folder = base_folder

# ---------------------------------------------------------------------
# 3. JOB DESCRIPTION INPUT
# ---------------------------------------------------------------------
st.markdown("### 🎯 تخصيص متطلبات المطابقة والتوظيف")
job_description = st.text_area(
    "📝 الصق الوصف الوظيفي للوظيفة الشاغرة هنا لضبط معايير التطابق آلياً:",
    value=DEFAULT_JOB_DESCRIPTION,
    height=120,
)

# ---------------------------------------------------------------------
# 4. LOAD & SCORE THE CVS (cached so repeat visits are instant)
# ---------------------------------------------------------------------
@st.cache_data(show_spinner="جاري معالجة وتحليل مستندات السير الذاتية... يرجى الانتظار قليلاً")
def cached_load(folder_path: str, jd: str):
    records, warnings = load_candidates(folder_path, jd)
    return pd.DataFrame(records), warnings

df, load_warnings = cached_load(cv_folder, job_description)

for warning in load_warnings:
    st.sidebar.warning(f"⚠️ {warning}")

if df.empty:
    st.warning("⚠️ لا توجد سير ذاتية صالحة أو مقروءة في المجلد المختار حالياً.")
    st.info("💡 تأكد من وجود ملفات PDF أو DOCX في مجلد data")
    st.stop()

st.sidebar.success(f"✅ تم تحميل {len(df)} سيرة ذاتية")
if st.sidebar.button("🔄 إعادة تحليل الملفات من جديد"):
    st.cache_data.clear()
    st.rerun()

# ---------------------------------------------------------------------
# 5. FILTERS -> RESULTS TABLE -> CONTACT -> PREVIEW
# ---------------------------------------------------------------------
filtered_df = render_filters(df)
render_results(df, filtered_df)

if filtered_df.empty:
    st.warning("نعتذر! لا توجد نتائج مطابقة لخيارات الفلترة والتصفية الحالية.")
else:
    selected_row = render_contact_panel(filtered_df)
    render_cv_preview(selected_row)
