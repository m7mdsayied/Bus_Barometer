# ECES Barometer Suite

A Streamlit-based CMS for producing the ECES Business Performance Indicator bilingual (English / Arabic) quarterly reports as polished PDFs via XeLaTeX.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.10+** | Tested on 3.13 |
| **MiKTeX** (Windows) or **TeXLive** (Linux/macOS) | Must include `xelatex` on PATH |
| Arabic fonts | Almarai / Amiri (included in MiKTeX package manager) |

---

## Local Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd CL_Baro

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up users (first run)
cp users.json.example users.json
# Edit users.json and replace placeholder hashes with real bcrypt hashes:
# python -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt()).decode())"

# 5. Run
streamlit run app.py
```

---

## Directory Structure

```
CL_Baro/
├── app.py                        # Entry point (~390 lines) — auth, CSS, sidebar, routing
├── issue_manager.py              # Issue archive/restore logic
├── utils/
│   ├── config.py                 # All constants, path definitions, label dicts
│   ├── auth.py                   # bcrypt auth, session management, activity logging
│   ├── content.py                # Slot system, factory reset, custom sections, file I/O
│   └── compiler.py               # XeLaTeX runner, MiKTeX helpers, fitz PDF renderer
├── views/
│   ├── sections.py               # Report Sections editor (slot-based + legacy)
│   ├── variables.py              # Report Variables (\newcommand editor)
│   ├── charts.py                 # Chart Manager (upload / replace images)
│   ├── publish.py                # Finalize & Publish (full PDF compile + download)
│   ├── activity.py               # Activity Log (admin only)
│   ├── users.py                  # User Management (admin only)
│   └── issues_view.py            # Issue Manager (save / load / archive)
├── content/                      # Editable LaTeX section files (.tex)
├── static_sections/              # Static LaTeX sections (cover, about, methodology)
├── overrides/                    # Per-slot content overrides (plain text, git-ignored)
├── images/
│   ├── charts/                   # English chart images (ch1.png … ch25.png, t1-t4.png)
│   ├── charts_ar/                # Arabic chart images (same naming)
│   └── static/                   # Logo and other shared images
├── templates_backup/             # Factory-reset snapshots (created on first run)
├── issues/                       # Archived issue snapshots (JSON + tex files)
├── users.json                    # User store (bcrypt hashed — never commit plaintext)
├── users.json.example            # Template for new deployments
├── requirements.txt
└── .streamlit/
    └── secrets.toml.example      # Template for Streamlit Cloud deployment
```

---

## Role System

| Role | Capabilities |
|---|---|
| **admin** | All views + User Management + Factory Reset |
| **editor** | Report Sections, Variables, Chart Manager, Issue Manager |
| **viewer** | Report Sections (read-only — no save) |

---

## Streamlit Cloud Deployment

Instead of `users.json`, configure users via Streamlit secrets:

1. Copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml`
2. Replace placeholder hashes with real bcrypt hashes
3. Add `secrets.toml` to `.gitignore` (already included)
4. In Streamlit Cloud, paste the contents of `secrets.toml` into the Secrets panel

The app's `load_users()` automatically falls back to `st.secrets["users"]` when `users.json` is absent.

---

## Report Language Toggle

The sidebar **Report Language** radio (English / Arabic) controls **which LaTeX files are compiled** — it does not change the UI language (the UI is English-only). Switching to Arabic loads `*_ar.tex` files and `images/charts_ar/`.

---

## Slot System

Content sections use `\ECESContent{slot_id}{default text}` macros. Edits are saved as plain-text files in `overrides/` — the original `.tex` templates are never modified. This means:

- Factory reset only needs to clear `overrides/`
- Git diffs on `.tex` files stay clean
- Multiple users editing the same section don't conflict at the file level

---

## Factory Reset

Available to **admin** only via the sidebar expander:

- **Reset Current Section** — clears overrides for the open section
- **Reset All Content Edits** — clears all `overrides/*.tex` files
- **Full Factory Reset** — restores all `.tex` files from `templates_backup/` and clears overrides
