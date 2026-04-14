"""View: Report Variables — edit \newcommand values in the active config file."""
import os
import re

import streamlit as st

from utils.content import load_file, save_file, page_header
from utils.config import VARIABLE_LABELS

_LATEX_SPECIAL = re.compile(r'[\\{}_^#%&$]')


def _sanitize_latex_value(val: str) -> str:
    """Escape LaTeX special characters in user-provided config values.
    These are plain-text fields (issue number, quarter names) — raw commands are never intended."""
    # Order matters: backslash first to avoid double-escaping
    for old, new in [
        ('\\', r'\textbackslash{}'),
        ('{', r'\{'), ('}', r'\}'),
        ('#', r'\#'), ('%', r'\%'),
        ('&', r'\&'), ('$', r'\$'),
        ('^', r'\^{}'), ('_', r'\_'),
        ('~', r'\~{}'),
    ]:
        val = val.replace(old, new)
    return val


def render(ctx):
    page_header(
        "⚙️", "Global Configuration",
        f"Step 2 of 5 · Active config file: <code>{ctx.active_config['config']}</code>",
        "#6366f1",
    )

    if not os.path.exists(ctx.CONFIG_FILE):
        st.error(f"{ctx.active_config['config']} not found.")
        return

    raw_config = load_file(ctx.CONFIG_FILE)

    if "[TODO]" in raw_config:
        st.warning("⚠️ This config file contains `[TODO]` placeholders. Fill them in before compiling.")

    pattern = re.compile(r"\\newcommand\{\\(\w+)\}\{(.*?)\}")
    matches = pattern.findall(raw_config)

    with st.form("config_form"):
        updates = {}
        cols = st.columns(2)
        for i, (key, val) in enumerate(matches):
            col = cols[i % 2]
            with col:
                _var_label = VARIABLE_LABELS.get(key, key)
                updates[key] = st.text_input(_var_label, value=val)

        if st.form_submit_button("💾 Update Variables", type="primary"):
            _risky = [k for k, v in updates.items() if _LATEX_SPECIAL.search(v)]
            if _risky:
                st.info(
                    "Special characters were auto-escaped in: "
                    + ", ".join(f"**{k}**" for k in _risky)
                    + ". This prevents LaTeX errors."
                )
            new_config = raw_config
            for key, val in updates.items():
                safe_val = _sanitize_latex_value(val) if _LATEX_SPECIAL.search(val) else val
                regex_replace = r"(\\newcommand\{\\" + key + r"\}\{)(.*?)(\})"
                new_config = re.sub(regex_replace, lambda m, v=safe_val: m.group(1) + v + m.group(3), new_config)
            save_file(ctx.CONFIG_FILE, new_config)
            st.toast("Updated!", icon="⚙️")
            st.rerun()

    st.divider()
    st.markdown('<div class="continue-btn-wrapper">', unsafe_allow_html=True)
    if st.button("→ Continue to Step 3: Chart Manager", type="primary",
                 use_container_width=True, key="next_step_variables"):
        st.session_state["_pending_nav"] = "📊 Chart Manager"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
