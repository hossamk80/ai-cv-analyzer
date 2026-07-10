# =====================================================================
# BLOCK: UI COMPONENTS (src/ui_components.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   The reusable visual pieces of the dashboard. Each function draws
#   ONE section of the page. dashboard.py just calls them in order.
#
#   Every sentence comes from t("...") so the whole page follows the
#   visitor's language choice (Arabic / English — see i18n.py).
#   To change how a section LOOKS, edit the matching function here.
# =====================================================================

import os
import urllib.parse

import docx
import fitz
import pandas as pd
import streamlit as st

from i18n import t


# ---------------------------------------------------------------------
# SECTION: sidebar filters
# ---------------------------------------------------------------------
def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Draw the sidebar filters and return the filtered table."""
    with st.sidebar:
        st.header(t("filter_header"))
        city = st.selectbox(t("city"), options=[""] + sorted(df.location.dropna().unique()))
        nationality = st.selectbox(t("nationality"), options=[""] + sorted(df.nationality.dropna().unique()))
        match_level = st.multiselect(
            t("match_level_label"),
            options=sorted(df.match_level.unique()),
            default=sorted(df.match_level.unique()),
            format_func=t,  # shows ممتاز/Excellent per language
        )
        min_experience = st.slider(t("min_exp"), min_value=0, max_value=30, value=0)
        search_text = st.text_input(t("search"))

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
    col1.metric(t("total_cvs"), len(df))
    col2.metric(t("filtered_count"), len(filtered))
    col3.metric(t("avg_score"), f"{filtered.match_score.mean():.1f}%" if not filtered.empty else "—")

    columns_to_show = [
        "name", "email", "phone", "location", "nationality", "candidate_role",
        "experience_years", "languages", "match_score", "match_level",
    ]
    actual = [c for c in columns_to_show if c in filtered.columns]
    display = filtered[actual].sort_values("match_score", ascending=False).copy()
    # Turn the internal level codes into words in the visitor's language
    display["match_level"] = display["match_level"].map(t)

    if not display.empty:
        st.download_button(
            label=t("export_csv"),
            data=display.to_csv(index=False).encode("utf-8-sig"),
            file_name="candidates_report.csv",
            mime="text/csv",
        )
    st.dataframe(display, use_container_width=True)


# ---------------------------------------------------------------------
# SECTION: contact panel (WhatsApp / e-mail / LinkedIn)
# ---------------------------------------------------------------------
def render_contact_panel(filtered: pd.DataFrame) -> pd.Series:
    """Draw the candidate contact section; return the selected row."""
    st.markdown("---")
    st.header(t("contact_header"))

    selected_name = st.selectbox(t("choose_candidate"), filtered.name)
    row = filtered[filtered.name == selected_name].iloc[0]

    default_msg = t(
        "default_message",
        name=row["name"],
        role=row.get("candidate_role") or t("default_role"),
    )
    msg_template = st.text_area(t("message_label"), value=default_msg, height=120)
    subject_text = st.text_input(t("subject_label"), value=t("default_subject"))

    encoded_msg = urllib.parse.quote(msg_template)
    email_subject = urllib.parse.quote(subject_text)

    c1, c2, c3 = st.columns(3)
    with c1:
        if pd.notnull(row.get("phone")) and row.get("phone"):
            phone_str = str(row["phone"]).replace("+", "").replace(".0", "")
            st.markdown(f"[{t('whatsapp')}](https://wa.me/{phone_str}?text={encoded_msg})")
    with c2:
        if pd.notnull(row.get("email")) and row.get("email"):
            st.markdown(f"[{t('email_btn')}](mailto:{row['email']}?subject={email_subject}&body={encoded_msg})")
    with c3:
        if pd.notnull(row.get("linkedin")):
            st.markdown(f"[{t('linkedin')}]({row['linkedin']})")
    return row


# ---------------------------------------------------------------------
# SECTION: CV file preview
# ---------------------------------------------------------------------
def render_cv_preview(row: pd.Series) -> None:
    st.markdown("---")
    st.subheader(t("preview_header"))

    if not os.path.exists(row["file"]):
        st.info(t("file_missing"))
        return

    ext = os.path.splitext(row["file"])[1].lower()
    if ext == ".pdf":
        with open(row["file"], "rb") as f:
            st.download_button(t("pdf_download"), f, file_name=os.path.basename(row["file"]))
        try:
            with fitz.open(row["file"]) as doc:
                text = "\n\n".join(page.get_text() for page in doc)
            st.text_area(t("pdf_text"), text, height=350)
        except Exception as exc:
            st.warning(t("pdf_error", err=exc))
    elif ext in (".png", ".jpg", ".jpeg"):
        st.image(row["file"], caption=row["name"])
    elif ext == ".docx":
        # A .docx is a compressed archive — it must be read with the
        # Word library, never as a plain text file.
        try:
            document = docx.Document(row["file"])
            content = "\n".join(p.text for p in document.paragraphs)
            st.text_area(t("docx_content"), content, height=350)
        except Exception as exc:
            st.warning(t("docx_error", err=exc))
    elif ext == ".txt":
        with open(row["file"], "r", encoding="utf-8", errors="ignore") as f:
            st.text_area(t("txt_content"), f.read(), height=350)
    else:
        st.info(t("unsupported_preview"))
