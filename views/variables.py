"""View: Report Variables — edit \newcommand values in the active config file."""
import re

import streamlit as st

from utils.content import load_file, save_file, page_header
from utils.config import VARIABLE_LABELS


def render(ctx):
    page_header(
        "⚙️", "Global Configuration",
        f"Step 2 of 5 · Active config file: <code>{ctx.active_config['config']}</code>",
        "#6366f1",
    )

    import os
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
            new_config = raw_config
            for key, val in updates.items():
                safe_val = val.replace("\\", "\\\\")
                regex_replace = r"(\\newcommand\{\\" + key + r"\}\{)(.*?)(\})"
                new_config = re.sub(regex_replace, r"\g<1>" + safe_val + r"\g<3>", new_config)
            save_file(ctx.CONFIG_FILE, new_config)
            st.toast("Updated!", icon="⚙️")
            st.rerun()

    st.divider()
    if st.button("→ Continue to Step 3: Chart Manager", type="primary", key="next_step_variables"):
        st.session_state["_pending_nav"] = "📊 Chart Manager"
        st.rerun()
