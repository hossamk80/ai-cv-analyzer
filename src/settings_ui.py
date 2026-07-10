# =====================================================================
# BLOCK: AI SETTINGS PAGE (src/settings_ui.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   The "⚙️ إعدادات الذكاء الاصطناعي" tab. From here you can:
#     - connect any AI provider (Anthropic, OpenAI, Google, or any
#       OpenAI-compatible server) with its API key and model name
#     - enable several providers AT THE SAME TIME
#     - edit, pause, test, or delete each one
#     - watch the token-consumption meter per provider
#
#   The storage and API-calling logic lives in ai_providers.py.
# =====================================================================

import altair as alt
import pandas as pd
import streamlit as st

from ai_providers import (
    PROVIDER_KINDS,
    add_provider,
    delete_provider,
    load_providers,
    reset_usage,
    test_provider,
    update_provider,
)
from i18n import t

BAR_COLOR = "#4C78A8"


def render_settings_page() -> None:
    st.subheader(t("settings_header"))
    st.caption(t("settings_hint"))

    _render_usage_meter()
    _render_add_form()
    _render_provider_list()


# ---------------------------------------------------------------------
# SECTION: token-consumption meter
# ---------------------------------------------------------------------
def _render_usage_meter() -> None:
    providers = load_providers()
    st.markdown(f"### {t('usage_header')}")
    if not providers:
        st.info(t("no_providers"))
        return

    total_calls = sum(p.get("usage", {}).get("calls", 0) for p in providers)
    total_in = sum(p.get("usage", {}).get("input_tokens", 0) for p in providers)
    total_out = sum(p.get("usage", {}).get("output_tokens", 0) for p in providers)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t("usage_calls"), f"{total_calls:,}")
    m2.metric(t("usage_input"), f"{total_in:,}")
    m3.metric(t("usage_output"), f"{total_out:,}")
    m4.metric(t("usage_total"), f"{total_in + total_out:,}")

    if total_in + total_out > 0:
        data = pd.DataFrame([
            {"provider": f"{p['name']} ({p['model']})",
             "tokens": p.get("usage", {}).get("input_tokens", 0)
                       + p.get("usage", {}).get("output_tokens", 0)}
            for p in providers
        ])
        bars = alt.Chart(data).mark_bar(cornerRadiusEnd=4, color=BAR_COLOR, height=20).encode(
            x=alt.X("tokens:Q", title=None),
            y=alt.Y("provider:N", title=None, sort="-x", axis=alt.Axis(labelLimit=260)),
        )
        labels = bars.mark_text(align="left", dx=4).encode(
            text=alt.Text("tokens:Q", format=","), color=alt.value("#444"))
        st.altair_chart(bars + labels, use_container_width=True)

    if st.button(t("reset_usage")):
        reset_usage()
        st.rerun()


# ---------------------------------------------------------------------
# SECTION: add a new provider
# ---------------------------------------------------------------------
def _render_add_form() -> None:
    st.markdown(f"### {t('add_provider')}")
    with st.form("add_provider_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input(t("provider_name"), placeholder="Claude / GPT / Gemini ...")
        kind = c2.selectbox(
            t("provider_kind"),
            options=list(PROVIDER_KINDS),
            format_func=lambda k: PROVIDER_KINDS[k]["label"],
        )
        c3, c4 = st.columns(2)
        model = c3.text_input(t("provider_model"), placeholder=t("provider_model_ph"))
        api_key = c4.text_input(t("provider_key"), type="password")
        base_url = st.text_input(t("provider_base_url"), placeholder="https://... " + t("provider_base_url_hint"))

        if st.form_submit_button(t("save"), type="primary"):
            if not name or not api_key:
                st.error(t("provider_required"))
            else:
                add_provider(
                    name=name, kind=kind,
                    model=model or PROVIDER_KINDS[kind]["default_model"],
                    api_key=api_key, base_url=base_url,
                )
                st.success(t("provider_added"))
                st.rerun()


# ---------------------------------------------------------------------
# SECTION: manage existing providers (edit / pause / test / delete)
# ---------------------------------------------------------------------
def _render_provider_list() -> None:
    providers = load_providers()
    if not providers:
        return
    st.markdown(f"### {t('providers_header')}")

    for provider in providers:
        status = "🟢" if provider.get("enabled") else "⏸️"
        title = f"{status} {provider['name']} — {PROVIDER_KINDS.get(provider['kind'], {}).get('label', provider['kind'])} — {provider['model']}"
        with st.expander(title):
            usage = provider.get("usage", {})
            st.caption(t(
                "provider_usage_line",
                calls=usage.get("calls", 0),
                tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            ))

            with st.form(f"edit_{provider['id']}"):
                c1, c2 = st.columns(2)
                name = c1.text_input(t("provider_name"), value=provider["name"])
                model = c2.text_input(t("provider_model"), value=provider["model"])
                c3, c4 = st.columns(2)
                api_key = c3.text_input(t("provider_key"), value=provider["api_key"], type="password")
                base_url = c4.text_input(t("provider_base_url"), value=provider.get("base_url", ""))
                enabled = st.toggle(t("provider_enabled"), value=provider.get("enabled", True))

                b1, b2, b3 = st.columns(3)
                if b1.form_submit_button(t("save"), type="primary"):
                    update_provider(provider["id"], {
                        "name": name, "model": model, "api_key": api_key,
                        "base_url": base_url, "enabled": enabled,
                    })
                    st.success(t("provider_saved"))
                    st.rerun()
                if b2.form_submit_button(t("test_connection")):
                    try:
                        with st.spinner("..."):
                            _, tin, tout = test_provider({
                                **provider, "name": name, "model": model,
                                "api_key": api_key, "base_url": base_url,
                            })
                        st.success(t("test_ok", tokens=tin + tout))
                    except Exception as exc:
                        st.error(t("test_fail", err=str(exc)[:300]))
                if b3.form_submit_button(t("delete")):
                    delete_provider(provider["id"])
                    st.rerun()
