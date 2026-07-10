# =====================================================================
# BLOCK: AI CANDIDATE INSIGHTS (src/ai_insights.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   The "🤖 تحليل بالذكاء الاصطناعي" section under the candidate summary.
#   One click sends the job requirements + the selected candidate's CV
#   to EVERY provider you enabled in the settings page, shows their
#   assessments side by side, and adds the consumed tokens to the
#   usage meter.
# =====================================================================

import streamlit as st

from ai_providers import call_provider, load_providers, record_usage
from i18n import current_lang, t

# CVs can be long; cap what we send so one click stays cheap.
MAX_CV_CHARS = 8000


def _build_prompts(row, matching_text: str) -> tuple[str, str]:
    answer_language = "Arabic" if current_lang() == "ar" else "English"
    system_prompt = (
        "You are an expert technical recruiter. Assess how well a candidate's CV "
        "matches a job's requirements. Be honest and specific. "
        f"Answer in {answer_language}, concisely, using this structure: "
        "1) Fit score out of 10. 2) Top strengths for THIS job. "
        "3) Gaps or missing requirements. 4) Hire recommendation in one sentence."
    )
    user_prompt = (
        f"JOB REQUIREMENTS:\n{matching_text}\n\n"
        f"CANDIDATE CV ({row['name']}):\n{str(row.get('cv_text', ''))[:MAX_CV_CHARS]}"
    )
    return system_prompt, user_prompt


def render_ai_insights(row, matching_text: str) -> None:
    st.markdown("---")
    st.subheader(t("ai_header"))

    enabled = [p for p in load_providers() if p.get("enabled")]
    if not enabled:
        st.info(t("ai_no_providers"))
        return

    st.caption(t("ai_hint", n=len(enabled)))
    if not st.button(t("ai_run", name=row["name"]), type="primary"):
        return

    system_prompt, user_prompt = _build_prompts(row, matching_text)
    columns = st.columns(len(enabled))
    for column, provider in zip(columns, enabled):
        with column:
            st.markdown(f"**🤖 {provider['name']}** — `{provider['model']}`")
            try:
                with st.spinner(t("ai_working")):
                    text, tokens_in, tokens_out = call_provider(
                        provider, system_prompt, user_prompt)
                record_usage(provider["id"], tokens_in, tokens_out)
                st.markdown(text)
                st.caption(t("ai_tokens", n=tokens_in + tokens_out))
            except Exception as exc:
                st.error(t("ai_error", err=str(exc)[:300]))
