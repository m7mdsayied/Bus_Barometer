import streamlit as st
import os
import re
import subprocess
import base64
import shutil
import time

# ==========================================
# 1. CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="ECES Barometer Suite",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ==========================================
# 0. AUTHENTICATION SYSTEM
# ==========================================
import json
import bcrypt
import logging
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
ACTIVITY_LOG = os.path.join(os.path.dirname(__file__), "activity.log")
SESSION_TIMEOUT_MINUTES = 30

# ── Activity Logger ─────────────────────────────────────
_activity_logger = logging.getLogger("eces_activity")
_activity_logger.setLevel(logging.INFO)
if not _activity_logger.handlers:
    _fh = logging.FileHandler(ACTIVITY_LOG, encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    _activity_logger.addHandler(_fh)

def log_activity(action: str, user: str = "", detail: str = ""):
    """Write a line to activity.log."""
    user = user or st.session_state.get("current_user", "unknown")
    _activity_logger.info(f"[{user}] {action}" + (f" — {detail}" if detail else ""))

def parse_activity_log():
    """Parse activity.log into structured records for the Activity Log viewer."""
    records = []
    if not os.path.exists(ACTIVITY_LOG):
        return records
    with open(ACTIVITY_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.match(
                r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| \[(\w+)\] (\w+)(?: — (.*))?",
                line
            )
            if match:
                records.append({
                    "timestamp": match.group(1),
                    "date": match.group(1)[:10],
                    "user": match.group(2),
                    "action": match.group(3),
                    "detail": match.group(4) or "",
                })
    return records

# ── Password Helpers (bcrypt) ───────────────────────────
def hash_password(plain: str) -> str:
    """Return a bcrypt hash string for a plaintext password."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, stored: str) -> bool:
    """Check a plaintext password against a stored value.
    Supports both bcrypt hashes and legacy plaintext (for migration)."""
    if stored.startswith("$2b$") or stored.startswith("$2a$"):
        return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
    # Legacy plaintext comparison (will be auto-migrated on success)
    return plain == stored

# Role → allowed nav views (English keys)
ROLE_PERMISSIONS = {
    "admin":   ["📝 Report Sections", "⚙️ Report Variables", "📊 Chart Manager", "🚀 Finalize & Publish", "📋 Activity Log", "👥 User Management"],
    "editor":  ["📝 Report Sections", "⚙️ Report Variables", "📊 Chart Manager"],
    "viewer":  ["📝 Report Sections"],
}

def load_users() -> dict:
    """Load users from users.json, falling back to st.secrets if file is missing."""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        pass  # fall through to secrets
    except Exception:
        pass  # corrupted file — also fall through

    try:
        return {
            username: dict(attrs)
            for username, attrs in st.secrets["users"].items()
        }
    except Exception:
        return {}

def save_users(users: dict):
    """Persist users dict back to users.json."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# Session state bootstrap
for _key, _val in [("authenticated", False), ("current_user", ""), ("current_role", "viewer"), ("last_active", 0.0)]:
    if _key not in st.session_state:
        st.session_state[_key] = _val

def _session_expired() -> bool:
    """Return True if the session has been idle longer than SESSION_TIMEOUT_MINUTES."""
    last = st.session_state.get("last_active", 0.0)
    if last == 0.0:
        return False
    return (time.time() - last) > SESSION_TIMEOUT_MINUTES * 60

def _touch_session():
    """Update the last-active timestamp to now."""
    st.session_state["last_active"] = time.time()

def check_login():
    """Verifies credentials and stores user + role in session state."""
    username = st.session_state['login_user'].strip()
    password = st.session_state['login_pass']
    users = load_users()

    if username in users:
        user = users[username]
        if user.get("enabled", True) and verify_password(password, user["password"]):
            # Auto-migrate plaintext password to bcrypt on successful login
            if not (user["password"].startswith("$2b$") or user["password"].startswith("$2a$")):
                users[username]["password"] = hash_password(password)
                save_users(users)

            st.session_state['authenticated'] = True
            st.session_state['current_user'] = username
            st.session_state['current_role'] = user.get("role", "viewer")
            _touch_session()
            log_activity("LOGIN", username)
            st.toast(f"Welcome back, {username}!", icon="🔓")
            return
    st.error("❌ Invalid username or password, or account is disabled.")

if not st.session_state['authenticated']:
    # Custom CSS to hide the sidebar on the login screen only
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: #1e293b;
            border-radius: 12px;
            border: 1px solid #475569;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
            text-align: center;
        }
        .login-header { color: #1FBACF; margin-bottom: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)
    
    # Login Form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="login-container">
                <h2 class="login-header">ECES Barometer Suite</h2>
                <p>Please log in to continue</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.text_input("Username", key="login_user")
            st.text_input("Password", type="password", key="login_pass")
            st.form_submit_button("🔒 Secure Login", on_click=check_login, type="primary", use_container_width=True)
            
    # Stop execution here if not logged in
    st.stop()

# ── Session Timeout Check ───────────────────────────────
if _session_expired():
    _expired_user = st.session_state.get("current_user", "")
    log_activity("SESSION_TIMEOUT", _expired_user)
    for _k in list(st.session_state.keys()):
        del st.session_state[_k]
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = ""
    st.session_state["current_role"] = "viewer"
    st.session_state["last_active"] = 0.0
    st.warning(f"⏱️ Session expired after {SESSION_TIMEOUT_MINUTES} minutes of inactivity. Please log in again.")
    st.rerun()

# Keep session alive on every interaction
_touch_session()

# Initialize Session State for Language
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

# Define Language-Specific Logic
is_arabic = st.session_state['language'] == 'Arabic'
text_direction = "rtl" if is_arabic else "ltr"
font_family = "'Almarai', 'Amiri', 'Arial', sans-serif" if is_arabic else "'Sinkin Sans', 'Inter', 'Source Sans Pro', sans-serif"
editor_align = "right" if is_arabic else "left"

st.markdown(f"""
    <style>
    /* ECES CORPORATE THEME — Dark Mode with Cyan/Magenta Branding */

    :root {{
        /* ECES Brand Palette */
        --primary: #1FBACF;
        --secondary: #1FBACF;
        --accent: #CF34A9;
        --light-accent: #5ce0f0;

        /* Backgrounds */
        --bg-dark: #0f172a;
        --bg-primary: #1e293b;
        --bg-secondary: #334155;
        --sidebar-bg: #1e293b;
        --card-bg: #1e293b;

        /* Text */
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;

        /* Borders & Status */
        --border-color: #475569;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
    }}

    /* Base Styles */
    .stApp {{
        background: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Sinkin Sans', 'Inter', 'Source Sans Pro', sans-serif;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }}

    p, label, span, div {{
        color: var(--text-primary) !important;
        line-height: 1.6;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 1rem;
    }}

    section[data-testid="stSidebar"] h3 {{
        color: var(--primary);
        font-weight: 600 !important;
        margin-bottom: 0.75rem !important;
    }}

    /* Cards */
    .css-card {{
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
        box-shadow: 0 6px 40px rgba(143, 143, 143, 0.08);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }}

    .css-card:hover {{
        border-color: var(--accent);
        box-shadow: 0 8px 40px rgba(31, 186, 207, 0.12);
    }}

    /* Text Editors */
    .stTextArea textarea {{
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-{"right" if is_arabic else "left"}: 3px solid var(--primary) !important;
        border-radius: 12px !important;
        font-family: {font_family} !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        direction: {text_direction} !important;
        text-align: {editor_align} !important;
        padding: 1rem !important;
        transition: border-color 0.2s ease;
    }}

    .stTextArea textarea:focus {{
        border-color: var(--accent) !important;
        border-{"right" if is_arabic else "left"}-color: var(--accent) !important;
        outline: none !important;
    }}

    /* Buttons */
    div.stButton > button {{
        background: var(--card-bg);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 50px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover {{
        border-color: var(--accent);
        color: var(--light-accent);
    }}

    button[kind="primary"] {{
        background: var(--primary) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }}

    button[kind="primary"]:hover {{
        background: var(--accent) !important;
    }}

    /* Form Elements */
    .stSelectbox > div > div,
    .stRadio > div {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
    }}

    /* Status Messages */
    .stSuccess {{
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 3px solid var(--success) !important;
    }}

    .stWarning {{
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 3px solid var(--warning) !important;
    }}

    .stError {{
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 3px solid var(--error) !important;
    }}

    .stInfo {{
        background: rgba(31, 186, 207, 0.1) !important;
        border-left: 3px solid var(--primary) !important;
    }}

    /* PDF Viewer */
    iframe {{
        border: 1px solid var(--border-color);
        border-radius: 12px;
        background: white;
    }}

    /* Expanders */
    div[data-testid="stExpander"] {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin-bottom: 0.75rem;
    }}

    /* File Uploader */
    .stFileUploader > div {{
        background: var(--card-bg);
        border: 1px dashed var(--border-color);
        border-radius: 12px;
    }}

    /* Metrics */
    div[data-testid="stMetric"] {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
    }}

    div[data-testid="stMetric"] label {{
        color: var(--text-secondary) !important;
    }}

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: var(--primary) !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: var(--bg-primary);
    }}

    ::-webkit-scrollbar-thumb {{
        background: var(--border-color);
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary);
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FILE SYSTEM & MAPPING LOGIC
# ==========================================
BASE_DIR = os.getcwd()
CHARTS_EN_DIR = os.path.join(BASE_DIR, "images", "charts")
CHARTS_AR_DIR = os.path.join(BASE_DIR, "images", "charts_ar")
STATIC_IMG_DIR = os.path.join(BASE_DIR, "images", "static")
# Ensure all directories exist
for d in[CHARTS_EN_DIR, CHARTS_AR_DIR, STATIC_IMG_DIR]:
    os.makedirs(d, exist_ok=True)

# Set the active charts directory dynamically based on the current language
ACTIVE_CHARTS_DIR = CHARTS_AR_DIR if is_arabic else CHARTS_EN_DIR


# ==========================================
# FACTORY RESET SYSTEM
# ==========================================
BACKUP_DIR = os.path.join(BASE_DIR, "templates_backup")

def initialize_factory_backup():
    """Create initial backup of templates if not exists"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

        # Backup content files
        content_backup = os.path.join(BACKUP_DIR, "content")
        os.makedirs(content_backup, exist_ok=True)
        if os.path.exists(os.path.join(BASE_DIR, "content")):
            for file in os.listdir(os.path.join(BASE_DIR, "content")):
                if file.endswith(".tex"):
                    shutil.copy2(
                        os.path.join(BASE_DIR, "content", file),
                        os.path.join(content_backup, file)
                    )

        # Backup static sections
        static_backup = os.path.join(BACKUP_DIR, "static_sections")
        os.makedirs(static_backup, exist_ok=True)
        if os.path.exists(os.path.join(BASE_DIR, "static_sections")):
            for file in os.listdir(os.path.join(BASE_DIR, "static_sections")):
                if file.endswith(".tex"):
                    shutil.copy2(
                        os.path.join(BASE_DIR, "static_sections", file),
                        os.path.join(static_backup, file)
                    )

        # Backup config files
        for config_file in ["config.tex", "config_ar.tex"]:
            if os.path.exists(os.path.join(BASE_DIR, config_file)):
                shutil.copy2(
                    os.path.join(BASE_DIR, config_file),
                    os.path.join(BACKUP_DIR, config_file)
                )

        return True
    return False

def factory_reset(target="all"):
    """
    Restore files from factory backup.
    Also clears content override files when doing a full reset.

    Args:
        target: "all", "overrides", or specific filename
    """
    if not os.path.exists(BACKUP_DIR) and target != "overrides":
        return False, "No factory backup found. Cannot reset."

    try:
        if target == "overrides":
            # Reset only the override files (slot edits)
            overrides_dir = os.path.join(BASE_DIR, "overrides")
            if os.path.exists(overrides_dir):
                count = 0
                for f in os.listdir(overrides_dir):
                    if f.endswith(".tex"):
                        os.remove(os.path.join(overrides_dir, f))
                        count += 1
                return True, f"Cleared {count} content overrides"
            return True, "No overrides to clear"

        elif target == "all":
            # Reset all content files
            backup_content = os.path.join(BACKUP_DIR, "content")
            if os.path.exists(backup_content):
                for file in os.listdir(backup_content):
                    shutil.copy2(
                        os.path.join(backup_content, file),
                        os.path.join(BASE_DIR, "content", file)
                    )

            # Reset all static sections
            backup_static = os.path.join(BACKUP_DIR, "static_sections")
            if os.path.exists(backup_static):
                for file in os.listdir(backup_static):
                    shutil.copy2(
                        os.path.join(backup_static, file),
                        os.path.join(BASE_DIR, "static_sections", file)
                    )

            # Reset config files
            for config_file in ["config.tex", "config_ar.tex"]:
                if os.path.exists(os.path.join(BACKUP_DIR, config_file)):
                    shutil.copy2(
                        os.path.join(BACKUP_DIR, config_file),
                        os.path.join(BASE_DIR, config_file)
                    )

            # Also clear all content overrides
            overrides_dir = os.path.join(BASE_DIR, "overrides")
            if os.path.exists(overrides_dir):
                for f in os.listdir(overrides_dir):
                    if f.endswith(".tex"):
                        os.remove(os.path.join(overrides_dir, f))

            return True, "All files restored to factory state (including content overrides)"

        else:
            # Reset specific file
            if os.path.exists(os.path.join(BACKUP_DIR, "content", target)):
                src = os.path.join(BACKUP_DIR, "content", target)
                dst = os.path.join(BASE_DIR, "content", target)
            elif os.path.exists(os.path.join(BACKUP_DIR, "static_sections", target)):
                src = os.path.join(BACKUP_DIR, "static_sections", target)
                dst = os.path.join(BASE_DIR, "static_sections", target)
            else:
                return False, f"File {target} not found in backup"

            shutil.copy2(src, dst)

            # Also clear any overrides belonging to this section
            overrides_dir = os.path.join(BASE_DIR, "overrides")
            # Derive prefix from filename (e.g. 01_exec_summary.tex → exec_)
            base_name = target.replace(".tex", "").replace("_ar", "")
            # Remove leading number prefix like "01_"
            if len(base_name) > 3 and base_name[2] == '_':
                base_name = base_name[3:]
            if os.path.exists(overrides_dir):
                for f in os.listdir(overrides_dir):
                    if f.startswith(base_name.split("_")[0] + "_") and f.endswith(".tex"):
                        os.remove(os.path.join(overrides_dir, f))

            return True, f"Restored {target} (and cleared related overrides)"

    except Exception as e:
        return False, f"Reset failed: {str(e)}"

# Initialize backup on startup
initialize_factory_backup()

# --- DYNAMIC PROJECT STRUCTURE ---
# This maps sections to specific files based on the language
PROJECT_CONFIG = {
    "English": {
        "main": "main.tex",
        "config": "config.tex",
        "preamble": "preamble.tex",
        "sections": {
            "Executive Summary": "content/01_exec_summary.tex",
            "Macroeconomic Overview": "content/02_macro_overview.tex",
            "Analysis: Overall Index": "content/03_analysis_overall.tex",
            "Analysis: Constraints": "content/04_constraints.tex",
            "Analysis: Sub-Indices": "content/05_subindices.tex",
            "Appendix: Data Tables": "content/06_tables.tex",
            "Cover Page Text": "static_sections/00_cover.tex",
            "About ECES": "static_sections/00_about_eces.tex",
            "Methodology": "static_sections/00_methodology.tex",
        }
    },
    "Arabic": {
        "main": "main_ar.tex",
        "config": "config_ar.tex",
        "preamble": "preamble_ar.tex",
        "sections": {
            "Executive Summary": "content/01_exec_summary_ar.tex",
            "Macroeconomic Overview": "content/02_macro_overview_ar.tex",
            "Analysis: Overall Index": "content/03_analysis_overall_ar.tex",
            "Analysis: Constraints": "content/04_constraints_ar.tex",
            "Analysis: Sub-Indices": "content/05_subindices_ar.tex",
            "Appendix: Data Tables": "content/06_tables_ar.tex",
            "Cover Page Text": "static_sections/00_cover_ar.tex",
            "About ECES": "static_sections/00_about_eces_ar.tex",
            "Methodology": "static_sections/00_methodology_ar.tex",
        }
    }
}

# Get current config based on selection
active_config = PROJECT_CONFIG[st.session_state['language']]
SECTION_MAP = active_config["sections"]
CONFIG_FILE = os.path.join(BASE_DIR, active_config["config"])
MAIN_FILE = os.path.join(BASE_DIR, active_config["main"])
PREAMBLE_FILE = active_config["preamble"]

def load_file(filepath):
    if not os.path.exists(filepath): return ""
    with open(filepath, 'r', encoding='utf-8') as f: return f.read()

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f: f.write(content)

def display_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        st.error("Preview file not found.")
        return
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0&scrollbar=0" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# ==========================================
# 3. COMPILER & TOOLS
# ==========================================
def parse_latex_log(log_path):
    if not os.path.exists(log_path): return "Log file not found."
    errors = []
    try:
        with open(log_path, "r", encoding="latin-1", errors='ignore') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("!"):
                context = lines[i:i+3] 
                errors.append("".join(context).strip())
    except:
        return "Could not parse log."
    return "\n\n".join(errors) if errors else "Unknown error. Check syntax."

def render_toolbar():
    """Render LaTeX quick-insert toolbar with 3 rows of helpers."""
    st.markdown("##### 🛠️ Quick Tools")

    def show_hint(msg, code):
        st.toast(msg, icon="💡")
        st.sidebar.code(code, language="latex")
        st.sidebar.info("Code copied to sidebar! ↖️")

    # Row 1 — Basic formatting
    r1 = st.columns(5)
    with r1[0]:
        if st.button("Bold", width='stretch', key="tb_bold"): show_hint("Bold Text", r"\textbf{Text}")
    with r1[1]:
        if st.button("Italic", width='stretch', key="tb_italic"): show_hint("Italic Text", r"\textit{Text}")
    with r1[2]:
        if st.button("Underline", width='stretch', key="tb_underline"): show_hint("Underline", r"\underline{Text}")
    with r1[3]:
        if st.button("% Sign", width='stretch', key="tb_pct"): show_hint("Escape %", r"\%")
    with r1[4]:
        if st.button("New Line", width='stretch', key="tb_newline"): show_hint("Line Break", r"\\")

    # Row 2 — Structures
    r2 = st.columns(5)
    with r2[0]:
        if st.button("List", width='stretch', key="tb_list"):
            show_hint("Bulleted List", "\\begin{itemize}\n    \\item Point 1\n    \\item Point 2\n\\end{itemize}")
    with r2[1]:
        if st.button("Numbered", width='stretch', key="tb_enum"):
            show_hint("Numbered List", "\\begin{enumerate}\n    \\item First\n    \\item Second\n\\end{enumerate}")
    with r2[2]:
        if st.button("Footnote", width='stretch', key="tb_fn"): show_hint("Footnote", r"\footnote{Note text}")
    with r2[3]:
        if st.button("Table", width='stretch', key="tb_table"):
            show_hint("Table", "\\begin{tabular}{l|r}\n    Header & Value \\\\\n    \\hline\n    Row 1 & 100 \\\\\n\\end{tabular}")
    with r2[4]:
        if st.button("Superscript", width='stretch', key="tb_sup"): show_hint("Superscript", r"\textsuperscript{th}")

    # Row 3 — Special characters
    r3 = st.columns(5)
    with r3[0]:
        if st.button("En-dash –", width='stretch', key="tb_endash"): show_hint("En-dash", "--")
    with r3[1]:
        if st.button("Em-dash —", width='stretch', key="tb_emdash"): show_hint("Em-dash", "---")
    with r3[2]:
        if st.button("Arabic ،", width='stretch', key="tb_arcomma"): show_hint("Arabic Comma", "،")
    with r3[3]:
        if st.button("Color", width='stretch', key="tb_color"): show_hint("Colored Text", r"\textcolor{ECEScyan}{Text}")
    with r3[4]:
        if st.button("Spacing", width='stretch', key="tb_vspace"): show_hint("Vertical Space", r"\vspace{0.5cm}")

def generate_preview(content_latex):
    """
    Generates a standalone PDF snippet. 
    Crucially, uses the active language's preamble to ensure fonts/RTL work.
    """
    preview_filename = "preview_temp"
    preview_tex = f"{preview_filename}.tex"
    preview_pdf = f"{preview_filename}.pdf"
    preview_log = f"{preview_filename}.log"
    
    if os.path.exists(preview_pdf): os.remove(preview_pdf)
    if os.path.exists(preview_log): os.remove(preview_log)
    
    # Construct LaTeX wrapper
    # We include the specific preamble (English or Arabic) and the matching config
    full_latex_code = f"\\documentclass[a4paper,12pt]{{article}}\n"
    full_latex_code += f"\\input{{{PREAMBLE_FILE}}}\n"
    full_latex_code += f"\\input{{{active_config['config']}}}\n"
    full_latex_code += "\\begin{document}\n"
    
    # If Arabic, ensure the environment is set if not handled by preamble globally
    # Ideally preamble_ar.tex has \usepackage{polyglossia} \setmainlanguage{arabic}
    full_latex_code += content_latex
    full_latex_code += "\n\\end{document}"
    
    with open(preview_tex, "w", encoding="utf-8") as f:
        f.write(full_latex_code)
        
    try:
        # ALWAYS use xelatex for best compatibility (required for Arabic, fine for English)
        subprocess.run(["xelatex", "-interaction=nonstopmode", preview_tex], cwd=BASE_DIR, stdout=subprocess.DEVNULL)
        
        if os.path.exists(preview_pdf):
            return preview_pdf, None
        else:
            error_msg = parse_latex_log(os.path.join(BASE_DIR, preview_log))
            return None, error_msg
    except Exception as e:
        return None, str(e)

# ==========================================
# SLOT-BASED CONTENT SYSTEM
# ==========================================
# Replaces the old parse_latex_blocks / reconstruct_latex approach.
# Templates use \ECESContent{slot_id}{default text} markers.
# Edits are saved as plain text in overrides/*.tex files.
# LaTeX formatting is NEVER exposed to the editor.

OVERRIDES_DIR = os.path.join(BASE_DIR, "overrides")
os.makedirs(OVERRIDES_DIR, exist_ok=True)

def extract_slots(tex_content):
    """
    Extract all \\ECESContent{slot_id}{default_text} from a .tex file.
    Returns list of (slot_id, default_text) in order of appearance.
    Handles nested braces in default text (e.g. \\textbf{word} inside content).
    """
    slots = []
    marker = r'\ECESContent{'
    i = 0

    while i < len(tex_content):
        pos = tex_content.find(marker, i)
        if pos == -1:
            break

        # Extract slot_id (between first { and })
        id_start = pos + len(marker)
        id_end = tex_content.find('}', id_start)
        if id_end == -1:
            break
        slot_id = tex_content[id_start:id_end]

        # Skip past "}{" to reach the default text
        if id_end + 1 >= len(tex_content) or tex_content[id_end + 1] != '{':
            i = id_end + 1
            continue
        text_start = id_end + 2

        # Extract default_text handling nested braces
        brace_depth = 1
        j = text_start
        while j < len(tex_content) and brace_depth > 0:
            if tex_content[j] == '{' and tex_content[j-1:j] != '\\':
                brace_depth += 1
            elif tex_content[j] == '}' and tex_content[j-1:j] != '\\':
                brace_depth -= 1
            j += 1

        default_text = tex_content[text_start:j - 1]
        slots.append((slot_id, default_text))
        i = j

    return slots


def get_slot_content(slot_id, default_text):
    """Get current content for a slot: override file if it exists, else default."""
    override_path = os.path.join(OVERRIDES_DIR, f"{slot_id}.tex")
    if os.path.exists(override_path):
        return load_file(override_path), True  # (content, is_overridden)
    return default_text, False


def save_slot(slot_id, content):
    """Save edited content to an override file."""
    override_path = os.path.join(OVERRIDES_DIR, f"{slot_id}.tex")
    save_file(override_path, content)


def reset_slot(slot_id):
    """Remove an override file, reverting the slot to its default text."""
    override_path = os.path.join(OVERRIDES_DIR, f"{slot_id}.tex")
    if os.path.exists(override_path):
        os.remove(override_path)


def get_all_section_slots(section_file_path):
    """
    Load a section .tex file and return all its slots with current content.
    Returns: [(slot_id, current_text, is_overridden, default_text), ...]
    """
    tex_content = load_file(section_file_path)
    raw_slots = extract_slots(tex_content)

    result = []
    for slot_id, default_text in raw_slots:
        current_text, is_overridden = get_slot_content(slot_id, default_text)
        result.append((slot_id, current_text, is_overridden, default_text))

    return result


def reset_all_overrides():
    """Remove all override files (used by factory reset)."""
    if os.path.exists(OVERRIDES_DIR):
        for f in os.listdir(OVERRIDES_DIR):
            if f.endswith(".tex"):
                os.remove(os.path.join(OVERRIDES_DIR, f))


# Human-readable labels for content slots
SLOT_LABELS = {
    # Executive Summary
    "exec_intro": "📄 Introduction Paragraph",
    "exec_box_overall": "📊 Key Findings — Overall Index",
    "exec_box_size": "📏 Key Findings — By Firm Size",
    "exec_box_sector": "🏭 Key Findings — By Sector",
    "exec_box_challenges": "⚠️ Key Findings — Challenges",
    "exec_bpi_analysis": "📈 BPI Performance Analysis",
    "exec_expectations": "🔮 Performance Expectations",
    "exec_size_detail": "📏 Detailed Size Analysis",
    "exec_sector_summary": "🏭 Sector Overview",
    "exec_manufacturing": "🔧 Manufacturing Sector Detail",
    "exec_best_sector": "🌟 Best Performing Sector Detail",
    "exec_challenges_headline": "⚠️ Challenges — Headline",
    "exec_challenges_body": "📋 Challenges — Full Analysis",
    "exec_sme_comparison": "🏢 SMEs vs Large Firms",
    "exec_priorities": "🎯 Business Priorities",
    "exec_macro_global": "🌍 Macro — Global Outlook",
    "exec_macro_local": "🇪🇬 Macro — Local Outlook",
    # Macroeconomic Overview
    "macro_global_intro": "🌍 Global Overview — Introduction",
    "macro_global_growth": "📉 Global Growth Forecasts",
    "macro_global_inflation": "💹 Global Inflation Trends",
    "macro_global_pmi": "📊 Global PMI Analysis",
    "macro_local_intro": "🇪🇬 Local Economy — Introduction",
    "macro_imf_review": "🏦 IMF Review & Outlook",
    "macro_imf_reforms": "📋 Structural Reform Priorities",
    "macro_gdp_growth": "📈 GDP Growth Analysis",
    "macro_inflation": "💰 Inflation Analysis",
    "macro_foreign_bop": "💱 Balance of Payments",
    "macro_foreign_current": "📊 Current Account",
    "macro_foreign_petroleum": "⛽ Petroleum Trade Balance",
    "macro_foreign_assets": "🏦 Net Foreign Assets",
    "macro_foreign_reserves": "💵 International Reserves",
    "macro_foreign_exchange": "💱 Exchange Rate",
    "macro_public_finance": "🏛️ Public Finance",
    # Analysis: Overall Index
    "overall_intro": "📊 Overall Index — Introduction",
    "overall_bpi_text": "📈 BPI Performance Text",
    "overall_expectations": "🔮 Expectations Analysis",
    "overall_size_text": "📏 Performance by Firm Size",
    "overall_expectations_size": "🔮 Expectations by Firm Size",
    "overall_sector_intro": "🏭 Sector Performance Intro",
    "overall_sector_analysis": "📋 Detailed Sector Analysis",
    "overall_sector_outlook_intro": "🔮 Sector Outlook Introduction",
    "overall_sector_outlook": "📊 Sector Outlook Details",
    # Analysis: Constraints
    "constraints_intro": "⚠️ Constraints — Introduction",
    "constraints_main": "📋 Main Constraints Analysis",
    "constraints_by_size_intro": "📏 Constraints by Size — Intro",
    "constraints_by_size": "📊 Constraints by Size — Detail",
    "constraints_by_sector": "🏭 Constraints by Sector",
    "priorities_intro": "🎯 Priorities — Introduction",
    "priorities_main": "📋 Priorities Analysis",
    "priorities_by_size": "📏 Priorities by Firm Size",
    "priorities_by_sector": "🏭 Priorities by Sector",
    "outlook_community": "🔮 Business Community Outlook",
    # Analysis: Sub-Indices
    "sub_performance_intro": "📊 Sub-Indices Performance Intro",
    "sub_production_sales": "🏭 Production & Sales Analysis",
    "sub_prices_wages": "💰 Prices & Wages Analysis",
    "sub_investment_employment": "📈 Investment & Employment",
    "sub_expectations_intro": "🔮 Sub-Indices Expectations Intro",
    "sub_expectations_production": "🏭 Production Expectations",
    "sub_expectations_prices": "💰 Price Expectations",
    "sub_expectations_investment": "📈 Investment Expectations",
}


def get_slot_label(slot_id):
    """Get human-readable label for a slot, with fallback."""
    return SLOT_LABELS.get(slot_id, slot_id.replace("_", " ").title())


# Legacy functions kept for backward compatibility with non-migrated sections
def parse_latex_blocks(content):
    """LEGACY: Line-based parser for sections not yet migrated to slots."""
    lines = content.splitlines()
    blocks = []
    current_chunk = []
    current_type = None
    latex_cmd_pattern = re.compile(r'^(\\|\%|\{|}|\s*\\)')

    for line in lines:
        is_code = bool(latex_cmd_pattern.match(line.strip())) or line.strip() == ""
        line_type = 'code' if is_code else 'text'
        if current_type is None: current_type = line_type

        if line_type != current_type:
            blocks.append({'type': current_type, 'content': "\n".join(current_chunk)})
            current_chunk = [line]
            current_type = line_type
        else:
            current_chunk.append(line)
    if current_chunk:
        blocks.append({'type': current_type, 'content': "\n".join(current_chunk)})
    return blocks

def reconstruct_latex(blocks):
    """LEGACY: Reconstruct LaTeX from blocks for non-migrated sections."""
    return "\n".join([b['content'] for b in blocks])

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    # Attempt to load a local logo; fallback to a sleek CSS banner
    logo_path = os.path.join(STATIC_IMG_DIR, "eces_logo.png")
    if os.path.exists(logo_path):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo_path, width=150) # Adjust 150 up or down to your liking
    else:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #0f172a 0%, #1FBACF 100%); 
                        border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 15px;
                        box-shadow: 0 6px 40px rgba(143,143,143,0.12);'>
                <h2 style='color: white; margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 1px;'>
                    📊 ECES Suite
                </h2>
            </div>
        """, unsafe_allow_html=True)

    # --- LANGUAGE TOGGLE ---
    st.markdown("### 🌍 Language / اللغة")
    selected_lang = st.radio(
        "Select Language",
        ["English", "Arabic"],
        index=0 if st.session_state['language'] == 'English' else 1,
        label_visibility="collapsed",
        horizontal=True
    )
    
    # Update state and rerun if changed to load correct file maps
    if selected_lang != st.session_state['language']:
        st.session_state['language'] = selected_lang
        st.session_state['pdf_ready'] = False # Reset PDF status
        st.rerun()

    st.markdown("---")
    # --- USER INFO & LOGOUT ---
    _role_badge = {"admin": "🔴 Admin", "editor": "🟡 Editor", "viewer": "🟢 Viewer"}.get(
        st.session_state['current_role'], "🟢 Viewer"
    )
    st.markdown(
        f"<div style='font-size:0.82rem; color:#94a3b8; padding:0.25rem 0;'>"
        f"👤 <b style='color:#f1f5f9;'>{st.session_state['current_user']}</b> &nbsp;|&nbsp; {_role_badge}</div>",
        unsafe_allow_html=True
    )
    if st.button("🚪 Logout", use_container_width=True):
        log_activity("LOGOUT")
        for _k in list(st.session_state.keys()):
            del st.session_state[_k]
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = ""
        st.session_state["current_role"] = "viewer"
        st.session_state["last_active"] = 0.0
        st.rerun()

    # ── Self-Service Password Change ────────────────────────
    with st.expander("🔑 Change Password" if not is_arabic else "🔑 تغيير كلمة المرور", expanded=False):
        with st.form("change_pw_form", clear_on_submit=True):
            _cur_pw = st.text_input("Current Password" if not is_arabic else "كلمة المرور الحالية", type="password")
            _new_pw = st.text_input("New Password" if not is_arabic else "كلمة المرور الجديدة", type="password")
            _confirm_pw = st.text_input("Confirm New Password" if not is_arabic else "تأكيد كلمة المرور", type="password")
            _pw_submit = st.form_submit_button("Update" if not is_arabic else "تحديث", use_container_width=True)

            if _pw_submit:
                _users = load_users()
                _me = st.session_state["current_user"]
                if _me not in _users:
                    st.error("User not found.")
                elif not verify_password(_cur_pw, _users[_me]["password"]):
                    st.error("Current password is incorrect." if not is_arabic else "كلمة المرور الحالية غير صحيحة.")
                elif len(_new_pw) < 6:
                    st.error("New password must be at least 6 characters." if not is_arabic else "يجب أن تكون كلمة المرور الجديدة 6 أحرف على الأقل.")
                elif _new_pw != _confirm_pw:
                    st.error("Passwords do not match." if not is_arabic else "كلمتا المرور غير متطابقتين.")
                else:
                    _users[_me]["password"] = hash_password(_new_pw)
                    save_users(_users)
                    log_activity("PASSWORD_CHANGE", _me)
                    st.success("Password updated!" if not is_arabic else "تم تحديث كلمة المرور!")

    st.markdown("---")
    st.markdown("### Control Center")

    # Build nav based on role
    _allowed = ROLE_PERMISSIONS.get(st.session_state['current_role'], ["📝 Report Sections"])
    _en_to_ar = {
        "📝 Report Sections":      "📝 أقسام التقرير",
        "⚙️ Report Variables":     "⚙️ متغيرات التقرير",
        "📊 Chart Manager":        "📊 إدارة الرسوم البيانية",
        "🚀 Finalize & Publish":   "🚀 إنهاء ونشر",
        "📋 Activity Log":         "📋 سجل النشاط",
        "👥 User Management":      "👥 User Management",
    }

    if st.session_state['language'] == 'Arabic':
        _display_options = [_en_to_ar.get(v, v) for v in _allowed]
    else:
        _display_options = _allowed

    _ar_to_en = {v: k for k, v in _en_to_ar.items()}

    selected_view_display = st.radio(
        "Navigation",
        _display_options,
        label_visibility="collapsed"
    )

    # Normalize view variable to English key
    selected_view = _ar_to_en.get(selected_view_display, selected_view_display)
    
    st.markdown("---")
    if is_arabic:
        st.info("💡 **تلميح:** 'المعاينة' تقوم بتجميع القسم الحالي فقط.")
    else:
        st.info("💡 **Tip:** 'Preview' compiles the current section only.")

    st.markdown("---")

    # Factory Reset is admin-only
    if st.session_state.get("current_role") == "admin":
        st.markdown("### 🔄 Factory Reset")

        reset_help = "استعادة الملفات الأصلية" if is_arabic else "Restore original templates"

        with st.expander(reset_help, expanded=False):
            col_reset1, col_reset2 = st.columns(2)

            with col_reset1:
                if st.button("Reset Current File", use_container_width=True, key="reset_current"):
                    if 'current_section_name' in locals():
                        filename = os.path.basename(SECTION_MAP.get(st.session_state.get('current_section_name', '')))
                        success, msg = factory_reset(target=filename)
                        if success:
                            log_activity("FACTORY_RESET", detail=f"file: {filename}")
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.info("Open a section first to reset it.")

            with col_reset2:
                if st.button("Reset All", use_container_width=True, type="primary", key="reset_all_trigger"):
                    st.session_state['confirm_reset_all'] = True
                    st.rerun()

            # Reset only content overrides (slot edits)
            if st.button(
                "🔄 Reset All Content Edits" if not is_arabic else "🔄 مسح جميع التعديلات",
                use_container_width=True, key="reset_overrides"
            ):
                success, msg = factory_reset(target="overrides")
                if success:
                    log_activity("FACTORY_RESET", detail="overrides only")
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            # Confirmation dialog
            if st.session_state.get('confirm_reset_all'):
                st.warning("⚠️ This will restore ALL files to original state!")
                col_yes, col_no = st.columns(2)

                with col_yes:
                    if st.button("✓ Confirm", use_container_width=True, key="confirm_yes"):
                        success, msg = factory_reset(target="all")
                        st.session_state['confirm_reset_all'] = False
                        if success:
                            log_activity("FACTORY_RESET", detail="all files")
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

                with col_no:
                    if st.button("✗ Cancel", use_container_width=True, key="confirm_no"):
                        st.session_state['confirm_reset_all'] = False
                        st.rerun()

# ==========================================
# 5. VIEW: REPORT SECTIONS (SLOT-BASED)
# ==========================================
if selected_view == "📝 Report Sections":
    header_text = "📝 محرر المحتوى والمعاينة" if is_arabic else "📝 Content Editor & Preview"
    st.markdown(f"## {header_text}")

    # Section Selector (horizontal radio — tab-like)
    section_keys = list(SECTION_MAP.keys())
    current_section_name = st.radio(
        "اختر القسم" if is_arabic else "Select Section",
        section_keys,
        horizontal=True,
        label_visibility="collapsed"
    )

    if 'last_section' not in st.session_state:
        st.session_state['last_section'] = current_section_name

    if st.session_state['last_section'] != current_section_name:
        st.session_state['last_section'] = current_section_name
        st.session_state['active_preview_pdf'] = None  # Clear the persistent preview

    current_file_path = os.path.join(BASE_DIR, SECTION_MAP[current_section_name])

    # Check if file exists
    if not os.path.exists(current_file_path):
        save_file(current_file_path, "% New Section")

    # Detect whether this section has been migrated to the slot system
    raw_content = load_file(current_file_path)
    slots = extract_slots(raw_content)
    is_slot_based = len(slots) > 0

    # Compute section slots early (for progress bar + editor)
    section_slots = get_all_section_slots(current_file_path) if is_slot_based else []
    _total_slots = len(section_slots)
    _edited_slots = sum(1 for _, _, ov, _ in section_slots if ov)

    # Breadcrumb context bar + progress
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
        st.progress(_edited_slots / _total_slots, text=f"{_edited_slots}/{_total_slots} slots customized")

    st.markdown("---")
    col_editor, col_preview = st.columns([3, 2])

    # ── EDITOR ──────────────────────────────────────────────
    with col_editor:
        st.subheader("Edit Content" if not is_arabic else "تحرير المحتوى")

        if is_slot_based:
            # ── SLOT-BASED EDITOR (migrated sections) ───────
            # section_slots already computed above for progress bar

            # LaTeX toolbar (admin & editor only)
            if st.session_state.get('current_role') in ('admin', 'editor'):
                with st.expander("🛠️ LaTeX Quick Tools" if not is_arabic else "🛠️ أدوات LaTeX السريعة", expanded=False):
                    render_toolbar()

            with st.container(height=800):
                with st.form(f"slot_form_{current_section_name}"):
                    edited_slots = {}
                    reset_flags = {}

                    for slot_id, current_text, is_overridden, default_text in section_slots:
                        label = get_slot_label(slot_id)

                        # Status indicator
                        if is_overridden:
                            st.markdown(
                                f"**{label}** &ensp;"
                                f"<span style='background:#CF34A9; color:white; padding:3px 10px; "
                                f"border-radius:50px; font-size:0.75em; font-weight:600;'>✏️ Edited</span>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"**{label}** &ensp;"
                                f"<span style='background:transparent; color:#94a3b8; padding:3px 10px; "
                                f"border-radius:50px; font-size:0.75em; border:1px solid #475569;'>📄 Default</span>",
                                unsafe_allow_html=True
                            )

                        # Text area
                        h = max(80, min(400, len(current_text) // 2))
                        edited_slots[slot_id] = st.text_area(
                            label,
                            value=current_text,
                            height=int(h),
                            label_visibility="collapsed",
                            key=f"slot_{st.session_state['language']}_{slot_id}"
                        )

                        # Reset checkbox (only show for overridden slots)
                        if is_overridden:
                            reset_flags[slot_id] = st.checkbox(
                                "↩️ Reset to default" if not is_arabic else "↩️ إعادة للنص الأصلي",
                                key=f"reset_{slot_id}",
                                value=False
                            )

                        st.markdown(
                            "<div style='height:8px; border-bottom:1px solid #334155; "
                            "margin-bottom:12px;'></div>",
                            unsafe_allow_html=True
                        )

                    st.markdown("---")
                    btn_save_txt = "💾 حفظ جميع التعديلات" if is_arabic else "💾 Save All Changes"
                    save_clicked = st.form_submit_button(
                        btn_save_txt, type="primary", use_container_width=True
                    )

            # Handle save
            if save_clicked:
                # Build a default-text lookup
                default_map = {sid: dtxt for sid, dtxt in extract_slots(raw_content)}
                saved_count = 0
                reset_count = 0

                for slot_id, edited_text in edited_slots.items():
                    # Check if user wants to reset this slot
                    if reset_flags.get(slot_id, False):
                        reset_slot(slot_id)
                        reset_count += 1
                    else:
                        default = default_map.get(slot_id, "")
                        if edited_text.strip() != default.strip():
                            save_slot(slot_id, edited_text)
                            saved_count += 1
                        else:
                            # Text matches default — remove any stale override
                            reset_slot(slot_id)

                if saved_count > 0 or reset_count > 0:
                    parts = []
                    if saved_count > 0:
                        parts.append(f"{saved_count} saved")
                    if reset_count > 0:
                        parts.append(f"{reset_count} reset")
                    log_activity("CONTENT_EDIT", detail=f"{current_section_name}: {', '.join(parts)}")
                    st.toast(f"✅ {current_section_name}: {', '.join(parts)}")
                else:
                    st.toast(f"ℹ️ No changes detected in {current_section_name}")

        else:
            # ── LEGACY EDITOR (non-migrated sections) ───────
            st.caption(
                "⚠️ This section uses the legacy editor. "
                "Migrate to slot system for safer editing."
                if not is_arabic else
                "⚠️ هذا القسم يستخدم المحرر القديم. انقل إلى نظام الـ Slots للتحرير الآمن."
            )

            blocks = parse_latex_blocks(raw_content)

            with st.container(height=800):
                with st.form(f"legacy_form_{current_section_name}"):
                    edited_blocks = []
                    for idx, block in enumerate(blocks):
                        if block['type'] == 'code':
                            edited_blocks.append(block)
                        else:
                            h = max(100, len(block['content']) // 1.5)
                            new_text = st.text_area(
                                f"##",
                                value=block['content'],
                                height=int(h),
                                label_visibility="collapsed",
                                key=f"legacy_{st.session_state['language']}_{current_section_name}_{idx}"
                            )
                            edited_blocks.append({'type': 'text', 'content': new_text})
                            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

                    st.markdown("---")
                    btn_save_txt = "💾 حفظ الملف" if is_arabic else "💾 Save to File"
                    legacy_save = st.form_submit_button(
                        btn_save_txt, type="primary", use_container_width=True
                    )

            legacy_draft = reconstruct_latex(edited_blocks)

            if legacy_save:
                save_file(current_file_path, legacy_draft)
                log_activity("CONTENT_EDIT", detail=f"{current_section_name} (legacy)")
                st.toast(f"✅ Saved {current_section_name}")

    # ── PREVIEW ─────────────────────────────────────────────
    with col_preview:
        st.subheader("Live Preview" if not is_arabic else "المعاينة الحية")

        btn_prev_txt = "👁️ Generate Preview" if not is_arabic else "👁️ إنشاء معاينة"
        if st.button(btn_prev_txt, use_container_width=True, type="primary",
                     key=f"preview_{current_section_name}"):
            st.session_state['preview_clicked'] = True
            st.rerun()

        preview_container = st.empty()

        if st.session_state.get('preview_clicked'):
            status_txt = "جاري تجميع ملف المعاينة..." if is_arabic else "Compiling Preview..."
            with st.status(status_txt, expanded=True) as status:
                if is_slot_based:
                    # Slot-based: the .tex template is never modified.
                    # XeLaTeX reads override files at compile time via \ECESContent.
                    preview_content = load_file(current_file_path)
                else:
                    # Legacy: use the reconstructed content
                    preview_content = reconstruct_latex(edited_blocks) if 'edited_blocks' in dir() else raw_content

                pdf_path, error_msg = generate_preview(preview_content)

                if pdf_path and os.path.exists(pdf_path):
                    status.update(label="Ready!", state="complete", expanded=False)
                    with preview_container.container():
                        display_pdf(pdf_path)
                    st.session_state['preview_clicked'] = False
                else:
                    status.update(label="Failed", state="error")
                    st.error("⚠️ LaTeX Compilation Error")
                    with st.expander("Error Details", expanded=True):
                        st.code(error_msg, language="tex")
        else:
            preview_container.info("Click Preview / اضغط على المعاينة")

# ==========================================
# 6. VIEW: VARIABLES
# ==========================================
elif selected_view == "⚙️ Report Variables":
    header = "⚙️ الإعدادات العامة (Variables)" if is_arabic else "⚙️ Global Configuration"
    st.markdown(f"## {header}")
    
    st.markdown(f"""
    <div class="css-card">
    Current Configuration File: <code>{active_config['config']}</code>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists(CONFIG_FILE):
        raw_config = load_file(CONFIG_FILE)
        pattern = re.compile(r'\\newcommand\{\\(\w+)\}\{(.*?)\}')
        matches = pattern.findall(raw_config)
        
        with st.form("config_form"):
            updates = {}
            cols = st.columns(2)
            # RTL adjustment for inputs
            
            for i, (key, val) in enumerate(matches):
                col = cols[i % 2]
                with col:
                    updates[key] = st.text_input(f"Value for: {key}", value=val)
            
            st.markdown("---")
            btn_txt = "💾 تحديث المتغيرات" if is_arabic else "💾 Update Variables"
            if st.form_submit_button(btn_txt, type="primary"):
                new_config = raw_config
                for key, val in updates.items():
                    safe_val = val.replace('\\', '\\\\')
                    regex_replace = r'(\\newcommand\{\\' + key + r'\}\{)(.*?)(\})'
                    new_config = re.sub(regex_replace, r'\g<1>' + safe_val + r'\g<3>', new_config)
                
                save_file(CONFIG_FILE, new_config)
                st.toast("Updated!", icon="⚙️")
                st.rerun()
    else:
        st.error(f"{active_config['config']} not found.")

# ==========================================
# 7. VIEW: CHART MANAGER (Shared)
# ==========================================
elif selected_view == "📊 Chart Manager":
    header = "📊 إدارة الرسوم البيانية والصور" if is_arabic else "📊 Image & Chart Management"
    st.markdown(f"## {header}")
    
    # Create Tabs for cleaner organization
    tab_charts, tab_static = st.tabs([
        "📈 الرسوم البيانية (عربي)" if is_arabic else "📈 Charts (English)", 
        "🖼️ صور ثابتة (مشتركة)" if is_arabic else "🖼️ Static Images (Shared)"
    ])
    
    # Reusable function to render images for any given directory
    def render_image_manager(directory):
        if os.path.exists(directory):
            # Allowed extensions added
            files = sorted([f for f in os.listdir(directory) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
            
            if not files:
                st.info("لا توجد صور في هذا المجلد." if is_arabic else "No images found in this directory.")
                return
                
            cols = st.columns(3)
            for idx, filename in enumerate(files):
                col = cols[idx % 3]
                filepath = os.path.join(directory, filename)
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{filename}**")
                        st.image(filepath, use_container_width=True) # Updated to modern Streamlit syntax
                        
                        lbl = "استبدال" if is_arabic else "Replace"
                        # Unique keys to prevent Streamlit DuplicateKey error
                        uploaded = st.file_uploader(f"{lbl} {filename}", type=["png", "jpg", "jpeg"], key=f"up_{directory}_{filename}")
                        
                        if uploaded:
                            with open(filepath, "wb") as f:
                                f.write(uploaded.getbuffer())
                            st.toast(f"✅ Updated {filename}")
                            st.rerun()
        else:
            st.error("Directory not found.")

    # Render inside respective tabs
    with tab_charts:
        st.markdown(f"**Active Directory:** `{os.path.basename(ACTIVE_CHARTS_DIR)}`")
        render_image_manager(ACTIVE_CHARTS_DIR)
        
    with tab_static:
        st.markdown(f"**Active Directory:** `{os.path.basename(STATIC_IMG_DIR)}`")
        render_image_manager(STATIC_IMG_DIR)

# ==========================================
# 8. VIEW: COMPILE FINAL
# ==========================================
elif selected_view == "🚀 Finalize & Publish":
    header = "🚀 إنهاء ونشر التقرير" if is_arabic else "🚀 Compile Final Report"
    st.markdown(f"## {header}")
    
    c1, c2 = st.columns([2, 1])
    target_main = active_config["main"]
    
    with c1:
        msg = f"""
        <div class="css-card">
        <b>Target File: {target_main}</b><br>
        Using <b>XeLaTeX</b> engine to support {st.session_state['language']} fonts and layout.
        </div>
        """
        st.markdown(msg, unsafe_allow_html=True)
        
        btn_txt = "بدء التجميع الكامل" if is_arabic else "Generate Full PDF"
        
        if st.button(btn_txt, type="primary"):
            with st.status("Processing..." if not is_arabic else "جاري المعالجة...", expanded=True) as status:
                try:
                    # IMPORTANT: Arabic needs xelatex
                    cmd = ["xelatex", "-interaction=nonstopmode", target_main]
                    
                    st.write("Running xelatex (Pass 1)...")
                    subprocess.run(cmd, cwd=BASE_DIR, stdout=subprocess.DEVNULL)
                    
                    st.write("Running xelatex (Pass 2 for ToC)...")
                    subprocess.run(cmd, cwd=BASE_DIR, stdout=subprocess.DEVNULL)
                    
                    expected_pdf = target_main.replace(".tex", ".pdf")
                    if os.path.exists(os.path.join(BASE_DIR, expected_pdf)):
                        status.update(label="Success!", state="complete", expanded=False)
                        st.session_state['pdf_ready'] = True
                        st.session_state['final_pdf_name'] = expected_pdf
                    else:
                        status.update(label="Compilation Failed", state="error")
                        st.error("PDF was not created. Check logs.")
                except Exception as e:
                    status.update(label="Error", state="error")
                    st.error(str(e))

    with c2:
        if st.session_state.get('pdf_ready'):
            final_name = st.session_state.get('final_pdf_name', 'output.pdf')
            pdf_path = os.path.join(BASE_DIR, final_name)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF" if not is_arabic else "📥 تحميل التقرير",
                    data=f,
                    file_name=final_name,
                    mime="application/pdf",
                    type="primary",
                    width='stretch'
                )

# ==========================================
# 8b. VIEW: ACTIVITY LOG (Admin only)
# ==========================================
elif selected_view == "📋 Activity Log":
    if st.session_state.get('current_role') != 'admin':
        st.error("🔒 Access denied. Admin only.")
        st.stop()

    header = "📋 سجل النشاط" if is_arabic else "📋 Activity Log"
    st.markdown(f"## {header}")

    records = parse_activity_log()

    # ── Summary Metrics ─────────────────────────────────
    from datetime import date, timedelta
    _today_str = str(date.today())
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Total Events" if not is_arabic else "إجمالي الأحداث", len(records))
    mc2.metric(
        "Today" if not is_arabic else "اليوم",
        sum(1 for r in records if r["date"] == _today_str)
    )
    mc3.metric(
        "Unique Users" if not is_arabic else "المستخدمون",
        len(set(r["user"] for r in records))
    )
    mc4.metric(
        "Content Edits" if not is_arabic else "تعديلات المحتوى",
        sum(1 for r in records if r["action"] == "CONTENT_EDIT")
    )

    st.markdown("")

    # ── Filters ─────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        all_users = sorted(set(r["user"] for r in records))
        _all_label = "الكل" if is_arabic else "All"
        filter_user = st.selectbox(
            "User" if not is_arabic else "المستخدم",
            [_all_label] + all_users
        )

    with col_f2:
        all_actions = sorted(set(r["action"] for r in records))
        filter_action = st.selectbox(
            "Action" if not is_arabic else "الإجراء",
            [_all_label] + all_actions
        )

    with col_f3:
        _default_start = date.today() - timedelta(days=30)
        date_range = st.date_input(
            "Date Range" if not is_arabic else "نطاق التاريخ",
            value=(_default_start, date.today()),
            max_value=date.today()
        )

    # ── Apply Filters ───────────────────────────────────
    filtered = records
    if filter_user != _all_label:
        filtered = [r for r in filtered if r["user"] == filter_user]
    if filter_action != _all_label:
        filtered = [r for r in filtered if r["action"] == filter_action]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        _start, _end = str(date_range[0]), str(date_range[1])
        filtered = [r for r in filtered if _start <= r["date"] <= _end]

    # Reverse chronological, cap at 500
    filtered = list(reversed(filtered))
    _display_cap = 500
    _total_filtered = len(filtered)
    filtered = filtered[:_display_cap]

    st.markdown("---")

    # ── Data Table ──────────────────────────────────────
    if filtered:
        import pandas as pd
        df = pd.DataFrame(filtered)
        st.dataframe(
            df[["timestamp", "user", "action", "detail"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": st.column_config.TextColumn(
                    "Timestamp" if not is_arabic else "الوقت", width="medium"
                ),
                "user": st.column_config.TextColumn(
                    "User" if not is_arabic else "المستخدم", width="small"
                ),
                "action": st.column_config.TextColumn(
                    "Action" if not is_arabic else "الإجراء", width="small"
                ),
                "detail": st.column_config.TextColumn(
                    "Details" if not is_arabic else "التفاصيل", width="large"
                ),
            }
        )
        _cap_note = f" (showing latest {_display_cap})" if _total_filtered > _display_cap else ""
        st.caption(
            f"{'عرض' if is_arabic else 'Showing'} {len(filtered)} "
            f"{'من' if is_arabic else 'of'} {len(records)} "
            f"{'سجل' if is_arabic else 'entries'}{_cap_note}"
        )
    else:
        st.info("No matching records." if not is_arabic else "لا توجد سجلات مطابقة.")

# ==========================================
# 9. VIEW: USER MANAGEMENT (Admin only)
# ==========================================
elif selected_view == "👥 User Management":
    # Double-check permission (defence-in-depth)
    if st.session_state.get('current_role') != 'admin':
        st.error("🔒 Access denied. Admin only.")
        st.stop()

    st.markdown("## 👥 User Management")
    st.markdown(
        "<div class='css-card'>Manage application users, roles, and access. "
        "Changes take effect on the next login.</div>",
        unsafe_allow_html=True
    )
    st.markdown("")

    users = load_users()
    ROLE_OPTIONS = ["admin", "editor", "viewer"]

    # ── ADD USER FORM ────────────────────────────────────────────
    with st.expander("➕ Add New User", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                new_username = st.text_input("Username", placeholder="e.g. sara")
            with c2:
                new_password = st.text_input("Password", type="password", placeholder="Min 6 characters")
            with c3:
                new_role = st.selectbox("Role", ROLE_OPTIONS, index=1)
            submitted = st.form_submit_button("✅ Create User", type="primary", use_container_width=True)

            if submitted:
                new_username = new_username.strip()
                if not new_username:
                    st.error("Username cannot be empty.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_username in users:
                    st.error(f"User '{new_username}' already exists.")
                else:
                    users[new_username] = {"password": hash_password(new_password), "role": new_role, "enabled": True}
                    save_users(users)
                    log_activity("USER_CREATED", detail=f"{new_username} as {new_role}")
                    st.success(f"✅ User '{new_username}' created as **{new_role}**.")
                    st.rerun()

    st.markdown("### 👤 All Users")

    # ── USER TABLE ───────────────────────────────────────────────
    # Header row
    hc = st.columns([2, 2, 2, 1, 1, 1])
    for col, label in zip(hc, ["**Username**", "**Password**", "**Role**", "**Status**", "**Save**", "**Delete**"]):
        col.markdown(label)
    st.markdown("<hr style='margin:0.25rem 0 0.75rem 0; border-color:#475569;'>", unsafe_allow_html=True)

    for username, info in list(users.items()):
        col_user, col_pass, col_role, col_status, col_save, col_del = st.columns([2, 2, 2, 1, 1, 1])

        with col_user:
            badge = " 🧑‍💼 **(you)**" if username == st.session_state['current_user'] else ""
            st.markdown(f"`{username}`{badge}")

        with col_pass:
            new_pass = st.text_input(
                "pw", value="",
                type="password",
                label_visibility="collapsed",
                key=f"pw_{username}",
                placeholder="New password (leave blank to keep)"
            )

        with col_role:
            current_role_idx = ROLE_OPTIONS.index(info.get("role", "viewer"))
            new_role = st.selectbox(
                "role", ROLE_OPTIONS,
                index=current_role_idx,
                label_visibility="collapsed",
                key=f"role_{username}"
            )

        with col_status:
            is_enabled = info.get("enabled", True)
            status_label = "✅ On" if is_enabled else "⛔ Off"
            if st.button(status_label, key=f"toggle_{username}", use_container_width=True):
                if username == st.session_state['current_user']:
                    st.toast("⚠️ You cannot disable your own account.", icon="⚠️")
                else:
                    users[username]["enabled"] = not is_enabled
                    save_users(users)
                    st.rerun()

        with col_save:
            if st.button("💾", key=f"save_{username}", use_container_width=True, help="Save changes"):
                if new_pass and len(new_pass) < 6:
                    st.toast(f"⚠️ Password too short for {username}.", icon="⚠️")
                elif username == st.session_state['current_user'] and new_role != "admin":
                    st.toast("⚠️ You cannot downgrade your own admin role.", icon="⚠️")
                else:
                    if new_pass:
                        users[username]["password"] = hash_password(new_pass)
                    users[username]["role"] = new_role
                    save_users(users)
                    log_activity("USER_EDITED", detail=f"{username} → role={new_role}" + (", password changed" if new_pass else ""))
                    st.toast(f"✅ Saved changes for {username}.", icon="✅")
                    st.rerun()

        with col_del:
            if username == st.session_state['current_user']:
                st.markdown("<span title='Cannot delete yourself' style='color:#64748b; cursor:not-allowed;'>🗑️</span>", unsafe_allow_html=True)
            else:
                if st.button("🗑️", key=f"del_{username}", use_container_width=True, help=f"Delete {username}"):
                    st.session_state[f"confirm_del_{username}"] = True
                    st.rerun()

        # Inline delete confirmation
        if st.session_state.get(f"confirm_del_{username}"):
            st.warning(f"⚠️ Delete user **{username}**? This cannot be undone.")
            cc1, cc2, _ = st.columns([1, 1, 4])
            with cc1:
                if st.button("✓ Yes, delete", key=f"confirm_del_yes_{username}", type="primary"):
                    del users[username]
                    save_users(users)
                    st.session_state.pop(f"confirm_del_{username}", None)
                    log_activity("USER_DELETED", detail=username)
                    st.toast(f"🗑️ User '{username}' deleted.", icon="🗑️")
                    st.rerun()
            with cc2:
                if st.button("✗ Cancel", key=f"confirm_del_no_{username}"):
                    st.session_state.pop(f"confirm_del_{username}", None)
                    st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── ROLE LEGEND ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Role Permissions")
    lc = st.columns(3)
    role_desc = {
        "🔴 Admin":   "Full access — all views + User Management",
        "🟡 Editor":  "Report Sections, Variables, Chart Manager",
        "🟢 Viewer":  "Read-only access — Report Sections only",
    }
    for col, (badge, desc) in zip(lc, role_desc.items()):
        col.markdown(f"<div class='css-card'><b>{badge}</b><br><small style='color:#94a3b8;'>{desc}</small></div>", unsafe_allow_html=True)