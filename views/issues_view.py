"""
View: Issue Manager — save, load, and manage archived issues.
Dialogs: save overwrite, new from template, new from prev, load, delete.
"""
import streamlit as st

import issue_manager as _im
from utils.auth import log_activity
from utils.config import BASE_DIR
from utils.content import page_header


# ── Dialogs ───────────────────────────────────────────────────────────────────
@st.dialog("Overwrite Archived Issue?")
def _dlg_save_overwrite(issue_num, lang, user):
    st.warning(f"Issue **{issue_num}** ({lang.upper()}) is already archived. Overwrite it?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✓ Overwrite", type="primary", use_container_width=True):
            _ok, _msg = _im.save_issue(lang, BASE_DIR, archived_by=user, overwrite=True)
            if _ok:
                log_activity("ISSUE_SAVED", detail=f"issue {issue_num} ({lang.upper()}) overwrite")
                st.toast(f"Issue {issue_num} overwritten.", icon="✅")
                st.rerun()
            else:
                st.error(_msg)
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Load Blank Template?")
def _dlg_new_from_template(lang):
    st.warning(
        "This will **replace all active content** with the blank template. "
        "Save the current issue first if you want to keep it."
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✓ Confirm", type="primary", use_container_width=True):
            _ok, _msg = _im.new_from_template(lang, BASE_DIR)
            if _ok:
                log_activity("ISSUE_NEW_TEMPLATE", detail=f"lang={lang.upper()}")
                _lang_label = "Arabic" if lang == "ar" else "English"
                for _k in [k for k in st.session_state if k.startswith(f"slot_{_lang_label}_")]:
                    del st.session_state[_k]
                st.toast("Blank template loaded.", icon="📄")
                st.rerun()
            else:
                st.error(_msg)
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Load Previous Issue as Starting Point?")
def _dlg_new_from_prev(src_num, lang):
    st.warning(
        f"This will **replace all active {lang.upper()} content** with Issue **{src_num}**. "
        "Save the current issue first if you want to keep it."
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✓ Confirm", type="primary", use_container_width=True):
            _ok, _msg = _im.new_from_issue(lang, src_num, BASE_DIR)
            if _ok:
                log_activity("ISSUE_LOADED", detail=f"issue {src_num} ({lang.upper()}) as starting point")
                _lang_label = "Arabic" if lang == "ar" else "English"
                for _k in [k for k in st.session_state if k.startswith(f"slot_{_lang_label}_")]:
                    del st.session_state[_k]
                st.toast(_msg, icon="📋")
                st.rerun()
            else:
                st.error(_msg)
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Load Issue?")
def _dlg_load_issue(num, lang):
    st.warning(
        f"Load Issue **{num}** ({lang.upper()})? "
        f"This will overwrite the currently active {lang.upper()} content."
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✓ Load", type="primary", use_container_width=True):
            _ok, _msg = _im.load_issue(lang, num, BASE_DIR)
            if _ok:
                log_activity("ISSUE_LOADED", detail=f"issue {num} ({lang.upper()})")
                _lang_label = "Arabic" if lang == "ar" else "English"
                for _k in [k for k in st.session_state if k.startswith(f"slot_{_lang_label}_")]:
                    del st.session_state[_k]
                st.toast(_msg, icon="✅")
                st.rerun()
            else:
                st.error(_msg)
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Delete Archive?")
def _dlg_delete_issue(num, lang):
    st.error(
        f"Permanently delete the archive for Issue **{num}** ({lang.upper()})? "
        "This cannot be undone."
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Delete", type="primary", use_container_width=True):
            _ok, _msg = _im.delete_issue(lang, num, BASE_DIR)
            if _ok:
                log_activity("ISSUE_DELETED", detail=f"issue {num} ({lang.upper()})")
                st.toast(f"Issue {num} deleted.", icon="🗑️")
                st.rerun()
            else:
                st.error(_msg)
    with c2:
        if st.button("✗ Cancel", use_container_width=True):
            st.rerun()


# ── Render ────────────────────────────────────────────────────────────────────
def render(ctx):
    _role = st.session_state.get("current_role", "viewer")
    if _role not in ("admin", "editor"):
        st.error("🔒 Access denied. Admin or Editor role required.")
        st.stop()

    page_header(
        "📁", "Issue Manager",
        "Step 1 of 5 · Save the active issue, load a previous one, or start fresh from the blank template.",
        "#8b5cf6",
    )

    # ── Workflow overview card ────────────────────────────────────────
    from utils.config import WORKFLOW_STEPS as _WS
    _steps_html = ""
    for _w in _WS:
        _steps_html += (
            f"<div style='flex:1;text-align:center;padding:0 4px;'>"
            f"<div style='font-size:1.1rem;'>{_w['icon']}</div>"
            f"<div style='font-size:0.62rem;font-weight:700;color:#1FBACF;margin:2px 0;'>Step {_w['num']}</div>"
            f"<div style='font-size:0.65rem;color:#f1f5f9;font-weight:600;line-height:1.2;'>{_w['label']}</div>"
            f"<div style='font-size:0.6rem;color:#94a3b8;line-height:1.2;margin-top:2px;'>{_w['short']}</div>"
            f"</div>"
        )
        if _w["num"] < len(_WS):
            _steps_html += (
                "<div style='flex:0 0 14px;display:flex;align-items:center;"
                "justify-content:center;color:#475569;font-size:0.9rem;'>›</div>"
            )
    st.markdown(
        "<div style='background:#0f172a;border:1px solid #334155;border-radius:10px;"
        "padding:12px 16px;margin-bottom:1rem;'>"
        "<div style='font-size:0.68rem;font-weight:700;color:#64748b;letter-spacing:0.08em;"
        "text-transform:uppercase;margin-bottom:8px;'>Report Production Workflow</div>"
        f"<div style='display:flex;align-items:flex-start;'>{_steps_html}</div></div>",
        unsafe_allow_html=True,
    )

    # Language selector — defaults to active report language, user can override
    _im_lang_default = 1 if st.session_state.get("language") == "Arabic" else 0
    with st.container(border=True):
        _lc1, _lc2 = st.columns([2, 3])
        with _lc1:
            st.caption("Managing issues for:")
        with _lc2:
            _im_lang = st.radio(
                "", ["English (EN)", "Arabic (AR)"],
                index=_im_lang_default,
                horizontal=True,
                key="im_lang_radio",
                label_visibility="collapsed",
            )
    _lang = "en" if _im_lang.startswith("English") else "ar"

    col_active, col_saved = st.columns([1, 1], gap="large")

    with col_active:
        st.markdown("#### Active Issue")
        try:
            _info = _im.get_current_issue_info(_lang, BASE_DIR)
            _issue_num = _info["issue_num"]
            _quarter   = _info["quarter"]
            _fy        = _info.get("fiscal_year", "")
            with st.container(border=True):
                _c_num, _c_meta = st.columns([1, 2])
                with _c_num:
                    st.metric(label="Issue", value=f"#{_issue_num}")
                with _c_meta:
                    st.markdown(f"**{_quarter}**" if _quarter else "—")
                    if _fy:
                        st.caption(f"FY {_fy}")
                    st.caption("🇬🇧 EN" if _lang == "en" else "🇦🇪 AR")
        except Exception as _e:
            st.error(f"Could not read active issue: {_e}")
            _issue_num = "??"

        if st.button("💾  Save Current Issue", use_container_width=True,
                     type="primary", key="im_save_btn"):
            _existing = _im.list_issues(_lang, BASE_DIR)
            _exists = any(str(i.get("issue_num")) == str(_issue_num) for i in _existing)
            if _exists:
                _dlg_save_overwrite(
                    _issue_num, _lang,
                    st.session_state.get("current_user", "unknown"),
                )
            else:
                _ok, _msg = _im.save_issue(
                    _lang, BASE_DIR,
                    archived_by=st.session_state.get("current_user", "unknown"),
                )
                if _ok:
                    log_activity("ISSUE_SAVED", detail=f"issue {_issue_num} ({_lang.upper()})")
                    st.toast(f"Issue {_issue_num} saved.", icon="✅")
                    st.rerun()
                else:
                    st.error(_msg)

        if st.button("📄  New Issue from Template", use_container_width=True,
                     type="primary", key="im_new_template_btn"):
            _dlg_new_from_template(_lang)

        _saved_issues = _im.list_issues(_lang, BASE_DIR)
        if _saved_issues:
            st.caption("Start from a previous issue:")
            _src_options = [
                f"Issue {i['issue_num']} — {i.get('quarter', '')}".strip(" —")
                for i in _saved_issues
            ]
            _src_sel = st.selectbox(
                "Select source issue", _src_options,
                key="im_src_select", label_visibility="collapsed",
            )
            _src_idx = _src_options.index(_src_sel)
            _src_num = _saved_issues[_src_idx]["issue_num"]

            if st.button(f"📋  Load Issue {_src_num} as Starting Point",
                         use_container_width=True, key="im_new_from_prev_btn"):
                _dlg_new_from_prev(_src_num, _lang)

    with col_saved:
        st.markdown("#### Saved Issues")
        _saved_issues = _im.list_issues(_lang, BASE_DIR)
        if not _saved_issues:
            st.info("No archived issues yet. Save the current issue to create an archive.")
        else:
            for _iss in reversed(_saved_issues):
                _num      = _iss.get("issue_num", "?")
                _qtr      = _iss.get("quarter", "")
                _saved_at = _iss.get("archived_at", "")
                _saved_by = _iss.get("archived_by", "")
                _is_active = str(_num) == str(_issue_num)

                with st.container(border=True):
                    _ci, _cd = st.columns([5, 1])
                    with _ci:
                        _live_badge = (
                            " &nbsp;<span style='background:#10b981;color:white;padding:2px 9px;"
                            "border-radius:50px;font-size:0.72em;font-weight:700;'>● LIVE</span>"
                            if _is_active else ""
                        )
                        st.markdown(
                            f"**Issue {_num}**{_live_badge} &nbsp;"
                            f"<small style='color:#94a3b8;'>{_lang.upper()}</small>",
                            unsafe_allow_html=True,
                        )
                        if _qtr:
                            st.caption(_qtr)
                        if _saved_at:
                            _by_str = (
                                f" · by {_saved_by}"
                                if _saved_by and not _saved_by.startswith("system") else ""
                            )
                            st.caption(f"Saved {_saved_at[:10]}{_by_str}")
                    with _cd:
                        if _role == "admin":
                            if st.button("🗑️", key=f"im_del_{_lang}_{_num}",
                                         use_container_width=True,
                                         help=f"Delete archive for Issue {_num}"):
                                _dlg_delete_issue(_num, _lang)
                    if st.button(f"↩ Load Issue {_num}",
                                 key=f"im_load_{_lang}_{_num}", use_container_width=True):
                        _dlg_load_issue(_num, _lang)

    st.divider()
    st.info(
        "**Tip:** After loading an issue or template, go to ⚙️ Report Variables "
        "to update the Issue Number and dates before compiling."
    )
    if st.button("→ Continue to Step 2: Report Variables", type="primary", key="next_step_issues"):
        st.session_state["_pending_nav"] = "⚙️ Report Variables"
        st.rerun()
