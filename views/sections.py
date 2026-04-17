"""
View: Report Sections (slot-based content editor + live preview).
Dialogs: _dlg_add_section, _dlg_delete_section.
"""
import os

import streamlit as st
import streamlit.components.v1 as _stc

from utils.auth import log_activity
from utils.compiler import render_toolbar, generate_preview, display_pdf
from utils.content import (
    add_custom_section, delete_custom_section,
    extract_section_items, extract_slots, get_all_section_slots,
    get_slot_label, load_custom_sections, load_file, save_file, save_slot,
    reset_slot,
    append_text_slot_to_section, append_chart_slot_to_section,
    remove_text_slot_from_section, remove_chart_slot_from_section,
    page_header,
)


# ── Dialogs ───────────────────────────────────────────────────────────────────
@st.dialog("Add New Section")
def _dlg_add_section(lang: str):
    if st.session_state.get("current_role") not in ("admin", "editor"):
        st.error("🔒 Access denied.")
        st.stop()
    _type_icons = {"text": "📝", "chart": "📊", "mixed": "📝+📊", "table": "📋"}
    st.markdown("Create a new custom section for this report.")
    _title = st.text_input(
        "Section Title", placeholder="e.g. Special Analysis", key="dlg_sec_title"
    )
    _type = st.radio(
        "Section Type",
        list(_type_icons.keys()),
        format_func=lambda t: f"{_type_icons[t]} {t.capitalize()}",
        horizontal=True,
        key="dlg_sec_type",
    )
    st.caption({
        "text":  "Text paragraphs only — no images.",
        "chart": "Single chart/image — no text slots.",
        "mixed": "Introduction + chart + analysis paragraphs.",
        "table": "Table image with caption slot.",
    }[_type])
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Create Section", type="primary", use_container_width=True):
            if not _title.strip():
                st.error("Title cannot be empty.")
            else:
                _ok, _msg = add_custom_section(lang, _title.strip(), _type)
                if _ok:
                    log_activity("SECTION_CREATED", detail=f"'{_title}' ({_type}, {lang})")
                    st.toast(f"Section '{_title}' created!", icon="✅")
                    st.rerun()
                else:
                    st.error(_msg)
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Remove Text Block?")
def _dlg_remove_text_block(file_path: str, slot_id: str):
    if st.session_state.get("current_role") not in ("admin", "editor"):
        st.error("🔒 Access denied.")
        st.stop()
    st.warning("Permanently remove this text block? Unsaved edits will be lost.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Remove", type="primary", use_container_width=True):
            remove_text_slot_from_section(file_path, slot_id)
            st.rerun()
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Delete Custom Section?")
def _dlg_delete_section(lang: str, sec_id: str, sec_title: str):
    if st.session_state.get("current_role") not in ("admin", "editor"):
        st.error("🔒 Access denied.")
        st.stop()
    st.warning(
        f"Remove **{sec_title}** from the section list?\n\n"
        "The `.tex` file is kept on disk — only the registration is removed."
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Remove", type="primary", use_container_width=True):
            delete_custom_section(lang, sec_id)
            log_activity("SECTION_DELETED", detail=f"'{sec_title}' ({lang})")
            st.toast(f"Section '{sec_title}' removed.", icon="🗑️")
            st.rerun()
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


# ── Render ────────────────────────────────────────────────────────────────────
def render(ctx):
    page_header("📝", "Content Editor &amp; Preview",
                "Step 4 of 5 · Edit slot content and preview compiled PDF sections.", "#1FBACF")

    if ctx.is_arabic:
        st.markdown(
            "<style>textarea { direction: rtl !important; text-align: right !important; }</style>",
            unsafe_allow_html=True,
        )

    st.info(
        "**LaTeX tip:** Use `\\\\textbf{bold}`, `\\\\textit{italic}`, "
        "`\\\\textsuperscript{1}`. "
        "**Avoid:** bare `%` (use `\\\\%`), unmatched `{` or `}`, "
        "bare `\\\\` at end of a line, bare `$` or `&`.",
        icon="ℹ️",
    )

    section_keys = list(ctx.SECTION_MAP.keys())
    _cs_data = load_custom_sections()
    _cs_lang_key = "ar" if ctx.is_arabic else "en"
    _custom_ids = {s["title"]: s["id"] for s in _cs_data.get(_cs_lang_key, [])}

    _sel_col, _add_col = st.columns([5, 1])
    with _sel_col:
        current_section_name = st.selectbox(
            "Select Section", section_keys,
            label_visibility="collapsed", key="section_selectbox",
        )
    with _add_col:
        if st.session_state.get("current_role") in ("admin", "editor"):
            if st.button("➕", use_container_width=True,
                         help="Add a new custom section", key="btn_add_section"):
                _dlg_add_section(st.session_state["language"])

    # Store current section name for sidebar factory reset
    st.session_state["_current_section_name"] = current_section_name

    if current_section_name in _custom_ids:
        _cs_id = _custom_ids[current_section_name]
        if st.session_state.get("current_role") in ("admin", "editor"):
            if st.button(f"🗑️ Remove '{current_section_name}'",
                         key="btn_del_section", use_container_width=False):
                _dlg_delete_section(st.session_state["language"], _cs_id, current_section_name)

    if "last_section" not in st.session_state:
        st.session_state["last_section"] = current_section_name
    if st.session_state["last_section"] != current_section_name:
        st.session_state["last_section"] = current_section_name
        st.session_state["active_preview_pdf"] = None

    current_file_path = os.path.join(ctx.BASE_DIR, ctx.SECTION_MAP[current_section_name])
    if not os.path.exists(current_file_path):
        save_file(current_file_path, "% New Section")

    raw_content = load_file(current_file_path)
    slots = extract_slots(raw_content)
    is_slot_based = len(slots) > 0

    section_slots = get_all_section_slots(current_file_path) if is_slot_based else []
    _total_slots = len(section_slots)
    _edited_slots = sum(1 for _, _, ov, _ in section_slots if ov)

    _engine_label = "Slot Engine" if is_slot_based else "Legacy"
    _sep = '<span style="color:#1FBACF; margin:0 0.4rem;">›</span>'
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap; margin-bottom:0.5rem;">
        <span style="background:var(--bg-secondary,#334155); padding:6px 14px; border-radius:50px;
                     border:1px solid #475569; font-size:0.85rem;">
            <b style="color:#1FBACF;">{st.session_state['language']}</b>
            {_sep}<code>{os.path.basename(current_file_path)}</code>
            {_sep}<b>{_engine_label}</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

    if is_slot_based and _total_slots > 0:
        _pct = int((_edited_slots / _total_slots) * 100)
        _bar_col = "#22c55e" if _pct == 100 else "#1FBACF"
        st.markdown(
            f"<div style='margin:8px 0 14px 0;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:baseline;"
            f"margin-bottom:5px;'>"
            f"<span style='font-size:0.78rem;color:#94a3b8;font-weight:500;'>Slots customized</span>"
            f"<span style='font-size:0.78rem;font-weight:700;color:{_bar_col};'>"
            f"{_edited_slots} / {_total_slots}</span></div>"
            f"<div style='height:5px;background:rgba(255,255,255,0.07);border-radius:99px;overflow:hidden;'>"
            f"<div style='height:100%;width:{_pct}%;background:{_bar_col};"
            f"border-radius:99px;transition:width 0.4s ease;'></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    if is_slot_based and section_slots:
        _lang_key = st.session_state["language"]
        _pending_changes = any(
            st.session_state.get(f"slot_{_lang_key}_{sid}") != cur
            for sid, cur, _, _ in section_slots
            if f"slot_{_lang_key}_{sid}" in st.session_state
        )
        if _pending_changes:
            st.warning("⚠️ You have unsaved changes — press **Save All Changes** before switching sections.")

    st.divider()
    st.markdown("""
<style>
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:last-child {
    align-items: flex-start !important;
}
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:last-child
  > div[data-testid="stColumn"]:last-child,
section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:last-child
  > div[data-testid="stVerticalBlockBorderWrapper"]:last-child {
    position: sticky !important;
    top: 3.5rem;
    max-height: calc(100vh - 4rem);
    overflow-y: auto;
    align-self: flex-start;
}
</style>
""", unsafe_allow_html=True)
    
    st.markdown("""
<style>
/* Make the image take up 100% of the column without constraints */
[data-testid="stImage"] {
    width: 100% !important;
}
[data-testid="stImage"] img {
    width: 100% !important;
    max-width: none !important;
    border-radius: 6px;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
}
</style>
""", unsafe_allow_html=True)


    col_editor, col_preview = st.columns([3, 2])

    # ── Editor ────────────────────────────────────────────────────────────────
    with col_editor:
        st.markdown("**Edit Content**")

        if is_slot_based:
            if st.session_state.get("current_role") in ("admin", "editor"):
                with st.expander("🛠️ LaTeX Quick Tools", expanded=False):
                    render_toolbar()

            _is_custom_sec = current_section_name in _custom_ids
            _role = st.session_state.get("current_role", "viewer")
            _sec_items = extract_section_items(raw_content, ctx.ACTIVE_CHARTS_DIR)
            _text_slot_ids = []

            for _item in _sec_items:
                if _item["type"] == "text":
                    _sid = _item["slot_id"]
                    _cur = _item["current_text"]
                    _ov  = _item["is_overridden"]
                    _text_slot_ids.append(_sid)

                    with st.container(border=True):
                        _lc, _bc = st.columns([4, 1])
                        with _lc:
                            st.markdown(f"**{get_slot_label(_sid)}**")
                        with _bc:
                            if _ov:
                                st.markdown(
                                    "<span title='Override saved — click Save All Changes to update' "
                                    "style='background:#CF34A9;color:white;padding:3px 10px;"
                                    "border-radius:50px;font-size:0.75em;font-weight:600;"
                                    "cursor:help;'>✏️ Edited</span>",
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(
                                    "<span title='Showing default content' "
                                    "style='color:#94a3b8;padding:3px 10px;"
                                    "border-radius:50px;font-size:0.75em;border:1px solid #475569;"
                                    "cursor:help;'>📄 Default</span>",
                                    unsafe_allow_html=True,
                                )
                        _h = max(150, min(400, len(_cur) // 2))
                        st.text_area(
                            get_slot_label(_sid), value=_cur, height=int(_h),
                            label_visibility="collapsed",
                            key=f"slot_{st.session_state['language']}_{_sid}",
                        )
                        if _ov:
                            st.checkbox("↩️ Reset to default", key=f"reset_{_sid}", value=False)
                        if _is_custom_sec and _role in ("admin", "editor"):
                            if st.button("🗑️ Remove block", key=f"rm_{_sid}",
                                         help="Remove this text block"):
                                _dlg_remove_text_block(current_file_path, _sid)

                else:  # chart
                    _fn = _item["filename"]
                    _fp = _item["filepath"]
                    with st.container(border=True):
                        from utils.config import CHART_LABELS
                        _ch_label = CHART_LABELS.get(_fn.lower(), _fn)
                        st.markdown(f"📊 **{_ch_label}** &nbsp; `{_fn}`", unsafe_allow_html=True)
                        if _item["exists"]:
                            st.image(_fp, use_container_width=True)
                        else:
                            st.warning(f"`{_fn}` not uploaded yet — use the **Chart Manager** (Step 3) to upload it.")
                        if _is_custom_sec and _role in ("admin", "editor"):
                            if st.button("🗑️ Remove chart",
                                         key=f"rm_ch_{_fn}_{current_section_name}",
                                         help="Remove this chart placeholder"):
                                remove_chart_slot_from_section(current_file_path, _fn)
                                st.rerun()

            # Add-block toolbar (custom sections only)
            if _is_custom_sec and _role in ("admin", "editor"):
                st.markdown("---")
                _ab1, _ab2 = st.columns(2)
                with _ab1:
                    if st.button("➕ Add Text Block", key="btn_add_text_block", use_container_width=True):
                        append_text_slot_to_section(current_file_path)
                        st.rerun()
                with _ab2:
                    if st.button("➕ Add Chart Block", key="btn_add_chart_block", use_container_width=True):
                        append_chart_slot_to_section(current_file_path)
                        st.rerun()

            # Save all text edits
            st.markdown("")
            save_clicked = st.button(
                "💾 Save All Changes", type="primary", use_container_width=True,
                key=f"save_slots_{current_section_name}",
            )
            if save_clicked:
                default_map = {sid: dtxt for sid, dtxt in slots}
                saved_count = reset_count = 0

                for _sid in _text_slot_ids:
                    _key = f"slot_{st.session_state['language']}_{_sid}"
                    edited_text = st.session_state.get(_key, "")
                    if st.session_state.get(f"reset_{_sid}", False):
                        reset_slot(_sid)
                        reset_count += 1
                    else:
                        default = default_map.get(_sid, "")
                        if edited_text.strip() != default.strip():
                            save_slot(_sid, edited_text)
                            saved_count += 1
                        else:
                            reset_slot(_sid)

                if saved_count > 0 or reset_count > 0:
                    parts = []
                    if saved_count > 0:
                        parts.append(f"{saved_count} saved")
                    if reset_count > 0:
                        parts.append(f"{reset_count} reset")
                    log_activity("CONTENT_EDIT", detail=f"{current_section_name}: {', '.join(parts)}")
                    st.toast(f"✅ {current_section_name}: {', '.join(parts)}")
                    st.rerun()
                else:
                    st.info(f"No changes detected in {current_section_name}.")


    # ── Preview ───────────────────────────────────────────────────────────────
    with col_preview:
        st.markdown("**Live Preview**")

        # Section-scoped keys so preview survives slider reruns but clears on section change
        _pdf_key      = f"preview_pdf_{current_section_name}"
        _err_key      = f"preview_err_{current_section_name}"
        _compile_key  = f"preview_compiling_{current_section_name}"

        _is_compiling = st.session_state.get(_compile_key, False)
        if st.button(
            "⏳ Compiling…" if _is_compiling else "👁️ Generate Preview",
            use_container_width=True, type="primary",
            key=f"preview_{current_section_name}",
            disabled=_is_compiling,
        ):
            st.session_state[_compile_key] = True
            preview_content = load_file(current_file_path)
            with st.status("Compiling Preview...", expanded=True) as _status:
                pdf_path, error_msg = generate_preview(
                    preview_content,
                    ctx.PREAMBLE_FILE,
                    ctx.active_config["config"],
                    ctx.BASE_DIR,
                )
                if pdf_path and os.path.exists(pdf_path):
                    st.session_state[_pdf_key] = pdf_path
                    st.session_state[_err_key] = None
                    _status.update(label="Ready!", state="complete", expanded=False)
                else:
                    st.session_state[_pdf_key] = None
                    st.session_state[_err_key] = error_msg
                    _status.update(label="Failed", state="error")
            st.session_state[_compile_key] = False

        # Always render from stored state — survives page-slider reruns
        _stored_pdf = st.session_state.get(_pdf_key)
        if _stored_pdf and os.path.exists(_stored_pdf):
            display_pdf(_stored_pdf)
        elif st.session_state.get(_err_key):
            st.error("⚠️ LaTeX Compilation Error")
            with st.expander("Error Details", expanded=True):
                st.code(st.session_state[_err_key], language="tex")
        else:
            st.info("Click Preview to compile this section.")

    # JS: enforce sticky preview column after Streamlit re-renders
    _stc.html("""
<script>
(function() {
  function applySticky() {
    try {
      var doc = window.frameElement ? window.frameElement.ownerDocument : null;
      if (!doc) return;
      var blocks = doc.querySelectorAll('[data-testid="stHorizontalBlock"]');
      if (!blocks.length) return;
      var last = blocks[blocks.length - 1];
      last.style.alignItems = 'flex-start';
      var cols = last.querySelectorAll(':scope > div');
      if (cols.length >= 2) {
        var preview = cols[cols.length - 1];
        preview.style.position = 'sticky';
        preview.style.top = '3.5rem';
        preview.style.maxHeight = 'calc(100vh - 4rem)';
        preview.style.overflowY = 'auto';
        preview.style.alignSelf = 'flex-start';
      }
    } catch(e) {}
  }
  applySticky();
  setTimeout(applySticky, 200);
  setTimeout(applySticky, 800);
})();
</script>
""", height=0)

    if st.session_state.get("current_role") in ("admin", "editor"):
        st.divider()
        st.markdown('<div class="continue-btn-wrapper">', unsafe_allow_html=True)
        if st.button("→ Continue to Step 5: Finalize & Publish", type="primary",
                     use_container_width=True, key="next_step_sections"):
            st.session_state["_pending_nav"] = "🚀 Finalize & Publish"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
