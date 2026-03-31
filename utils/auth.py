"""
Authentication, session management, and activity logging.
No Streamlit calls except where session_state / st.toast are unavoidable.
"""
import json
import logging
import re
import time

import bcrypt
import streamlit as st

from utils.config import USERS_FILE, ACTIVITY_LOG, SESSION_TIMEOUT_MINUTES

# ── Activity Logger ──────────────────────────────────────────────────────────
_activity_logger = logging.getLogger("eces_activity")
_activity_logger.setLevel(logging.INFO)
if not _activity_logger.handlers:
    _fh = logging.FileHandler(ACTIVITY_LOG, encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    _activity_logger.addHandler(_fh)


def log_activity(action: str, user: str = "", detail: str = ""):
    """Write a structured line to activity.log."""
    user = user or st.session_state.get("current_user", "unknown")
    _activity_logger.info(f"[{user}] {action}" + (f" — {detail}" if detail else ""))


def parse_activity_log() -> list:
    """Parse activity.log into structured records for the Activity Log viewer."""
    import os
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
                line,
            )
            if match:
                records.append({
                    "timestamp": match.group(1),
                    "date":      match.group(1)[:10],
                    "user":      match.group(2),
                    "action":    match.group(3),
                    "detail":    match.group(4) or "",
                })
    return records


# ── Password Helpers ─────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, stored: str) -> bool:
    if stored.startswith("$2b$") or stored.startswith("$2a$"):
        return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
    return plain == stored  # legacy plaintext (auto-migrated on login)


# ── User Store ───────────────────────────────────────────────────────────────
def load_users() -> dict:
    """Load from users.json; falls back to st.secrets['users_json'] (raw JSON string) for cloud deployment."""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        pass
    try:
        return json.loads(st.secrets["users_json"])
    except Exception:
        return {}


def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


# ── Session Helpers ───────────────────────────────────────────────────────────
def setup_session_state():
    """Initialise required session-state keys on cold start."""
    defaults = [
        ("authenticated", False),
        ("current_user", ""),
        ("current_role", "viewer"),
        ("last_active", 0.0),
    ]
    for key, val in defaults:
        if key not in st.session_state:
            st.session_state[key] = val


def _session_expired() -> bool:
    last = st.session_state.get("last_active", 0.0)
    if last == 0.0:
        return False
    return (time.time() - last) > SESSION_TIMEOUT_MINUTES * 60


def _touch_session():
    st.session_state["last_active"] = time.time()


# ── Login ─────────────────────────────────────────────────────────────────────
def check_login():
    """on_click handler for the login form submit button."""
    username = st.session_state["login_user"].strip()
    password = st.session_state["login_pass"]
    users = load_users()

    if username in users:
        user = users[username]
        if user.get("enabled", True) and verify_password(password, user["password"]):
            # Auto-migrate legacy plaintext password to bcrypt
            if not (user["password"].startswith("$2b$") or user["password"].startswith("$2a$")):
                users[username]["password"] = hash_password(password)
                save_users(users)

            st.session_state["authenticated"] = True
            st.session_state["current_user"]  = username
            st.session_state["current_role"]  = user.get("role", "viewer")
            _touch_session()
            log_activity("LOGIN", username)
            st.toast(f"Welcome back, {username}!", icon="🔓")
            return
    st.error("❌ Invalid username or password, or account is disabled.")
