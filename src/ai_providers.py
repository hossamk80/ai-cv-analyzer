# =====================================================================
# BLOCK: AI PROVIDERS ENGINE (src/ai_providers.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   The engine behind the AI settings page. It does three jobs:
#     1. STORE   - saves your AI providers (name, model, API key,
#                  enabled on/off) in a local file: ai_providers.json.
#                  That file is in .gitignore so your keys are NEVER
#                  uploaded to GitHub.
#     2. CALL    - sends a prompt to a provider and returns the answer.
#                  Supported kinds: Anthropic (Claude), OpenAI (GPT),
#                  Google (Gemini), or any OpenAI-compatible server.
#     3. MEASURE - records how many tokens every call consumed, per
#                  provider, so the settings page can show usage.
#
#   The settings SCREEN lives in settings_ui.py; this file is logic only.
# =====================================================================

import json
import os
import threading
import uuid

import requests

from config import AI_PROVIDERS_FILE

# The provider kinds the system knows how to talk to, with sensible
# default models. You can type any other model name in the settings.
PROVIDER_KINDS = {
    "anthropic": {"label": "Anthropic (Claude)", "default_model": "claude-opus-4-8"},
    "openai": {"label": "OpenAI (GPT)", "default_model": "gpt-4o"},
    "google": {"label": "Google (Gemini)", "default_model": "gemini-2.0-flash"},
    "custom": {"label": "OpenAI-compatible (custom URL)", "default_model": ""},
}

# Keep answers short: candidate assessments are a few paragraphs, and
# short outputs keep the recruiter's token bill predictable.
MAX_ANSWER_TOKENS = 2048

_lock = threading.Lock()


# ---------------------------------------------------------------------
# 1. STORE — load / save / add / update / delete providers
# ---------------------------------------------------------------------
def load_providers(path: str = None) -> list[dict]:
    path = path or AI_PROVIDERS_FILE
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_providers(providers: list[dict], path: str = None) -> None:
    path = path or AI_PROVIDERS_FILE
    with _lock, open(path, "w", encoding="utf-8") as f:
        json.dump(providers, f, ensure_ascii=False, indent=2)


def add_provider(name: str, kind: str, model: str, api_key: str,
                 base_url: str = "", path: str = None) -> dict:
    provider = {
        "id": uuid.uuid4().hex[:12],
        "name": name.strip(),
        "kind": kind,
        "model": model.strip(),
        "api_key": api_key.strip(),
        "base_url": base_url.strip(),
        "enabled": True,
        "usage": {"calls": 0, "input_tokens": 0, "output_tokens": 0},
    }
    providers = load_providers(path)
    providers.append(provider)
    save_providers(providers, path)
    return provider


def update_provider(provider_id: str, changes: dict, path: str = None) -> None:
    providers = load_providers(path)
    for provider in providers:
        if provider["id"] == provider_id:
            provider.update(changes)
    save_providers(providers, path)


def delete_provider(provider_id: str, path: str = None) -> None:
    providers = [p for p in load_providers(path) if p["id"] != provider_id]
    save_providers(providers, path)


def record_usage(provider_id: str, input_tokens: int, output_tokens: int,
                 path: str = None) -> None:
    """Add one call's token counts to the provider's running total."""
    providers = load_providers(path)
    for provider in providers:
        if provider["id"] == provider_id:
            usage = provider.setdefault(
                "usage", {"calls": 0, "input_tokens": 0, "output_tokens": 0})
            usage["calls"] += 1
            usage["input_tokens"] += int(input_tokens)
            usage["output_tokens"] += int(output_tokens)
    save_providers(providers, path)


def reset_usage(path: str = None) -> None:
    providers = load_providers(path)
    for provider in providers:
        provider["usage"] = {"calls": 0, "input_tokens": 0, "output_tokens": 0}
    save_providers(providers, path)


# ---------------------------------------------------------------------
# 2. CALL — send a prompt to a provider, return (text, tokens in, out)
# ---------------------------------------------------------------------
def call_provider(provider: dict, system_prompt: str, user_prompt: str) -> tuple[str, int, int]:
    """Ask one AI provider a question. Returns (answer, input_tokens,
    output_tokens). Raises an exception with a readable message on
    failure — the caller shows it to the user."""
    kind = provider.get("kind", "custom")
    if kind == "anthropic":
        return _call_anthropic(provider, system_prompt, user_prompt)
    if kind == "google":
        return _call_gemini(provider, system_prompt, user_prompt)
    # "openai" and "custom" both speak the OpenAI chat-completions API
    return _call_openai_compatible(provider, system_prompt, user_prompt)


def _call_anthropic(provider: dict, system_prompt: str, user_prompt: str):
    # Official Anthropic SDK. Thinking is left at the model's default.
    import anthropic

    client = anthropic.Anthropic(api_key=provider["api_key"])
    response = client.messages.create(
        model=provider["model"] or "claude-opus-4-8",
        max_tokens=MAX_ANSWER_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("The model declined to answer this request.")
    text = "".join(block.text for block in response.content if block.type == "text")
    return text, response.usage.input_tokens, response.usage.output_tokens


def _call_openai_compatible(provider: dict, system_prompt: str, user_prompt: str):
    base_url = (provider.get("base_url") or "https://api.openai.com/v1").rstrip("/")
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {provider['api_key']}"},
        json={
            "model": provider["model"],
            "max_tokens": MAX_ANSWER_TOKENS,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
    data = response.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return text, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)


def _call_gemini(provider: dict, system_prompt: str, user_prompt: str):
    model = provider["model"] or "gemini-2.0-flash"
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": provider["api_key"]},
        json={
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"maxOutputTokens": MAX_ANSWER_TOKENS},
        },
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
    data = response.json()
    text = "".join(
        part.get("text", "")
        for part in data["candidates"][0]["content"]["parts"]
    )
    meta = data.get("usageMetadata", {})
    return text, meta.get("promptTokenCount", 0), meta.get("candidatesTokenCount", 0)


def test_provider(provider: dict) -> tuple[str, int, int]:
    """Cheap connectivity check used by the settings page's Test button."""
    return call_provider(provider, "You are a helpful assistant.", "Reply with the single word: OK")
