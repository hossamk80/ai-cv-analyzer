# =====================================================================
# BLOCK: ANALYTICS (src/analytics_ui.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   Two sections of the page:
#     1. render_analytics_dashboard(...)  - charts about the whole
#        FILTERED candidate pool (levels, top skills, cities, ranking)
#     2. render_candidate_analysis(...)   - a written + visual summary
#        of ONE selected candidate: their rank, how they compare to
#        the pool, and exactly which job requirements they match/miss.
#
# DESIGN RULES USED (do not "improve" them away):
#   - Quantity charts use ONE blue hue — never a rainbow.
#   - Match levels use reserved status colors (green/amber/red) and
#     are ALWAYS accompanied by their text label, never color alone.
# =====================================================================

import altair as alt
import pandas as pd
import streamlit as st

from i18n import t
from matching import explain_match

# One hue for "how much" charts; status colors for match levels.
BAR_COLOR = "#4C78A8"
LEVEL_COLORS = {"excellent": "#2E7D32", "fair": "#B45309", "poor": "#C62828"}


# ---------------------------------------------------------------------
# SECTION 1: pool analytics dashboard (four charts, 2 x 2)
# ---------------------------------------------------------------------
def render_analytics_dashboard(filtered: pd.DataFrame) -> None:
    if filtered.empty:
        return
    st.markdown("---")
    st.subheader(t("analytics_header"))

    top = st.columns(2)
    with top[0]:
        _chart_match_levels(filtered)
    with top[1]:
        _chart_top_candidates(filtered)

    bottom = st.columns(2)
    with bottom[0]:
        _chart_top_skills(filtered)
    with bottom[1]:
        _chart_cities(filtered)


def _chart_match_levels(df: pd.DataFrame) -> None:
    st.markdown(f"**{t('chart_levels')}**")
    counts = df.match_level.value_counts()
    data = pd.DataFrame({
        "level": [t(lvl) for lvl in ("excellent", "fair", "poor") if lvl in counts],
        "count": [int(counts[lvl]) for lvl in ("excellent", "fair", "poor") if lvl in counts],
        "color": [LEVEL_COLORS[lvl] for lvl in ("excellent", "fair", "poor") if lvl in counts],
    })
    bars = alt.Chart(data).mark_bar(cornerRadiusEnd=4, height=26).encode(
        x=alt.X("count:Q", title=None, axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("level:N", title=None, sort=None),
        color=alt.Color("color:N", scale=None, legend=None),
    )
    labels = bars.mark_text(align="left", dx=4).encode(text="count:Q", color=alt.value("#444"))
    st.altair_chart(bars + labels, use_container_width=True)


def _chart_top_candidates(df: pd.DataFrame) -> None:
    st.markdown(f"**{t('chart_top_candidates')}**")
    data = df.nlargest(10, "match_score")[["name", "match_score"]]
    bars = alt.Chart(data).mark_bar(cornerRadiusEnd=4, color=BAR_COLOR, height=18).encode(
        x=alt.X("match_score:Q", title=None),
        y=alt.Y("name:N", title=None, sort="-x", axis=alt.Axis(labelLimit=220)),
        tooltip=["name", "match_score"],
    )
    labels = bars.mark_text(align="left", dx=4).encode(
        text=alt.Text("match_score:Q", format=".1f"), color=alt.value("#444"))
    st.altair_chart(bars + labels, use_container_width=True)


def _chart_top_skills(df: pd.DataFrame) -> None:
    st.markdown(f"**{t('chart_skills')}**")
    all_skills: list[str] = []
    for cell in df.skills.dropna():
        all_skills.extend(s.strip() for s in str(cell).split(" / ") if s.strip())
    if not all_skills:
        st.caption(t("no_chart_data"))
        return
    counts = pd.Series(all_skills).value_counts().head(10).reset_index()
    counts.columns = ["skill", "count"]
    bars = alt.Chart(counts).mark_bar(cornerRadiusEnd=4, color=BAR_COLOR, height=18).encode(
        x=alt.X("count:Q", title=None, axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("skill:N", title=None, sort="-x", axis=alt.Axis(labelLimit=220)),
        tooltip=["skill", "count"],
    )
    labels = bars.mark_text(align="left", dx=4).encode(text="count:Q", color=alt.value("#444"))
    st.altair_chart(bars + labels, use_container_width=True)


def _chart_cities(df: pd.DataFrame) -> None:
    st.markdown(f"**{t('chart_cities')}**")
    cities = df.location[df.location != ""].dropna()
    if cities.empty:
        st.caption(t("no_chart_data"))
        return
    counts = cities.value_counts().head(10).reset_index()
    counts.columns = ["city", "count"]
    bars = alt.Chart(counts).mark_bar(cornerRadiusEnd=4, color=BAR_COLOR, height=18).encode(
        x=alt.X("count:Q", title=None, axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("city:N", title=None, sort="-x", axis=alt.Axis(labelLimit=220)),
        tooltip=["city", "count"],
    )
    labels = bars.mark_text(align="left", dx=4).encode(text="count:Q", color=alt.value("#444"))
    st.altair_chart(bars + labels, use_container_width=True)


# ---------------------------------------------------------------------
# SECTION 2: analytical summary for ONE selected candidate
# ---------------------------------------------------------------------
def render_candidate_analysis(row: pd.Series, filtered: pd.DataFrame, matching_text: str) -> None:
    st.markdown("---")
    st.subheader(t("analysis_header", name=row["name"]))

    # --- headline numbers: rank, score, distance from pool average ---
    ranked = filtered.sort_values("match_score", ascending=False).reset_index(drop=True)
    rank = int(ranked.index[ranked.name == row["name"]][0]) + 1
    pool_avg = float(filtered.match_score.mean())
    delta = float(row["match_score"]) - pool_avg

    m1, m2, m3 = st.columns(3)
    m1.metric(t("analysis_rank"), f"{rank} / {len(filtered)}")
    m2.metric(t("analysis_score"), f"{row['match_score']:.1f}%", delta=f"{delta:+.1f}%")
    m3.metric(t("analysis_level"), t(row["match_level"]))

    # --- score in context: candidate vs pool average vs best ---
    best = float(filtered.match_score.max())
    context = pd.DataFrame({
        "label": [t("analysis_this_candidate"), t("analysis_pool_avg"), t("analysis_pool_best")],
        "score": [float(row["match_score"]), pool_avg, best],
    })
    bars = alt.Chart(context).mark_bar(cornerRadiusEnd=4, color=BAR_COLOR, height=22).encode(
        x=alt.X("score:Q", title=None),
        y=alt.Y("label:N", title=None, sort=None, axis=alt.Axis(labelLimit=220)),
    )
    labels = bars.mark_text(align="left", dx=4).encode(
        text=alt.Text("score:Q", format=".1f"), color=alt.value("#444"))
    st.altair_chart(bars + labels, use_container_width=True)

    # --- which job requirements this CV matches / misses -------------
    matched, missing = explain_match(str(row.get("cv_text", "")), matching_text)
    c_ok, c_miss = st.columns(2)
    with c_ok:
        st.markdown(f"**✅ {t('analysis_matched')} ({len(matched)})**")
        st.success("، ".join(matched) if matched else t("analysis_none"))
    with c_miss:
        st.markdown(f"**❌ {t('analysis_missing')} ({len(missing)})**")
        st.error("، ".join(missing) if missing else t("analysis_none"))

    # --- what the CV itself offers -----------------------------------
    facts = []
    if row.get("education"):
        facts.append(f"🎓 {t('education_filter')}: {t(row['education'])}")
    if row.get("experience_years") and str(row["experience_years"]) not in ("", "nan"):
        facts.append(f"💼 {t('min_exp')}: {row['experience_years']}")
    if row.get("certifications"):
        facts.append(f"📜 {t('certs_filter')}: {row['certifications']}")
    if row.get("skills"):
        facts.append(f"🛠️ {t('skills_filter')}: {row['skills']}")
    if row.get("languages"):
        facts.append(f"🗣️ {t('analysis_languages')}: {row['languages']}")
    if facts:
        st.markdown(f"**{t('analysis_profile')}**")
        st.info("\n\n".join(facts))
