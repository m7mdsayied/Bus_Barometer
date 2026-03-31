"""View: Chart Manager — upload/replace charts and static images."""
import os

import streamlit as st

from utils.auth import log_activity
from utils.config import CHART_LABELS, CHART_SECTIONS
from utils.content import page_header


@st.dialog("Delete Chart?")
def _dlg_delete_chart(filepath: str, filename: str):
    st.warning(f"Permanently delete **{filename}**? This cannot be undone.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Delete", type="primary", use_container_width=True):
            try:
                os.remove(filepath)
                log_activity("CHART_DELETED", detail=filename)
                st.toast(f"{filename} deleted.", icon="🗑️")
                st.rerun()
            except Exception as e:
                st.error(str(e))
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


def render(ctx):
    page_header(
        "📊", "Image &amp; Chart Management",
        "Step 3 of 5 · Upload or replace charts and static images used by the report.",
        "#f59e0b",
    )

    tab_charts, tab_static = st.tabs(["📈 Charts", "🖼️ Static Images (Shared)"])
    _can_edit = st.session_state.get("current_role") in ("admin", "editor")

    def render_image_manager(directory, filter_files=None, allow_delete=False):
        if not os.path.exists(directory):
            st.error("Directory not found.")
            return
        files = sorted([
            f for f in os.listdir(directory)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ])
        if filter_files is not None:
            files = [f for f in files if f.lower() in [x.lower() for x in filter_files]]
        if not files:
            st.info("No images in this selection.")
            return
        cols = st.columns(3)
        for idx, filename in enumerate(files):
            col = cols[idx % 3]
            filepath = os.path.join(directory, filename)
            with col:
                with st.container(border=True):
                    _hdr_c, _del_c = st.columns([5, 1])
                    with _hdr_c:
                        st.markdown(f"**{filename}**")
                        _desc = CHART_LABELS.get(filename.lower(), "")
                        if _desc:
                            st.caption(_desc)
                    with _del_c:
                        if allow_delete and _can_edit:
                            if st.button("🗑️", key=f"del_{directory}_{filename}",
                                         help=f"Delete {filename}", use_container_width=True):
                                _dlg_delete_chart(filepath, filename)
                    st.image(filepath, use_container_width=True)
                    if _can_edit:
                        _up_key = f"up_{directory}_{filename}"
                        uploaded = st.file_uploader(
                            f"Replace {filename}", type=["png", "jpg", "jpeg"],
                            key=_up_key,
                        )
                        if uploaded:
                            _fid = f"{uploaded.name}_{uploaded.size}"
                            if st.session_state.get(f"_saved_{_up_key}") != _fid:
                                with open(filepath, "wb") as f:
                                    f.write(uploaded.getbuffer())
                                log_activity("CHART_UPDATED", detail=filename)
                                st.session_state[f"_saved_{_up_key}"] = _fid
                                st.toast(f"✅ Updated {filename}")
                                st.rerun()

    with tab_charts:
        _f_col, _u_col = st.columns([3, 2])
        with _f_col:
            _sec_options = ["All Charts"] + list(CHART_SECTIONS.keys())
            _sec_filter = st.selectbox(
                "Filter by section", _sec_options,
                key="chart_section_filter", label_visibility="collapsed",
            )
        with _u_col:
            st.caption(f"`{os.path.basename(ctx.ACTIVE_CHARTS_DIR)}`")

        _filter_files = (
            CHART_SECTIONS.get(_sec_filter) if _sec_filter != "All Charts" else None
        )

        if _can_edit:
            with st.expander("➕ Upload New Chart", expanded=False):
                _new_name = st.text_input(
                    "Filename (e.g. ch26.png)", placeholder="ch26.png", key="new_chart_name"
                )
                _new_file = st.file_uploader(
                    "Select image", type=["png", "jpg", "jpeg"], key="new_chart_upload"
                )
                if st.button("Upload", type="primary", key="btn_upload_new_chart"):
                    if not _new_name.strip():
                        st.error("Filename is required.")
                    elif not _new_file:
                        st.error("Please select an image file.")
                    else:
                        _save_name = _new_name.strip()
                        if not any(_save_name.lower().endswith(e) for e in (".png", ".jpg", ".jpeg")):
                            _save_name += ".png"
                        _dest = os.path.join(ctx.ACTIVE_CHARTS_DIR, _save_name)
                        _fid = f"{_new_file.name}_{_new_file.size}"
                        if st.session_state.get("_saved_new_chart") != _fid:
                            with open(_dest, "wb") as f:
                                f.write(_new_file.getbuffer())
                            log_activity("CHART_UPLOADED", detail=_save_name)
                            st.session_state["_saved_new_chart"] = _fid
                            st.toast(f"✅ {_save_name} uploaded.", icon="📊")
                            st.rerun()

        render_image_manager(ctx.ACTIVE_CHARTS_DIR, filter_files=_filter_files, allow_delete=True)

    with tab_static:
        st.caption(f"`{os.path.basename(ctx.STATIC_IMG_DIR)}`")
        render_image_manager(ctx.STATIC_IMG_DIR, allow_delete=_can_edit)

    st.divider()
    if st.button("→ Continue to Step 4: Report Sections", type="primary", key="next_step_charts"):
        st.session_state["_pending_nav"] = "📝 Report Sections"
        st.rerun()
