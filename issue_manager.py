"""
issue_manager.py — Issue Management Module for ECES Barometer CMS

Provides functions to:
- Inspect the currently active issue (parsed from config.tex / config_ar.tex)
- List archived issues
- Save the current active issue to the archive
- Load an archived issue into the active workspace
- Create a new blank issue from the empty template
- Generate placeholder PNG images for template charts

Archive structure:
    issues/
        en/
            75/
                config.tex
                content/          (only EN .tex files)
                overrides/        (only EN override files)
                charts/           (copy of images/charts/)
                metadata.json
        ar/
            77/
                config_ar.tex
                content/          (only AR .tex files)
                overrides/        (only AR override files)
                charts/           (copy of images/charts_ar/)
                metadata.json

Template structure:
    templates/
        empty/
            config.tex
            config_ar.tex
            content/              (all 12 files with [TODO:] placeholders)
            overrides/            (empty)
            charts/               (grey placeholder PNGs)
            charts_ar/            (grey placeholder PNGs)
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ---------------------------------------------------------------------------
# File lists (per language)
# ---------------------------------------------------------------------------

CHART_FILENAMES = [f"ch{i}.png" for i in range(1, 26)] + [f"t{i}.png" for i in range(1, 5)]

CONTENT_FILES = {
    "en": [
        "01_exec_summary.tex",
        "02_macro_overview.tex",
        "03_analysis_overall.tex",
        "04_constraints.tex",
        "05_subindices.tex",
        "06_tables.tex",
    ],
    "ar": [
        "01_exec_summary_ar.tex",
        "02_macro_overview_ar.tex",
        "03_analysis_overall_ar.tex",
        "04_constraints_ar.tex",
        "05_subindices_ar.tex",
        "06_tables_ar.tex",
    ],
}

CHARTS_DIR = {
    "en": os.path.join("images", "charts"),
    "ar": os.path.join("images", "charts_ar"),
}

CONFIG_FILE = {
    "en": "config.tex",
    "ar": "config_ar.tex",
}


# ---------------------------------------------------------------------------
# Placeholder PNG generation
# ---------------------------------------------------------------------------

# Minimal 1×1 grey PNG bytes (fallback when Pillow is unavailable)
_GREY_PNG_1X1 = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x00, 0x00, 0x00, 0x00, 0x3A, 0x7E, 0x9B,
    0x55, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
    0x54, 0x78, 0x9C, 0x62, 0xC8, 0x00, 0x00, 0x00,
    0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC, 0x33, 0x00,
    0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
    0x42, 0x60, 0x82,
])


def generate_placeholder_png(dest_path: str | os.PathLike, label: str = "") -> None:
    """
    Write a grey 900×500 placeholder PNG to dest_path.
    Falls back to a minimal 1×1 grey PNG when Pillow is unavailable.
    """
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    name = label or dest.name

    if PIL_AVAILABLE:
        W, H = 900, 500
        img = Image.new("RGB", (W, H), color=(210, 210, 210))
        draw = ImageDraw.Draw(img)

        # Border
        b = 14
        draw.rectangle([(b, b), (W - b, H - b)], outline=(160, 160, 160), width=3)

        # Simple bar-chart icon
        bars = [(60, (150, 150, 150)), (80, (130, 130, 130)), (100, (170, 170, 170))]
        bx, by = W // 2 - 110, H // 2 - 10
        for i, (bh, bc) in enumerate(bars):
            draw.rectangle(
                [(bx + i * 80, by - bh + 40), (bx + i * 80 + 55, by + 40)],
                fill=bc,
            )

        # Text lines
        lines = ["Chart Placeholder", name, "Upload via Chart Manager"]
        y = by + 75
        for line in lines:
            draw.text((W // 2, y), line, fill=(90, 90, 90), anchor="mm")
            y += 24

        img.save(dest, "PNG")
    else:
        dest.write_bytes(_GREY_PNG_1X1)


def ensure_template_charts(base_dir: str | os.PathLike) -> None:
    """Create placeholder PNGs in templates/empty/charts/ and charts_ar/ if absent."""
    base = Path(base_dir).resolve()
    for subdir in ("templates/empty/charts", "templates/empty/charts_ar"):
        d = base / subdir
        d.mkdir(parents=True, exist_ok=True)
        for fname in CHART_FILENAMES:
            p = d / fname
            if not p.exists():
                generate_placeholder_png(p, label=fname)


# ---------------------------------------------------------------------------
# Config parsing
# ---------------------------------------------------------------------------

def _parse_config(config_path: Path) -> dict:
    """Return a dict of {VariableName: value} from a LaTeX config file."""
    result = {}
    if not config_path.exists():
        return result
    for m in re.finditer(
        r"\\newcommand\{\\(\w+)\}\{([^}]*)\}",
        config_path.read_text(encoding="utf-8"),
    ):
        result[m.group(1)] = m.group(2).strip()
    return result


def get_current_issue_info(lang: str, base_dir: str | os.PathLike) -> dict:
    """
    Parse the active config file and return issue metadata dict.

    Keys: issue_num, quarter, next_quarter, fiscal_year, lang, config_file
    """
    base = Path(base_dir).resolve()
    cfg = _parse_config(base / CONFIG_FILE[lang])
    return {
        "issue_num":    cfg.get("IssueNumber", "??"),
        "quarter":      cfg.get("CurrentQuarterText", "??"),
        "next_quarter": cfg.get("NextQuarterText", ""),
        "fiscal_year":  cfg.get("CurrentFiscalYear", ""),
        "lang":         lang,
        "config_file":  CONFIG_FILE[lang],
    }


# ---------------------------------------------------------------------------
# List archived issues
# ---------------------------------------------------------------------------

def list_issues(lang: str, base_dir: str | os.PathLike) -> list[dict]:
    """
    Scan issues/{lang}/ and return a list of metadata dicts sorted by issue_num.
    Each dict includes: issue_num, quarter, archived_at, archived_by, path.
    """
    issues_dir = Path(base_dir).resolve() / "issues" / lang
    if not issues_dir.exists():
        return []

    results = []
    for entry in issues_dir.iterdir():
        if not entry.is_dir():
            continue
        meta_path = entry / "metadata.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                meta["path"] = str(entry)
                results.append(meta)
                continue
            except Exception:
                pass
        # Fallback: infer from folder name
        results.append({
            "issue_num":   entry.name,
            "quarter":     "Unknown",
            "archived_at": "",
            "archived_by": "",
            "lang":        lang,
            "path":        str(entry),
        })

    return sorted(results, key=lambda x: str(x.get("issue_num", "")))


# ---------------------------------------------------------------------------
# Save current issue
# ---------------------------------------------------------------------------

def save_issue(
    lang: str,
    base_dir: str | os.PathLike,
    archived_by: str = "system",
    overwrite: bool = False,
) -> tuple[bool, str]:
    """
    Archive the currently active content to issues/{lang}/{issue_num}/.

    Returns (success, message).
    """
    base = Path(base_dir).resolve()
    info = get_current_issue_info(lang, base_dir)
    issue_num = info["issue_num"]

    dest = base / "issues" / lang / str(issue_num)
    if dest.exists() and not overwrite:
        return False, f"ALREADY_EXISTS:{issue_num}"

    try:
        dest.mkdir(parents=True, exist_ok=True)

        # Config file
        shutil.copy2(base / CONFIG_FILE[lang], dest / CONFIG_FILE[lang])

        # Content files
        content_dest = dest / "content"
        content_dest.mkdir(exist_ok=True)
        for fname in CONTENT_FILES[lang]:
            src = base / "content" / fname
            if src.exists():
                shutil.copy2(src, content_dest / fname)

        # Override files (language-specific)
        overrides_dest = dest / "overrides"
        overrides_dest.mkdir(exist_ok=True)
        overrides_src = base / "overrides"
        if overrides_src.exists():
            for f in overrides_src.iterdir():
                if not f.name.endswith(".tex"):
                    continue
                if lang == "ar" and f.name.endswith("_ar.tex"):
                    shutil.copy2(f, overrides_dest / f.name)
                elif lang == "en" and not f.name.endswith("_ar.tex"):
                    shutil.copy2(f, overrides_dest / f.name)

        # Charts
        charts_src = base / CHARTS_DIR[lang]
        charts_dest = dest / "charts"
        charts_dest.mkdir(exist_ok=True)
        if charts_src.exists():
            for f in charts_src.iterdir():
                if f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                    shutil.copy2(f, charts_dest / f.name)

        # Metadata
        metadata = {
            "issue_num":   issue_num,
            "quarter":     info.get("quarter", ""),
            "fiscal_year": info.get("fiscal_year", ""),
            "lang":        lang,
            "archived_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "archived_by": archived_by,
        }
        (dest / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        return True, f"Issue {issue_num} ({lang.upper()}) saved to archive."

    except Exception as e:
        return False, f"Save failed: {e}"


# ---------------------------------------------------------------------------
# Load an archived issue into the active workspace
# ---------------------------------------------------------------------------

def _clear_lang_overrides(overrides_dir: Path, lang: str) -> None:
    """Remove override files belonging to the given language."""
    if not overrides_dir.exists():
        return
    for f in overrides_dir.iterdir():
        if not f.name.endswith(".tex"):
            continue
        if lang == "ar" and f.name.endswith("_ar.tex"):
            f.unlink()
        elif lang == "en" and not f.name.endswith("_ar.tex"):
            f.unlink()


def load_issue(
    lang: str,
    issue_num: str | int,
    base_dir: str | os.PathLike,
) -> tuple[bool, str]:
    """
    Restore an archived issue from issues/{lang}/{issue_num}/ to the active workspace.

    Returns (success, message).
    """
    base = Path(base_dir).resolve()
    src = base / "issues" / lang / str(issue_num)
    if not src.exists():
        return False, f"Archive for issue {issue_num} ({lang.upper()}) not found."

    try:
        # Config
        config_src = src / CONFIG_FILE[lang]
        if config_src.exists():
            shutil.copy2(config_src, base / CONFIG_FILE[lang])

        # Content files
        content_src = src / "content"
        if content_src.exists():
            for f in content_src.iterdir():
                if f.suffix == ".tex":
                    shutil.copy2(f, base / "content" / f.name)

        # Overrides: clear then restore
        overrides_dir = base / "overrides"
        overrides_dir.mkdir(exist_ok=True)
        _clear_lang_overrides(overrides_dir, lang)
        archived_overrides = src / "overrides"
        if archived_overrides.exists():
            for f in archived_overrides.iterdir():
                if f.suffix == ".tex":
                    shutil.copy2(f, overrides_dir / f.name)

        # Charts
        charts_dest = base / CHARTS_DIR[lang]
        charts_dest.mkdir(parents=True, exist_ok=True)
        archived_charts = src / "charts"
        if archived_charts.exists():
            for f in archived_charts.iterdir():
                if f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                    shutil.copy2(f, charts_dest / f.name)

        return True, f"Issue {issue_num} ({lang.upper()}) loaded successfully."

    except Exception as e:
        return False, f"Load failed: {e}"


# ---------------------------------------------------------------------------
# New issue from empty template
# ---------------------------------------------------------------------------

def new_from_template(lang: str, base_dir: str | os.PathLike) -> tuple[bool, str]:
    """
    Copy the empty template into the active workspace for the given language.
    Clears all language-specific overrides and replaces charts with placeholders.

    Returns (success, message).
    """
    base = Path(base_dir).resolve()
    tmpl = base / "templates" / "empty"
    if not tmpl.exists():
        return False, "Empty template not found at templates/empty/."

    try:
        # Config
        tmpl_config = tmpl / CONFIG_FILE[lang]
        if tmpl_config.exists():
            shutil.copy2(tmpl_config, base / CONFIG_FILE[lang])

        # Content files — English only (English embeds text as ECESContent defaults;
        # Arabic uses override files instead, so content files must not change for Arabic)
        if lang == "en":
            tmpl_content = tmpl / "content"
            for fname in CONTENT_FILES[lang]:
                src = tmpl_content / fname
                if src.exists():
                    shutil.copy2(src, base / "content" / fname)

        # Clear overrides for this language
        overrides_dir = base / "overrides"
        overrides_dir.mkdir(exist_ok=True)
        _clear_lang_overrides(overrides_dir, lang)

        # Copy placeholder override files from template (mirrors chart copy logic below)
        tmpl_overrides = tmpl / "overrides"
        if tmpl_overrides.exists():
            for f in tmpl_overrides.iterdir():
                if not f.name.endswith(".tex"):
                    continue
                is_ar = f.name.endswith("_ar.tex")
                if (lang == "ar" and is_ar) or (lang == "en" and not is_ar):
                    shutil.copy2(f, overrides_dir / f.name)

        # Charts — copy placeholders from template
        charts_subdir = "charts_ar" if lang == "ar" else "charts"
        tmpl_charts = tmpl / charts_subdir
        charts_dest = base / CHARTS_DIR[lang]
        charts_dest.mkdir(parents=True, exist_ok=True)
        if tmpl_charts.exists():
            for f in tmpl_charts.iterdir():
                if f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                    shutil.copy2(f, charts_dest / f.name)
        else:
            # Generate placeholders on the fly if template charts are missing
            for fname in CHART_FILENAMES:
                generate_placeholder_png(charts_dest / fname, label=fname)

        return True, (
            "Blank template loaded. "
            "Edit Issue Number & dates in Report Variables, "
            "upload charts via Chart Manager, then fill in content."
        )

    except Exception as e:
        return False, f"Template load failed: {e}"


# ---------------------------------------------------------------------------
# New issue based on a previous archived issue
# ---------------------------------------------------------------------------

def new_from_issue(
    lang: str,
    source_issue: str | int,
    base_dir: str | os.PathLike,
) -> tuple[bool, str]:
    """
    Copy an archived issue into the active workspace as a starting point for a new issue.
    Equivalent to load_issue but intended semantically for 'start from previous'.
    """
    ok, msg = load_issue(lang, source_issue, base_dir)
    if ok:
        return True, (
            f"Issue {source_issue} ({lang.upper()}) loaded as starting point. "
            "Update Issue Number & dates in Report Variables before publishing."
        )
    return ok, msg


# ---------------------------------------------------------------------------
# Delete an archived issue
# ---------------------------------------------------------------------------

def delete_issue(
    lang: str,
    issue_num: str | int,
    base_dir: str | os.PathLike,
) -> tuple[bool, str]:
    """Remove an archived issue folder entirely."""
    path = Path(base_dir).resolve() / "issues" / lang / str(issue_num)
    if not path.exists():
        return False, f"Archive for issue {issue_num} ({lang.upper()}) not found."
    try:
        shutil.rmtree(path)
        return True, f"Issue {issue_num} ({lang.upper()}) deleted from archive."
    except Exception as e:
        return False, f"Delete failed: {e}"


# ---------------------------------------------------------------------------
# First-run: auto-archive the currently active issue if not yet archived
# ---------------------------------------------------------------------------

def auto_archive_if_new(lang: str, base_dir: str | os.PathLike) -> None:
    """
    On first launch, silently archive the currently active issue so it is not
    accidentally overwritten when the user creates a new issue.
    Does nothing if an archive already exists for the current issue number.
    """
    try:
        info = get_current_issue_info(lang, base_dir)
        issue_num = info["issue_num"]
        if issue_num in ("??", "XX"):
            return
        archive_path = Path(base_dir).resolve() / "issues" / lang / str(issue_num)
        if not archive_path.exists():
            save_issue(lang, base_dir, archived_by="system:auto", overwrite=False)
    except Exception:
        pass  # Never block app startup
