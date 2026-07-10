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
# SECTION: filters (shown at the TOP of the page, above the results)
# ---------------------------------------------------------------------
def _options_from_joined(series: pd.Series) -> list[str]:
    """Turn a column like 'Cisco / Linux' into a sorted option list."""
    values = set()
    for cell in series.dropna():
        for part in str(cell).split(" / "):
            if part.strip():
                values.add(part.strip())
    return sorted(values)


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Draw the filter panel at the top of the page; return the
    filtered table. Every dropdown allows MULTIPLE selections.

    Behaviour: city / nationality / education / match level keep a
    candidate when they match ANY selected value; skills and
    certifications require ALL selected values (a recruiter who picks
    "Cisco" and "Linux" wants candidates who have both).
    """
    st.markdown("---")
    st.subheader(t("filter_header"))

    row1 = st.columns(4)
    city = row1[0].multiselect(t("city"), options=sorted(df.location.dropna()[df.location != ""].unique()))
    nationality = row1[1].multiselect(t("nationality"), options=sorted(df.nationality.dropna()[df.nationality != ""].unique()))
    education = row1[2].multiselect(
        t("education_filter"),
        options=[e for e in ("phd", "master", "bachelor", "diploma", "highschool")
                 if e in set(df.education.dropna().unique())],
        format_func=t,
    )
    match_level = row1[3].multiselect(
        t("match_level_label"),
        options=[l for l in ("excellent", "fair", "poor") if l in set(df.match_level.unique())],
        format_func=t,
    )

    row2 = st.columns(4)
    skills = row2[0].multiselect(t("skills_filter"), options=_options_from_joined(df.skills))
    certifications = row2[1].multiselect(t("certs_filter"), options=_options_from_joined(df.certifications))
    min_experience = row2[2].slider(t("min_exp"), min_value=0, max_value=30, value=0)
    search_text = row2[3].text_input(t("search"))

    filtered = df.copy()
    if city:
        filtered = filtered[filtered.location.isin(city)]
    if nationality:
        filtered = filtered[filtered.nationality.isin(nationality)]
    if education:
        filtered = filtered[filtered.education.isin(education)]
    if match_level:
        filtered = filtered[filtered.match_level.isin(match_level)]
    for skill in skills:
        filtered = filtered[filtered.skills.str.contains(skill, case=False, na=False, regex=False)]
    for cert in certifications:
        filtered = filtered[filtered.certifications.str.contains(cert, case=False, na=False, regex=False)]
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
        "experience_years", "education", "certifications", "skills",
        "languages", "match_score", "match_level",
    ]
    actual = [c for c in columns_to_show if c in filtered.columns]
    display = filtered[actual].sort_values("match_score", ascending=False).copy()
    # Turn the internal codes into words in the visitor's language
    display["match_level"] = display["match_level"].map(t)
    display["education"] = display["education"].map(lambda e: t(e) if e else "")
    if "experience_years" in display.columns:
        # show a blank cell instead of "None" when no experience found
        display["experience_years"] = display["experience_years"].map(
            lambda v: "" if pd.isna(v) else str(int(v)) if str(v).replace(".0", "").isdigit() else str(v)
        )

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
