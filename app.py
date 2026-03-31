"""
ECES Barometer Suite — Entry Point
Handles: page config, CSS, auth gate, session management, sidebar, view routing.
All business logic lives in utils/ and views/.
"""
import os
import time
from types import SimpleNamespace

import streamlit as st

# ── Page config (must be the first Streamlit call) ────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="ECES Barometer Suite",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

# ── Module imports ────────────────────────────────────────────────────────────
import issue_manager

from utils.config import (
    BASE_DIR, CHARTS_EN_DIR, CHARTS_AR_DIR, STATIC_IMG_DIR,
    ROLE_PERMISSIONS, WORKFLOW_STEPS, PROJECT_CONFIG, SESSION_TIMEOUT_MINUTES,
)
from utils.auth import (
    check_login, hash_password, load_users, log_activity,
    save_users, setup_session_state, verify_password,
    _session_expired, _touch_session,
)
from utils.content import (
    _build_section_map, factory_reset, initialize_factory_backup,
    load_custom_sections, sync_custom_sections_file,
)
from utils.compiler import _clear_miktex_issues, _get_miktex_env

import views.sections     as _sections
import views.variables    as _variables
import views.charts       as _charts
import views.publish      as _publish
import views.activity     as _activity
import views.users        as _users
import views.issues_view  as _issues

# ── Session bootstrap ─────────────────────────────────────────────────────────
setup_session_state()

# ── Login gate ────────────────────────────────────────────────────────────────
if not st.session_state["authenticated"]:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .login-container {
            max-width: 400px; margin: 100px auto; padding: 2rem;
            background: #1e293b; border-radius: 12px;
            border: 1px solid #475569;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5);
            text-align: center;
        }
        .login-header { color: #1FBACF; margin-bottom: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="login-container">
                <div style="display:flex;flex-direction:column;align-items:center;
                            gap:10px;padding:28px 0 20px 0;">
                    <div style="width:68px;height:68px;
                                background:linear-gradient(135deg,#1FBACF 0%,#CF34A9 100%);
                                border-radius:18px;display:flex;align-items:center;
                                justify-content:center;font-size:1.9rem;
                                box-shadow:0 8px 28px rgba(31,186,207,0.35);">📊</div>
                    <div style="font-size:1.5rem;font-weight:700;letter-spacing:-0.4px;
                                color:#e2e8f0;line-height:1.2;">ECES Barometer</div>
                    <div style="font-size:0.75rem;color:#64748b;letter-spacing:0.10em;
                                text-transform:uppercase;font-weight:600;">
                        Survey Management Suite</div>
                    <div style="width:44px;height:2px;
                                background:linear-gradient(90deg,#1FBACF,#CF34A9);
                                border-radius:2px;margin-top:2px;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            st.text_input("Username", key="login_user")
            st.text_input("Password", type="password", key="login_pass")
            st.form_submit_button("🔒 Secure Login", on_click=check_login,
                                  type="primary", use_container_width=True)
    st.stop()

# ── Session timeout ───────────────────────────────────────────────────────────
if _session_expired():
    _expired_user = st.session_state.get("current_user", "")
    log_activity("SESSION_TIMEOUT", _expired_user)
    for _k in list(st.session_state.keys()):
        del st.session_state[_k]
    st.session_state.update({"authenticated": False, "current_user": "",
                              "current_role": "viewer", "last_active": 0.0})
    st.warning(f"⏱️ Session expired after {SESSION_TIMEOUT_MINUTES} minutes of inactivity. Please log in again.")
    st.rerun()

_touch_session()

# Warn when less than 5 minutes remain
_remaining_secs = SESSION_TIMEOUT_MINUTES * 60 - (
    time.time() - st.session_state.get("last_active", time.time())
)
if 0 < _remaining_secs < 300:
    _mins, _secs = int(_remaining_secs // 60), int(_remaining_secs % 60)
    st.warning(f"⏱️ Your session will expire in **{_mins}m {_secs}s** due to inactivity. Save your work.")

# ── Language state ────────────────────────────────────────────────────────────
if "language" not in st.session_state:
    st.session_state["language"] = "English"

is_arabic    = st.session_state["language"] == "Arabic"
text_direction = "rtl" if is_arabic else "ltr"
font_family    = ("'Almarai', 'Amiri', 'Arial', sans-serif" if is_arabic
                  else "'Sinkin Sans', 'Inter', 'Source Sans Pro', sans-serif")
editor_align   = "right" if is_arabic else "left"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ECES CORPORATE THEME — Dark Mode with Cyan/Magenta Branding */
:root {{
    --primary: #1FBACF; --secondary: #1FBACF; --accent: #CF34A9;
    --light-accent: #5ce0f0;
    --bg-dark: #0f172a; --bg-primary: #1e293b; --bg-secondary: #334155;
    --sidebar-bg: #1e293b; --card-bg: #1e293b;
    --text-primary: #f1f5f9; --text-secondary: #cbd5e1;
    --border-color: #475569;
    --success: #10b981; --warning: #f59e0b; --error: #ef4444;
}}
.stApp {{
    background: var(--bg-primary); color: var(--text-primary);
    font-family: 'Sinkin Sans', 'Inter', 'Source Sans Pro', sans-serif;
}}
h1,h2,h3,h4,h5,h6 {{ color: var(--text-primary) !important; font-weight: 600 !important; }}
p, label, span, div {{ color: var(--text-primary) !important; line-height: 1.6; }}
section[data-testid="stSidebar"] {{
    background: var(--sidebar-bg); border-right: 1px solid var(--border-color);
}}
section[data-testid="stSidebar"] > div {{ padding-top: 1rem; }}
section[data-testid="stSidebar"] h3 {{
    color: var(--primary); font-weight: 600 !important; margin-bottom: 0.75rem !important;
}}
.css-card {{
    background: var(--card-bg); padding: 1.5rem; border-radius: 12px;
    border: 1px solid var(--border-color); margin-bottom: 1rem;
    box-shadow: 0 6px 40px rgba(143,143,143,0.08);
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}}
.css-card:hover {{
    border-color: var(--accent); box-shadow: 0 8px 40px rgba(31,186,207,0.12);
}}
.stTextArea textarea {{
    background: var(--bg-secondary) !important; color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-{"right" if is_arabic else "left"}: 3px solid var(--primary) !important;
    border-radius: 12px !important;
    font-family: {font_family} !important;
    font-size: 16px !important; line-height: 1.6 !important;
    direction: {text_direction} !important; text-align: {editor_align} !important;
    padding: 1rem !important; transition: border-color 0.2s ease;
}}
.stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    border-{"right" if is_arabic else "left"}-color: var(--accent) !important;
    outline: none !important;
}}
div.stButton > button {{
    background: var(--card-bg); color: var(--text-primary);
    border: 1px solid var(--border-color); border-radius: 50px;
    padding: 0.5rem 1.25rem; font-weight: 500; transition: all 0.3s ease;
}}
div.stButton > button:hover {{ border-color: var(--accent); color: var(--light-accent); }}
button[kind="primary"] {{
    background: var(--primary) !important; border: none !important;
    color: white !important; font-weight: 600 !important; transition: all 0.3s ease;
}}
button[kind="primary"]:hover {{ background: var(--accent) !important; }}
.stSelectbox > div > div, .stRadio > div {{
    background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px;
}}
.stSuccess {{ background: rgba(16,185,129,0.1) !important; border-left: 3px solid var(--success) !important; }}
.stWarning {{ background: rgba(245,158,11,0.1) !important; border-left: 3px solid var(--warning) !important; }}
.stError   {{ background: rgba(239,68,68,0.1) !important;  border-left: 3px solid var(--error) !important; }}
.stInfo    {{ background: rgba(31,186,207,0.1) !important; border-left: 3px solid var(--primary) !important; }}
iframe {{ border: 1px solid var(--border-color); border-radius: 12px; background: white; }}
div[data-testid="stExpander"] {{
    background: var(--card-bg); border: 1px solid var(--border-color);
    border-radius: 12px; margin-bottom: 0.75rem;
}}
.stFileUploader > div {{
    background: var(--card-bg); border: 1px dashed var(--border-color); border-radius: 12px;
}}
div[data-testid="stMetric"] {{
    background: var(--card-bg); border: 1px solid var(--border-color);
    border-radius: 12px; padding: 1rem;
}}
div[data-testid="stMetric"] label {{ color: var(--text-secondary) !important; }}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ color: var(--primary) !important; }}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-dark); }}
::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 99px; }}
::-webkit-scrollbar-thumb:hover {{ background: #475569; }}

/* ── Sidebar nav: hide radio dots, style as menu list ── */
div[data-testid="stSidebarContent"] .stRadio > label {{ display: none !important; }}
div[data-testid="stSidebarContent"] .stRadio > div[role="radiogroup"] {{
    display: flex; flex-direction: column; gap: 2px; background: transparent !important;
    border: none !important; border-radius: 0 !important; padding: 0 !important;
}}
div[data-testid="stSidebarContent"] .stRadio label {{
    display: flex !important; align-items: center;
    padding: 9px 12px; border-radius: 8px; cursor: pointer;
    font-size: 0.90rem; font-weight: 500; color: #94a3b8;
    background: transparent; border: none !important;
    transition: background 0.18s ease, color 0.18s ease;
    gap: 8px; user-select: none;
}}
div[data-testid="stSidebarContent"] .stRadio label:hover {{
    background: rgba(31,186,207,0.08); color: #e2e8f0;
}}
div[data-testid="stSidebarContent"] .stRadio label:has(input[aria-checked="true"]) {{
    background: rgba(31,186,207,0.15) !important; color: #1FBACF !important;
    font-weight: 600 !important;
    border-left: 3px solid #1FBACF !important; padding-left: 9px !important;
}}
div[data-testid="stSidebarContent"] .stRadio input[type="radio"] {{
    position: absolute; opacity: 0; width: 0; height: 0; pointer-events: none;
}}

/* ── Continue / next-step button wrapper ── */
div.continue-btn-wrapper > div[data-testid="stButton"] > button {{
    background: linear-gradient(90deg, #1FBACF 0%, #0ea5c9 100%) !important;
    color: #0f172a !important; font-weight: 700 !important;
    font-size: 0.95rem !important; letter-spacing: 0.02em !important;
    border: none !important; border-radius: 10px !important;
    box-shadow: 0 4px 18px rgba(31,186,207,0.30) !important;
    transition: box-shadow 0.2s ease, transform 0.15s ease !important;
}}
div.continue-btn-wrapper > div[data-testid="stButton"] > button:hover {{
    box-shadow: 0 6px 26px rgba(31,186,207,0.50) !important;
    transform: translateY(-1px) !important;
}}

/* ── Chart image height cap ── */
div[data-testid="stImage"] img {{
    max-height: 260px; object-fit: contain; border-radius: 6px; width: 100%;
}}

/* ── Metric refinements ── */
div[data-testid="stMetricValue"] > div {{
    font-size: 1.55rem !important; font-weight: 700 !important;
}}
div[data-testid="stMetricLabel"] > div {{
    font-size: 0.72rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.06em; color: #64748b !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Directory setup ───────────────────────────────────────────────────────────
for _d in [CHARTS_EN_DIR, CHARTS_AR_DIR, STATIC_IMG_DIR]:
    os.makedirs(_d, exist_ok=True)

ACTIVE_CHARTS_DIR = CHARTS_AR_DIR if is_arabic else CHARTS_EN_DIR

# ── App startup tasks (run once per session, not on every rerun) ──────────────
if not st.session_state.get("_startup_done"):
    initialize_factory_backup()
    for _startup_lang in ("English", "Arabic"):
        _suffix = "_ar" if _startup_lang == "Arabic" else ""
        _gen_file = os.path.join(BASE_DIR, f"custom_sections_generated{_suffix}.tex")
        if not os.path.exists(_gen_file):
            open(_gen_file, "w", encoding="utf-8").write("% Auto-generated by ECES CMS\n")
    issue_manager.ensure_template_charts(BASE_DIR)
    issue_manager.auto_archive_if_new("en", BASE_DIR)
    issue_manager.auto_archive_if_new("ar", BASE_DIR)
    st.session_state["_startup_done"] = True

# ── Active config ─────────────────────────────────────────────────────────────
active_config = PROJECT_CONFIG[st.session_state["language"]]

@st.cache_data(ttl=2)
def _cached_section_map(lang: str, base_sections_key: str):
    """Cache the merged section map for 2 s — avoids JSON read on every rerun."""
    return _build_section_map(lang, PROJECT_CONFIG[lang]["sections"])

SECTION_MAP   = _cached_section_map(st.session_state["language"], st.session_state["language"])
CONFIG_FILE   = os.path.join(BASE_DIR, active_config["config"])
MAIN_FILE     = os.path.join(BASE_DIR, active_config["main"])
PREAMBLE_FILE = active_config["preamble"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join(STATIC_IMG_DIR, "eces_logo.png")
    if os.path.exists(logo_path):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo_path, width=150)
    else:
        st.markdown("""
            <div style='background:linear-gradient(135deg,#0f172a 0%,#1FBACF 100%);
                        border-radius:12px;padding:15px;text-align:center;margin-bottom:15px;
                        box-shadow:0 6px 40px rgba(143,143,143,0.12);'>
                <h2 style='color:white;margin:0;font-size:1.4rem;font-weight:700;letter-spacing:1px;'>
                    📊 ECES Suite
                </h2>
            </div>
        """, unsafe_allow_html=True)

    # Language toggle
    st.markdown("**🌍 Report Language**")
    selected_lang = st.radio(
        "Select Language", ["English", "Arabic"],
        index=0 if st.session_state["language"] == "English" else 1,
        label_visibility="collapsed", horizontal=True,
    )
    if selected_lang != st.session_state["language"]:
        st.session_state["language"] = selected_lang
        st.session_state["pdf_ready"] = False
        st.rerun()

    st.caption("Switches which language files are compiled (EN / AR)")
    st.markdown("---")

    # User info + logout
    _role_badge = {"admin": "🔴 Admin", "editor": "🟡 Editor", "viewer": "🟢 Viewer"}.get(
        st.session_state["current_role"], "🟢 Viewer"
    )
    _uc1, _uc2 = st.columns([3, 1])
    with _uc1:
        st.markdown(
            f"<div style='font-size:0.82rem;color:#94a3b8;padding:0.3rem 0;'>"
            f"👤 <b style='color:#f1f5f9;'>{st.session_state['current_user']}</b><br>"
            f"<span style='font-size:0.75rem;'>{_role_badge}</span></div>",
            unsafe_allow_html=True,
        )
    with _uc2:
        if st.button("↩", help="Logout", use_container_width=True, key="sidebar_logout"):
            log_activity("LOGOUT")
            for _k in list(st.session_state.keys()):
                del st.session_state[_k]
            st.session_state.update({"authenticated": False, "current_user": "",
                                     "current_role": "viewer", "last_active": 0.0})
            st.rerun()

    # Self-service password change
    with st.expander("🔑 Change Password", expanded=False):
        with st.form("change_pw_form", clear_on_submit=True):
            _cur_pw     = st.text_input("Current Password", type="password")
            _new_pw     = st.text_input("New Password", type="password")
            _confirm_pw = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Update", use_container_width=True):
                _users = load_users()
                _me = st.session_state["current_user"]
                if _me not in _users:
                    st.error("User not found.")
                elif not verify_password(_cur_pw, _users[_me]["password"]):
                    st.error("Current password is incorrect.")
                elif len(_new_pw) < 6:
                    st.error("New password must be at least 6 characters.")
                elif _new_pw != _confirm_pw:
                    st.error("Passwords do not match.")
                else:
                    _users[_me]["password"] = hash_password(_new_pw)
                    save_users(_users)
                    log_activity("PASSWORD_CHANGE", _me)
                    st.success("Password updated!")

    st.markdown("---")

    # ── Pending navigation relay (from "Next Step" buttons in views) ─
    if "_pending_nav" in st.session_state:
        st.session_state["nav_radio"] = st.session_state.pop("_pending_nav")

    # ── Visited-steps tracking ────────────────────────────────────────
    st.session_state.setdefault("visited_steps", set())
    _allowed = ROLE_PERMISSIONS.get(st.session_state.get("current_role", "viewer"), ["📝 Report Sections"])
    _view_to_step = {s["view_key"]: s["num"] for s in WORKFLOW_STEPS}
    _current_step_num = _view_to_step.get(st.session_state.get("nav_radio", _allowed[0]), 0)
    _accessible_keys = {s["view_key"] for s in WORKFLOW_STEPS if s["view_key"] in _allowed}

    # ── Visual stepper (decorative — click navigation via radio below) ─
    _stepper_html = (
        "<div style='margin-bottom:6px;font-size:0.7rem;font-weight:700;"
        "color:#64748b;letter-spacing:0.08em;text-transform:uppercase;'>Workflow</div>"
    )
    for _s in WORKFLOW_STEPS:
        if _s["view_key"] not in _accessible_keys:
            continue
        _n = _s["num"]
        _is_active  = (_n == _current_step_num)
        _is_visited = (_n in st.session_state["visited_steps"] and not _is_active)
        if _is_active:
            _cbg, _ccol, _lcol, _op = "#1FBACF", "white",   "#f1f5f9", "1"
        elif _is_visited:
            _cbg, _ccol, _lcol, _op = "#134e4a", "#6ee7b7", "#94a3b8", "1"
        else:
            _cbg, _ccol, _lcol, _op = "#334155", "#64748b", "#64748b", "0.6"
        _stepper_html += (
            f"<div style='display:flex;align-items:flex-start;gap:8px;"
            f"margin-bottom:6px;opacity:{_op};'>"
            f"<div style='min-width:22px;height:22px;border-radius:50%;"
            f"background:{_cbg};color:{_ccol};font-size:0.7rem;font-weight:700;"
            f"display:flex;align-items:center;justify-content:center;"
            f"margin-top:1px;flex-shrink:0;'>{_n}</div>"
            f"<div><div style='font-size:0.78rem;font-weight:600;color:{_lcol};'>"
            f"{_s['label']}</div>"
            f"<div style='font-size:0.75rem;color:#94a3b8;line-height:1.3;'>"
            f"{_s['short']}</div></div></div>"
        )
    st.markdown(_stepper_html, unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)

    # ── Navigation radio ──────────────────────────────────────────────
    st.markdown("**Navigation**")
    selected_view = st.radio("Navigation", _allowed, label_visibility="collapsed", key="nav_radio")

    # Mark the active step as visited
    _active_step = _view_to_step.get(selected_view, 0)
    if _active_step:
        st.session_state["visited_steps"].add(_active_step)

    st.markdown("---")
    st.info("💡 **Tip:** 'Preview' compiles the current section only.")

    # Factory reset (admin only)
    if st.session_state.get("current_role") == "admin":
        with st.expander("⚠️ Factory Reset", expanded=False):
            if st.button("↩ Reset Current Section", use_container_width=True, key="reset_current"):
                _section_name = st.session_state.get("_current_section_name", "")
                if _section_name:
                    filename = os.path.basename(SECTION_MAP.get(_section_name, ""))
                    success, msg = factory_reset(target=filename)
                    if success:
                        log_activity("FACTORY_RESET", detail=f"file: {filename}")
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.info("Open a section first to reset it.")

            if st.button("🔄 Reset All Content Edits", use_container_width=True, key="reset_overrides"):
                success, msg = factory_reset(target="overrides")
                if success:
                    log_activity("FACTORY_RESET", detail="overrides only")
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            if st.button("⚠️ Full Factory Reset", use_container_width=True,
                         type="primary", key="reset_all_trigger"):
                st.session_state["confirm_reset_all"] = True
                st.rerun()

            if st.session_state.get("confirm_reset_all"):
                st.warning("⚠️ This will restore ALL files to original state!")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✓ Confirm", use_container_width=True, key="confirm_yes"):
                        success, msg = factory_reset(target="all")
                        st.session_state["confirm_reset_all"] = False
                        if success:
                            log_activity("FACTORY_RESET", detail="all files")
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                with col_no:
                    if st.button("✗ Cancel", use_container_width=True, key="confirm_no"):
                        st.session_state["confirm_reset_all"] = False
                        st.rerun()

# ── View context (passed to every render function) ────────────────────────────
ctx = SimpleNamespace(
    is_arabic=is_arabic,
    SECTION_MAP=SECTION_MAP,
    BASE_DIR=BASE_DIR,
    ACTIVE_CHARTS_DIR=ACTIVE_CHARTS_DIR,
    STATIC_IMG_DIR=STATIC_IMG_DIR,
    active_config=active_config,
    CONFIG_FILE=CONFIG_FILE,
    MAIN_FILE=MAIN_FILE,
    PREAMBLE_FILE=PREAMBLE_FILE,
)

# ── View routing ──────────────────────────────────────────────────────────────
_VIEW_MODULES = {
    "📝 Report Sections":  _sections.render,
    "⚙️ Report Variables": _variables.render,
    "📊 Chart Manager":    _charts.render,
    "🚀 Finalize & Publish": _publish.render,
    "📋 Activity Log":     _activity.render,
    "👥 User Management":  _users.render,
    "📁 Issue Manager":    _issues.render,
}

if selected_view in _VIEW_MODULES:
    _VIEW_MODULES[selected_view](ctx)
