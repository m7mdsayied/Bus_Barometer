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
git clone https://github.com/m7mdsayied/Bus_Barometer
cd Bus_Barometer

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run (cloud sync disabled locally by default)
streamlit run app.py
```

Cloud storage is disabled when `[r2]` is absent from `secrets.toml` — the app runs entirely on local files, which is the correct mode for local development.

---

## Directory Structure

```
Bus_Barometer/
├── app.py                        # Entry point — auth, CSS, sidebar, routing
├── issue_manager.py              # Issue archive/restore logic
├── utils/
│   ├── config.py                 # All constants, path definitions, label dicts
│   ├── auth.py                   # bcrypt auth, session management, activity logging
│   ├── content.py                # Slot system, factory reset, custom sections, file I/O
│   ├── storage.py                # Cloudflare R2 sync layer (boto3 / S3-compatible)
│   └── compiler.py               # XeLaTeX runner, MiKTeX helpers, fitz PDF renderer
├── views/
│   ├── sections.py               # Report Sections editor (slot-based + legacy)
│   ├── variables.py              # Report Variables (\newcommand editor)
│   ├── charts.py                 # Chart Manager (upload / replace images)
│   ├── publish.py                # Finalize & Publish (full PDF compile + download)
│   ├── activity.py               # Activity Log (admin only)
│   ├── users.py                  # User Management + full R2 sync (admin only)
│   └── issues_view.py            # Issue Manager (save / load / archive)
├── content/                      # Editable LaTeX section files (.tex)
├── static_sections/              # Static LaTeX sections (cover, about, methodology)
├── overrides/                    # Per-slot content overrides (plain text, git-ignored)
├── images/
│   ├── charts/                   # English chart images (ch1.png … ch25.png, t1-t4.png)
│   ├── charts_ar/                # Arabic chart images (same naming)
│   └── static/                   # Logo and other shared images
├── templates/                    # Empty issue template (placeholder charts + content)
├── templates_backup/             # Factory-reset snapshots (created on first run)
├── issues/                       # Archived issue snapshots (metadata.json per issue)
├── users.json                    # User store (bcrypt hashed — never commit plaintext)
├── requirements.txt
└── .streamlit/
    └── secrets.toml              # R2 credentials — git-ignored, set in Streamlit Cloud
```

---

## Role System

| Role | Capabilities |
|---|---|
| **admin** | All views + User Management + Factory Reset + R2 full sync |
| **editor** | Report Sections, Variables, Chart Manager, Issue Manager, Publish |
| **viewer** | Report Sections (read-only — no save) |

---

## Cloud Storage — Cloudflare R2

The app uses **Cloudflare R2** (S3-compatible object storage) to persist files across Streamlit Cloud's ephemeral filesystem. On every container startup, the app syncs files down from R2; on every save, it pushes the changed file back up.

### How the sync works

| Event | Action |
|---|---|
| Container start | Pull all content, overrides, charts, configs, issue metadata from R2 |
| File save | Push the changed file to R2 in a background thread |
| Issue archive | Upload the full issue folder to `issues/{lang}/{num}/` in R2 |
| Issue load | Download the full issue folder on demand (only metadata is fetched at startup) |
| File delete | Delete the corresponding object from R2 |

`reports/` and `templates/` are intentionally excluded from startup sync — reports are regenerated on demand and template placeholder PNGs are recreated locally.

### R2 credentials

Create an API token in the Cloudflare dashboard under **R2 → Manage R2 API Tokens** with **Object Read & Write** permissions, then add the following to `.streamlit/secrets.toml`:

```toml
[r2]
enabled    = true
account_id = "<your-cloudflare-account-id>"
access_key = "<your-r2-access-key-id>"
secret_key = "<your-r2-secret-access-key>"
bucket     = "<your-bucket-name>"
```

Set `enabled = false` (or omit the `[r2]` section entirely) for local development.

---

## Streamlit Cloud Deployment

1. Push the repo to GitHub (secrets are git-ignored — never committed).
2. In Streamlit Cloud → your app → **Settings → Secrets**, paste:

```toml
[r2]
enabled    = true
account_id = "<your-cloudflare-account-id>"
access_key = "<your-r2-access-key-id>"
secret_key = "<your-r2-secret-access-key>"
bucket     = "<your-bucket-name>"

[users_json]
# Optional fallback if users.json is not in the repo.
# Paste the full JSON content of your users.json here as a string.
```

3. Reboot the app. On first start it will pull all files from R2 and be fully operational.

> **First deployment?** After the app starts, go to **User Management → Sync All Files to R2** to do an initial upload of all local files to the bucket.

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
