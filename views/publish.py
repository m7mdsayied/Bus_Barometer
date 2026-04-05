"""View: Finalize & Publish — compile full PDF and manage report archive."""
import os
import re
import shutil

import streamlit as st

import issue_manager as _im
from utils import storage as _storage
from utils.auth import log_activity
from utils.compiler import _clear_miktex_issues, _get_miktex_env
from utils.content import load_file, page_header
from utils.config import BASE_DIR

import subprocess


def render(ctx):
    target_main = ctx.active_config["main"]
    page_header(
        "🚀", "Compile Final Report",
        f"Step 5 of 5 · Target: <code>{target_main}</code> · Engine: XeLaTeX "
        f"({st.session_state['language']} fonts &amp; layout)",
        "#10b981",
    )

    REPORTS_DIR = os.path.join(ctx.BASE_DIR, "reports")

    # Derive default filename from issue number in config
    _cfg_raw = load_file(ctx.CONFIG_FILE)
    _m = re.search(r"\\newcommand\{\\IssueNumber\}\{([^}]+)\}", _cfg_raw)
    _issue_num = _m.group(1) if _m else "XX"
    _default_fname = f"Issue-{_issue_num}-{'Arabic' if ctx.is_arabic else 'English'}.pdf"

    _fname_input = st.text_input(
        "Output filename",
        value=st.session_state.get("_finalize_fname", _default_fname),
        placeholder="Issue-77-English.pdf",
        key="_finalize_fname",
    )
    if not _fname_input.endswith(".pdf"):
        _fname_input = _fname_input + ".pdf"

    c1, c2 = st.columns([2, 1])

    with c1:
        if st.button("Generate Full PDF", type="primary"):
            with st.status("Processing...", expanded=True) as status:
                try:
                    cmd = ["xelatex", "-interaction=nonstopmode", target_main]

                    st.write("Running xelatex (Pass 1)...")
                    _clear_miktex_issues()
                    subprocess.run(cmd, cwd=ctx.BASE_DIR, stdout=subprocess.DEVNULL,
                                   env=_get_miktex_env())

                    st.write("Running xelatex (Pass 2 for ToC)...")
                    _clear_miktex_issues()
                    subprocess.run(cmd, cwd=ctx.BASE_DIR, stdout=subprocess.DEVNULL,
                                   env=_get_miktex_env())

                    expected_pdf = target_main.replace(".tex", ".pdf")
                    _src_pdf = os.path.join(ctx.BASE_DIR, expected_pdf)
                    if os.path.exists(_src_pdf):
                        os.makedirs(REPORTS_DIR, exist_ok=True)
                        _dest = os.path.join(REPORTS_DIR, _fname_input)
                        shutil.copy2(_src_pdf, _dest)
                        _storage.upload(_dest)
                        st.session_state["pdf_ready"] = True
                        st.session_state["final_pdf_path"] = _dest
                        st.session_state["final_pdf_label"] = _fname_input
                        log_activity("PDF_GENERATED", detail=_fname_input)
                        status.update(label="Success!", state="complete", expanded=False)
                    else:
                        status.update(label="Compilation Failed", state="error")
                        st.error("PDF was not created. Check logs.")
                except Exception as e:
                    status.update(label="Error", state="error")
                    st.error(str(e))

    with c2:
        _pdf_path = st.session_state.get("final_pdf_path")
        _pdf_label = st.session_state.get("final_pdf_label", _default_fname)
        if not _pdf_path:
            _fallback = os.path.join(REPORTS_DIR, _default_fname)
            if os.path.exists(_fallback):
                _pdf_path = _fallback
                _pdf_label = _default_fname
        if _pdf_path and os.path.exists(_pdf_path):
            with open(_pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF",
                    data=f,
                    file_name=_pdf_label,
                    mime="application/pdf",
                    type="primary",
                    width="stretch",
                )

    with st.expander("📁 Reports Archive", expanded=False):
        _rpts = (
            sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith(".pdf")], reverse=True)
            if os.path.exists(REPORTS_DIR) else []
        )
        if _rpts:
            for _rf in _rpts:
                _rp = os.path.join(REPORTS_DIR, _rf)
                with open(_rp, "rb") as _f:
                    st.download_button(
                        _rf, _f, file_name=_rf, mime="application/pdf",
                        key=f"dl_archive_{_rf}",
                    )
        else:
            st.caption("No reports yet.")

    st.divider()

    # ── Save current issue ────────────────────────────────────────────────────
    _lang = "ar" if ctx.is_arabic else "en"
    try:
        _info      = _im.get_current_issue_info(_lang, BASE_DIR)
        _issue_num = _info["issue_num"]
        _quarter   = _info.get("quarter", "")
    except Exception:
        _issue_num = "??"
        _quarter   = ""

    _label = f"Issue {_issue_num}" + (f" — {_quarter}" if _quarter else "")
    st.markdown("#### 💾 Save Issue")
    st.caption(
        f"Archive **{_label}** ({_lang.upper()}) so you can reload it later from the Issue Manager."
    )

    if st.button("💾 Save Current Issue", type="primary", key="publish_save_issue_btn"):
        _existing = _im.list_issues(_lang, BASE_DIR)
        _exists   = any(str(i.get("issue_num")) == str(_issue_num) for i in _existing)
        if _exists:
            st.session_state["_publish_confirm_overwrite"] = True
        else:
            _ok, _msg = _im.save_issue(
                _lang, BASE_DIR,
                archived_by=st.session_state.get("current_user", "unknown"),
            )
            if _ok:
                log_activity("ISSUE_SAVED", detail=f"issue {_issue_num} ({_lang.upper()}) from publish")
                st.success(f"Issue {_issue_num} saved.")
            else:
                st.error(_msg)

    if st.session_state.get("_publish_confirm_overwrite"):
        st.warning(f"Issue **{_issue_num}** ({_lang.upper()}) is already archived. Overwrite it?")
        _oc1, _oc2 = st.columns(2)
        with _oc1:
            if st.button("✓ Overwrite", type="primary", use_container_width=True,
                         key="publish_overwrite_yes"):
                st.session_state["_publish_confirm_overwrite"] = False
                _ok, _msg = _im.save_issue(
                    _lang, BASE_DIR,
                    archived_by=st.session_state.get("current_user", "unknown"),
                    overwrite=True,
                )
                if _ok:
                    log_activity("ISSUE_SAVED", detail=f"issue {_issue_num} ({_lang.upper()}) overwrite from publish")
                    st.success(f"Issue {_issue_num} overwritten.")
                else:
                    st.error(_msg)
        with _oc2:
            if st.button("✗ Cancel", use_container_width=True, key="publish_overwrite_no"):
                st.session_state["_publish_confirm_overwrite"] = False
                st.rerun()

    st.divider()
    st.success(
        "✅ **Workflow Complete** — compile the report above, save the issue, and download your PDF."
    )
