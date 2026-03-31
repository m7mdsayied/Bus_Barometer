"""View: Activity Log — audit trail with filters and CSV export (admin only)."""
import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from utils.auth import parse_activity_log
from utils.content import page_header

# ── Action badge styling map ──────────────────────────────────────────────────
_BADGE_MAP = {
    "LOGIN":          ("rgba(31,186,207,0.15)",  "#1FBACF",  "LOGIN"),
    "LOGOUT":         ("rgba(100,116,139,0.15)", "#94a3b8",  "LOGOUT"),
    "SESSION_TIMEOUT":("rgba(100,116,139,0.15)", "#94a3b8",  "TIMEOUT"),
    "PASSWORD_CHANGE":("rgba(99,102,241,0.15)",  "#818cf8",  "PASSWD"),
    "CHART_UPDATED":  ("rgba(207,52,169,0.15)",  "#CF34A9",  "CHART ✎"),
    "CHART_UPLOADED": ("rgba(207,52,169,0.15)",  "#CF34A9",  "CHART +"),
    "CHART_DELETED":  ("rgba(239,68,68,0.15)",   "#ef4444",  "CHART ✕"),
    "CONTENT_EDIT":   ("rgba(245,158,11,0.15)",  "#f59e0b",  "EDIT"),
    "SECTION_EDITED": ("rgba(245,158,11,0.15)",  "#f59e0b",  "SECTION"),
    "FACTORY_RESET":  ("rgba(239,68,68,0.15)",   "#ef4444",  "RESET"),
    "ISSUE_CREATED":  ("rgba(34,197,94,0.15)",   "#22c55e",  "ISSUE +"),
    "ISSUE_LOADED":   ("rgba(34,197,94,0.15)",   "#22c55e",  "ISSUE ↺"),
    "USER_CREATED":   ("rgba(139,92,246,0.15)",  "#a78bfa",  "USER +"),
    "USER_EDITED":    ("rgba(139,92,246,0.15)",  "#a78bfa",  "USER ✎"),
    "USER_DELETED":   ("rgba(239,68,68,0.15)",   "#ef4444",  "USER ✕"),
}

def _action_badge(action: str) -> str:
    action_up = action.upper()
    bg, color, label = _BADGE_MAP.get(
        action_up,
        ("rgba(100,116,139,0.10)", "#64748b", action_up[:10]),
    )
    return (
        f'<span style="display:inline-block;background:{bg};color:{color};'
        f'font-size:0.68rem;font-weight:700;letter-spacing:0.06em;'
        f'padding:2px 8px;border-radius:4px;border:1px solid {color}55;white-space:nowrap;">'
        f'{label}</span>'
    )

def _render_activity_table(df: pd.DataFrame):
    rows_html = ""
    for _, row in df.iterrows():
        badge  = _action_badge(str(row.get("action", "")))
        user   = str(row.get("user", "—"))
        ts     = str(row.get("timestamp", ""))
        detail = str(row.get("detail", ""))
        rows_html += (
            f'<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">'
            f'<td style="padding:9px 14px;white-space:nowrap;">{badge}</td>'
            f'<td style="padding:9px 14px;color:#e2e8f0;font-size:0.88rem;">{user}</td>'
            f'<td style="padding:9px 14px;color:#64748b;font-size:0.82rem;white-space:nowrap;">{ts}</td>'
            f'<td style="padding:9px 14px;color:#94a3b8;font-size:0.85rem;">{detail}</td>'
            f'</tr>'
        )
    th = (
        "padding:9px 14px;text-align:left;color:#475569;font-size:0.72rem;"
        "font-weight:700;letter-spacing:0.07em;text-transform:uppercase;"
    )
    st.markdown(
        f'<div style="overflow-x:auto;border-radius:10px;background:#1e293b;'
        f'border:1px solid rgba(255,255,255,0.07);">'
        f'<table style="width:100%;border-collapse:collapse;min-width:500px;">'
        f'<thead><tr style="border-bottom:2px solid rgba(255,255,255,0.08);">'
        f'<th style="{th}">Action</th><th style="{th}">User</th>'
        f'<th style="{th}">Timestamp</th><th style="{th}">Detail</th>'
        f'</tr></thead><tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def render(ctx):
    if st.session_state.get("current_role") != "admin":
        st.error("🔒 Access denied. Admin only.")
        st.stop()

    page_header(
        "📋", "Activity Log",
        "Audit trail of all user actions. Filter by user, action type, or date range.",
        "#f97316",
    )

    records = parse_activity_log()

    # Summary metrics
    _today_str = str(date.today())
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Total Events", len(records))
    mc2.metric("Today", sum(1 for r in records if r["date"] == _today_str))
    mc3.metric("Unique Users", len(set(r["user"] for r in records)))
    mc4.metric("Content Edits", sum(1 for r in records if r["action"] == "CONTENT_EDIT"))

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        all_users = sorted(set(r["user"] for r in records))
        filter_user = st.selectbox("User", ["All"] + all_users)
    with col_f2:
        all_actions = sorted(set(r["action"] for r in records))
        filter_action = st.selectbox("Action", ["All"] + all_actions)
    with col_f3:
        _default_start = date.today() - timedelta(days=30)
        date_range = st.date_input(
            "Date Range", value=(_default_start, date.today()), max_value=date.today()
        )

    # Apply filters
    filtered = records
    if filter_user != "All":
        filtered = [r for r in filtered if r["user"] == filter_user]
    if filter_action != "All":
        filtered = [r for r in filtered if r["action"] == filter_action]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        _start, _end = str(date_range[0]), str(date_range[1])
        filtered = [r for r in filtered if _start <= r["date"] <= _end]

    filtered = list(reversed(filtered))
    _display_cap = 500
    _total_filtered = len(filtered)
    filtered = filtered[:_display_cap]

    st.divider()

    if filtered:
        df = pd.DataFrame(filtered)
        _render_activity_table(df[["timestamp", "user", "action", "detail"]])
        _cap_note = f" (showing latest {_display_cap})" if _total_filtered > _display_cap else ""
        col_cap, col_export = st.columns([3, 1])
        with col_cap:
            st.caption(f"Showing {len(filtered)} of {len(records)} entries{_cap_note}")
        with col_export:
            _csv_buf = io.StringIO()
            df[["timestamp", "user", "action", "detail"]].to_csv(_csv_buf, index=False)
            st.download_button(
                label="📥 Export CSV",
                data=_csv_buf.getvalue(),
                file_name="activity_log.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.info("No matching records.")
