"""View: User Management — create, edit, enable/disable, delete users (admin only)."""
import os
import streamlit as st

from utils.auth import hash_password, load_users, log_activity, save_users
from utils.content import page_header
from utils import storage as _storage
from utils.config import (
    BASE_DIR, CHARTS_EN_DIR, CHARTS_AR_DIR, STATIC_IMG_DIR,
    BACKUP_DIR, OVERRIDES_DIR, CUSTOM_SECTIONS_FILE, USERS_FILE, ACTIVITY_LOG,
)

ROLE_OPTIONS = ["admin", "editor", "viewer"]


def render(ctx):
    if st.session_state.get("current_role") != "admin":
        st.error("🔒 Access denied. Admin only.")
        st.stop()

    page_header(
        "👥", "User Management",
        "Manage application users, roles, and access. Changes take effect on next login.",
        "#ef4444",
    )

    users = load_users()

    # Add user form
    with st.expander("➕ Add New User", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                new_username = st.text_input("Username", placeholder="e.g. sara")
            with c2:
                new_password = st.text_input("Password", type="password",
                                             placeholder="Min 6 characters")
            with c3:
                new_role = st.selectbox("Role", ROLE_OPTIONS, index=1)
            submitted = st.form_submit_button("✅ Create User", type="primary",
                                              use_container_width=True)
            if submitted:
                new_username = new_username.strip()
                if not new_username:
                    st.error("Username cannot be empty.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_username in users:
                    st.error(f"User '{new_username}' already exists.")
                else:
                    users[new_username] = {
                        "password": hash_password(new_password),
                        "role": new_role,
                        "enabled": True,
                    }
                    save_users(users)
                    log_activity("USER_CREATED", detail=f"{new_username} as {new_role}")
                    st.success(f"✅ User '{new_username}' created as **{new_role}**.")
                    st.rerun()

    st.markdown("**👤 All Users**")

    # Header row
    hc = st.columns([2, 2, 2, 1, 1, 1])
    for col, label in zip(hc, ["**Username**", "**Password**", "**Role**",
                                "**Status**", "", ""]):
        col.markdown(label)
    st.markdown("<hr style='margin:0.25rem 0 0.75rem 0; border-color:#475569;'>",
                unsafe_allow_html=True)

    for username, info in list(users.items()):
        col_user, col_pass, col_role, col_status, col_save, col_del = st.columns([2, 2, 2, 1, 1, 1])

        with col_user:
            badge = " 🧑‍💼 **(you)**" if username == st.session_state["current_user"] else ""
            st.markdown(f"`{username}`{badge}")

        with col_pass:
            new_pass = st.text_input(
                "pw", value="", type="password", label_visibility="collapsed",
                key=f"pw_{username}", placeholder="New password (leave blank to keep)",
            )

        with col_role:
            current_role_idx = ROLE_OPTIONS.index(info.get("role", "viewer"))
            new_role = st.selectbox(
                "role", ROLE_OPTIONS, index=current_role_idx,
                label_visibility="collapsed", key=f"role_{username}",
            )

        with col_status:
            is_enabled = info.get("enabled", True)
            status_label = "✅ On" if is_enabled else "⛔ Off"
            if st.button(status_label, key=f"toggle_{username}", use_container_width=True):
                if username == st.session_state["current_user"]:
                    st.toast("⚠️ You cannot disable your own account.", icon="⚠️")
                else:
                    users[username]["enabled"] = not is_enabled
                    save_users(users)
                    st.rerun()

        with col_save:
            if st.button("💾 Save", key=f"save_{username}", use_container_width=True):
                if new_pass and len(new_pass) < 6:
                    st.toast(f"⚠️ Password too short for {username}.", icon="⚠️")
                elif username == st.session_state["current_user"] and new_role != "admin":
                    st.toast("⚠️ You cannot downgrade your own admin role.", icon="⚠️")
                else:
                    if new_pass:
                        users[username]["password"] = hash_password(new_pass)
                    users[username]["role"] = new_role
                    save_users(users)
                    log_activity(
                        "USER_EDITED",
                        detail=f"{username} → role={new_role}"
                               + (", password changed" if new_pass else ""),
                    )
                    st.toast(f"✅ Saved changes for {username}.", icon="✅")
                    st.rerun()

        with col_del:
            if username == st.session_state["current_user"]:
                st.markdown(
                    "<span title='Cannot delete yourself' "
                    "style='color:#64748b; cursor:not-allowed;'>🗑️</span>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button("🗑️ Del", key=f"del_{username}", use_container_width=True,
                             help=f"Delete {username}"):
                    st.session_state[f"confirm_del_{username}"] = True
                    st.rerun()

        if st.session_state.get(f"confirm_del_{username}"):
            st.warning(f"⚠️ Delete user **{username}**? This cannot be undone.")
            cc1, cc2, _ = st.columns([1, 1, 4])
            with cc1:
                if st.button("✓ Yes, delete", key=f"confirm_del_yes_{username}",
                             type="primary"):
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

    # ── R2 full sync ─────────────────────────────────────────────────────────
    st.divider()
    with st.expander("☁️ Sync All Files to R2", expanded=False):
        st.markdown(
            "Use this to do an **initial upload** of all local files to Cloudflare R2, "
            "or to force a full re-sync if the cloud bucket is out of date. "
            "This uploads every content file, chart, override, issue archive, and config."
        )
        if st.button("☁️ Upload Everything to R2", type="primary",
                     use_container_width=True, key="full_sync_btn"):
            st.session_state["confirm_full_sync"] = True

        if st.session_state.get("confirm_full_sync"):
            st.warning("This will overwrite all files in the R2 bucket with your local versions.")
            cs1, cs2 = st.columns(2)
            with cs1:
                if st.button("✓ Confirm Upload", key="confirm_sync_yes", type="primary"):
                    st.session_state["confirm_full_sync"] = False
                    _dirs = [
                        ("content",         os.path.join(BASE_DIR, "content")),
                        ("static_sections", os.path.join(BASE_DIR, "static_sections")),
                        ("overrides",       OVERRIDES_DIR),
                        ("images/charts",   CHARTS_EN_DIR),
                        ("images/charts_ar",CHARTS_AR_DIR),
                        ("images/static",   STATIC_IMG_DIR),
                        ("issues",          os.path.join(BASE_DIR, "issues")),
                        ("templates_backup",BACKUP_DIR),
                        # "templates/" is excluded — placeholder PNGs are recreated
                        # locally on startup and are in _SYNC_SKIP_PREFIXES.
                    ]
                    _files = [
                        os.path.join(BASE_DIR, "config.tex"),
                        os.path.join(BASE_DIR, "config_ar.tex"),
                        os.path.join(BASE_DIR, "main.tex"),
                        os.path.join(BASE_DIR, "main_ar.tex"),
                        os.path.join(BASE_DIR, "preamble.tex"),
                        os.path.join(BASE_DIR, "preamble_ar.tex"),
                        os.path.join(BASE_DIR, "custom_sections_generated.tex"),
                        os.path.join(BASE_DIR, "custom_sections_generated_ar.tex"),
                        CUSTOM_SECTIONS_FILE,
                        USERS_FILE,
                        ACTIVITY_LOG,
                    ]
                    with st.spinner("Uploading to R2…"):
                        for prefix, path in _dirs:
                            if os.path.isdir(path):
                                _storage.upload_dir(path, prefix)
                        for fpath in _files:
                            if os.path.isfile(fpath):
                                _storage.upload(fpath)
                    log_activity("R2_FULL_SYNC", detail="manual full upload from admin panel")
                    st.success("All files uploaded to R2.")
            with cs2:
                if st.button("✗ Cancel", key="confirm_sync_no"):
                    st.session_state["confirm_full_sync"] = False
                    st.rerun()

    # Role legend
    st.divider()
    st.markdown("**📋 Role Permissions**")
    lc = st.columns(3)
    role_desc = {
        "🔴 Admin":  "Full access — all views + User Management",
        "🟡 Editor": "Report Sections, Variables, Chart Manager",
        "🟢 Viewer": "Read-only access — Report Sections only",
    }
    for col, (badge, desc) in zip(lc, role_desc.items()):
        col.markdown(
            f"<div class='css-card'><b>{badge}</b><br>"
            f"<small style='color:#94a3b8;'>{desc}</small></div>",
            unsafe_allow_html=True,
        )
