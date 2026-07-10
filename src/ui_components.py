# =====================================================================
# BLOCK: UI COMPONENTS (src/ui_components.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   The reusable visual pieces of the dashboard. Each function draws
#   ONE section of the page. dashboard.py just calls them in order.
#
#   To change how a section LOOKS, edit the matching function here.
#   To change WHAT DATA it shows, look at extract_cv_data.py instead.
# =====================================================================

import os
import urllib.parse

import docx
import fitz
import pandas as pd
import streamlit as st

from config import DEFAULT_CONTACT_MESSAGE, DEFAULT_EMAIL_SUBJECT


# ---------------------------------------------------------------------
# SECTION: sidebar filters
# ---------------------------------------------------------------------
def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Draw the sidebar filters and return the filtered table."""
    with st.sidebar:
        st.header("تصفية وفلترة المرشحين")
        city = st.selectbox("اختر المدينة", options=[""] + sorted(df.location.dropna().unique()))
        nationality = st.selectbox("اختر الجنسية", options=[""] + sorted(df.nationality.dropna().unique()))
        match_level = st.multiselect(
            "مستوى التطابق المستهدف",
            options=sorted(df.match_level.unique()),
            default=sorted(df.match_level.unique()),
        )
        min_experience = st.slider("أقل عدد سنوات خبرة عملية", min_value=0, max_value=30, value=0)
        search_text = st.text_input("🔍 بحث نصي حر شامل داخل البيانات")

    filtered = df.copy()
    if city:
        filtered = filtered[filtered.location.str.contains(city, case=False, na=False)]
    if nationality:
        filtered = filtered[filtered.nationality.str.contains(nationality, case=False, na=False)]
    if match_level:
        filtered = filtered[filtered.match_level.isin(match_level)]
    if "experience_years" in filtered.columns:
        filtered["experience_years"] = pd.to_numeric(filtered["experience_years"], errors="coerce")
        filtered = filtered[
            (filtered["experience_years"].isna()) | (filtered["experience_years"] >= min_experience)
        ]
    if search_text:
        filtered = filtered[
            filtered.apply(lambda row: search_text.lower() in str(row.to_dict()).lower(), axis=1)
        ]
    return filtered


# ---------------------------------------------------------------------
# SECTION: summary metrics + results table + CSV export
# ---------------------------------------------------------------------
def render_results(df: pd.DataFrame, filtered: pd.DataFrame) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي السير الذاتية المعالجة", len(df))
    col2.metric("عدد النتائج المطابقة للفلترة", len(filtered))
    col3.metric("متوسط نسبة التطابق", f"{filtered.match_score.mean():.1f}%" if not filtered.empty else "—")

    if not filtered.empty:
        st.download_button(
            label="📥 تصدير قائمة المرشحين المفلترة كـ CSV",
            data=filtered.to_csv(index=False).encode("utf-8-sig"),
            file_name="candidates_report.csv",
            mime="text/csv",
        )

    columns_to_show = [
        "name", "email", "phone", "location", "nationality", "candidate_role",
        "experience_years", "languages", "match_score", "match_level",
    ]
    actual = [c for c in columns_to_show if c in filtered.columns]
    st.dataframe(
        filtered[actual].sort_values("match_score", ascending=False),
        use_container_width=True,
    )


# ---------------------------------------------------------------------
# SECTION: contact panel (WhatsApp / e-mail / LinkedIn)
# ---------------------------------------------------------------------
def render_contact_panel(filtered: pd.DataFrame) -> pd.Series:
    """Draw the candidate contact section; return the selected row."""
    st.markdown("---")
    st.header("📤 قنوات التواصل والربط مع المرشح")

    selected_name = st.selectbox(
        "اختر اسماً من القائمة لبدء الاتصال وتدقيق الملف الخاص به:",
        filtered.name,
    )
    row = filtered[filtered.name == selected_name].iloc[0]

    default_msg = DEFAULT_CONTACT_MESSAGE.format(
        name=row["name"],
        role=row.get("candidate_role") or "الدعم الفني",
    )
    msg_template = st.text_area("📩 نص الرسالة المخصصة (يمكنك تعديلها بحرية):", value=default_msg, height=120)
    subject_text = st.text_input("📝 عنوان موضوع البريد الإلكتروني:", value=DEFAULT_EMAIL_SUBJECT)

    encoded_msg = urllib.parse.quote(msg_template)
    email_subject = urllib.parse.quote(subject_text)

    c1, c2, c3 = st.columns(3)
    with c1:
        if pd.notnull(row.get("phone")) and row.get("phone"):
            phone_str = str(row["phone"]).replace("+", "").replace(".0", "")
            st.markdown(f"[📱 أرسل عبر واتساب مباشرة](https://wa.me/{phone_str}?text={encoded_msg})")
    with c2:
        if pd.notnull(row.get("email")) and row.get("email"):
            st.markdown(f"[📧 إرسال بريد إلكتروني رسمي](mailto:{row['email']}?subject={email_subject}&body={encoded_msg})")
    with c3:
        if pd.notnull(row.get("linkedin")):
            st.markdown(f"[🔗 فتح حساب المرشح في لينكدإن]({row['linkedin']})")
    return row


# ---------------------------------------------------------------------
# SECTION: CV file preview
# ---------------------------------------------------------------------
def render_cv_preview(row: pd.Series) -> None:
    st.markdown("---")
    st.subheader("📄 لوحة المعاينة الفورية لملف السيرة الذاتية")

    if not os.path.exists(row["file"]):
        st.info("الملف الأصلي لم يعد موجوداً على القرص.")
        return

    ext = os.path.splitext(row["file"])[1].lower()
    if ext == ".pdf":
        with open(row["file"], "rb") as f:
            st.download_button("📂 تحميل نسخة الـ PDF الحالية للملف", f, file_name=os.path.basename(row["file"]))
        try:
            with fitz.open(row["file"]) as doc:
                text = "\n\n".join(page.get_text() for page in doc)
            st.text_area("النصوص الكاملة المستخرجة من الـ PDF:", text, height=350)
        except Exception as exc:
            st.warning(f"تعذر استخراج محتويات الـ PDF: {exc}")
    elif ext in (".png", ".jpg", ".jpeg"):
        st.image(row["file"], caption=row["name"])
    elif ext == ".docx":
        # A .docx is a compressed archive — the old code opened it as a
        # plain text file and displayed unreadable symbols. Read it with
        # the proper Word library instead.
        try:
            document = docx.Document(row["file"])
            content = "\n".join(p.text for p in document.paragraphs)
            st.text_area("محتويات ملف الوورد:", content, height=350)
        except Exception as exc:
            st.warning(f"تعذر قراءة ملف الوورد: {exc}")
    elif ext == ".txt":
        with open(row["file"], "r", encoding="utf-8", errors="ignore") as f:
            st.text_area("محتويات الملف النصي:", f.read(), height=350)
    else:
        st.info("نوع وصيغة هذا الملف غير مدعومة للعرض المباشر.")
