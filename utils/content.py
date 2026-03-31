"""
File I/O, slot-based content system, custom sections, factory reset,
and miscellaneous UI helpers (page header, latex block parser).
"""
import json
import os
import re
import shutil
import time

import streamlit as st

from utils.config import (
    BASE_DIR, BACKUP_DIR, OVERRIDES_DIR, CUSTOM_SECTIONS_FILE,
    SECTION_TEMPLATES, CHART_LABELS, SLOT_LABELS,
)

# Ensure overrides directory exists at import time
os.makedirs(OVERRIDES_DIR, exist_ok=True)


# ── Simple File I/O ──────────────────────────────────────────────────────────
def load_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def save_file(filepath: str, content: str):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


# ── Factory Reset ─────────────────────────────────────────────────────────────
def initialize_factory_backup() -> bool:
    """Create initial backup of templates if not already done. Returns True on first run."""
    if os.path.exists(BACKUP_DIR):
        return False

    os.makedirs(BACKUP_DIR)

    content_backup = os.path.join(BACKUP_DIR, "content")
    os.makedirs(content_backup, exist_ok=True)
    if os.path.exists(os.path.join(BASE_DIR, "content")):
        for file in os.listdir(os.path.join(BASE_DIR, "content")):
            if file.endswith(".tex"):
                shutil.copy2(
                    os.path.join(BASE_DIR, "content", file),
                    os.path.join(content_backup, file),
                )

    static_backup = os.path.join(BACKUP_DIR, "static_sections")
    os.makedirs(static_backup, exist_ok=True)
    if os.path.exists(os.path.join(BASE_DIR, "static_sections")):
        for file in os.listdir(os.path.join(BASE_DIR, "static_sections")):
            if file.endswith(".tex"):
                shutil.copy2(
                    os.path.join(BASE_DIR, "static_sections", file),
                    os.path.join(static_backup, file),
                )

    for config_file in ["config.tex", "config_ar.tex"]:
        if os.path.exists(os.path.join(BASE_DIR, config_file)):
            shutil.copy2(
                os.path.join(BASE_DIR, config_file),
                os.path.join(BACKUP_DIR, config_file),
            )

    return True


def factory_reset(target: str = "all"):
    """
    Restore files from factory backup.
    target: "all" | "overrides" | specific filename
    Returns: (success: bool, message: str)
    """
    if not os.path.exists(BACKUP_DIR) and target != "overrides":
        return False, "No factory backup found. Cannot reset."

    try:
        if target == "overrides":
            if os.path.exists(OVERRIDES_DIR):
                count = 0
                for f in os.listdir(OVERRIDES_DIR):
                    if f.endswith(".tex"):
                        os.remove(os.path.join(OVERRIDES_DIR, f))
                        count += 1
                return True, f"Cleared {count} content overrides"
            return True, "No overrides to clear"

        elif target == "all":
            backup_content = os.path.join(BACKUP_DIR, "content")
            if os.path.exists(backup_content):
                for file in os.listdir(backup_content):
                    shutil.copy2(
                        os.path.join(backup_content, file),
                        os.path.join(BASE_DIR, "content", file),
                    )

            backup_static = os.path.join(BACKUP_DIR, "static_sections")
            if os.path.exists(backup_static):
                for file in os.listdir(backup_static):
                    shutil.copy2(
                        os.path.join(backup_static, file),
                        os.path.join(BASE_DIR, "static_sections", file),
                    )

            for config_file in ["config.tex", "config_ar.tex"]:
                if os.path.exists(os.path.join(BACKUP_DIR, config_file)):
                    shutil.copy2(
                        os.path.join(BACKUP_DIR, config_file),
                        os.path.join(BASE_DIR, config_file),
                    )

            if os.path.exists(OVERRIDES_DIR):
                for f in os.listdir(OVERRIDES_DIR):
                    if f.endswith(".tex"):
                        os.remove(os.path.join(OVERRIDES_DIR, f))

            return True, "All files restored to factory state (including content overrides)"

        else:
            # Reset a specific file
            if os.path.exists(os.path.join(BACKUP_DIR, "content", target)):
                src = os.path.join(BACKUP_DIR, "content", target)
                dst = os.path.join(BASE_DIR, "content", target)
            elif os.path.exists(os.path.join(BACKUP_DIR, "static_sections", target)):
                src = os.path.join(BACKUP_DIR, "static_sections", target)
                dst = os.path.join(BASE_DIR, "static_sections", target)
            else:
                return False, f"File {target} not found in backup"

            shutil.copy2(src, dst)

            base_name = target.replace(".tex", "").replace("_ar", "")
            if len(base_name) > 3 and base_name[2] == "_":
                base_name = base_name[3:]
            if os.path.exists(OVERRIDES_DIR):
                for f in os.listdir(OVERRIDES_DIR):
                    if f.startswith(base_name.split("_")[0] + "_") and f.endswith(".tex"):
                        os.remove(os.path.join(OVERRIDES_DIR, f))

            return True, f"Restored {target} (and cleared related overrides)"

    except Exception as e:
        return False, f"Reset failed: {str(e)}"


# ── Custom Sections ───────────────────────────────────────────────────────────
def load_custom_sections() -> dict:
    if os.path.exists(CUSTOM_SECTIONS_FILE):
        try:
            with open(CUSTOM_SECTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"en": [], "ar": []}


def save_custom_sections(data: dict):
    with open(CUSTOM_SECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Bust the section-map cache so the sidebar reflects the change immediately
    try:
        import streamlit as st
        st.cache_data.clear()
    except Exception:
        pass


def add_custom_section(lang: str, title: str, sec_type: str):
    """Create a .tex file and register the section. Returns (ok, msg)."""
    _cs = load_custom_sections()
    _lang_key = "ar" if lang == "Arabic" else "en"
    _suffix = "_ar" if lang == "Arabic" else ""
    _id = f"cs_{int(time.time())}{_suffix}"
    _fname = f"content/{_id}.tex"
    _fpath = os.path.join(BASE_DIR, _fname)
    try:
        _tex = SECTION_TEMPLATES[sec_type].format(title=title, id=_id)
        os.makedirs(os.path.dirname(_fpath), exist_ok=True)
        with open(_fpath, "w", encoding="utf-8") as f:
            f.write(_tex)
        _cs[_lang_key].append({"id": _id, "title": title, "type": sec_type, "file": _fname})
        save_custom_sections(_cs)
        sync_custom_sections_file(lang)
        return True, f"Section '{title}' created."
    except Exception as e:
        return False, str(e)


def delete_custom_section(lang: str, sec_id: str):
    _cs = load_custom_sections()
    _lang_key = "ar" if lang == "Arabic" else "en"
    _cs[_lang_key] = [s for s in _cs[_lang_key] if s["id"] != sec_id]
    save_custom_sections(_cs)
    sync_custom_sections_file(lang)


def sync_custom_sections_file(lang: str):
    """Regenerate custom_sections_generated[_ar].tex from custom_sections.json."""
    _cs = load_custom_sections()
    _lang_key = "ar" if lang == "Arabic" else "en"
    _suffix = "_ar" if lang == "Arabic" else ""
    _fname = os.path.join(BASE_DIR, f"custom_sections_generated{_suffix}.tex")
    lines = ["% Auto-generated by ECES CMS — do not edit manually\n"]
    for sec in _cs.get(_lang_key, []):
        lines.append(f"\\clearpage\n\\input{{{sec['file']}}}\n")
    with open(_fname, "w", encoding="utf-8") as f:
        f.writelines(lines)


def _build_section_map(lang: str, base_sections: dict) -> dict:
    """Merge static + custom sections for the given language."""
    _cs = load_custom_sections()
    _lang_key = "ar" if lang == "Arabic" else "en"
    _merged = dict(base_sections)
    for _s in _cs.get(_lang_key, []):
        _merged[_s["title"]] = _s["file"]
    return _merged


# ── Slot-Based Content System ─────────────────────────────────────────────────
def extract_slots(tex_content: str) -> list:
    """
    Extract all \\ECESContent{slot_id}{default_text} from a .tex file.
    Returns list of (slot_id, default_text) in document order.
    Handles nested braces in default text.
    """
    slots = []
    marker = r"\ECESContent{"
    i = 0

    while i < len(tex_content):
        pos = tex_content.find(marker, i)
        if pos == -1:
            break

        id_start = pos + len(marker)
        id_end = tex_content.find("}", id_start)
        if id_end == -1:
            break
        slot_id = tex_content[id_start:id_end]

        if id_end + 1 >= len(tex_content) or tex_content[id_end + 1] != "{":
            i = id_end + 1
            continue
        text_start = id_end + 2

        brace_depth = 1
        j = text_start
        while j < len(tex_content) and brace_depth > 0:
            if tex_content[j] == "{" and tex_content[j - 1:j] != "\\":
                brace_depth += 1
            elif tex_content[j] == "}" and tex_content[j - 1:j] != "\\":
                brace_depth -= 1
            j += 1

        default_text = tex_content[text_start:j - 1]
        slots.append((slot_id, default_text))
        i = j

    return slots


def get_slot_content(slot_id: str, default_text: str):
    """Return (content, is_overridden). Override file takes priority."""
    override_path = os.path.join(OVERRIDES_DIR, f"{slot_id}.tex")
    if os.path.exists(override_path):
        return load_file(override_path), True
    return default_text, False


def save_slot(slot_id: str, content: str):
    save_file(os.path.join(OVERRIDES_DIR, f"{slot_id}.tex"), content)


def reset_slot(slot_id: str):
    override_path = os.path.join(OVERRIDES_DIR, f"{slot_id}.tex")
    if os.path.exists(override_path):
        os.remove(override_path)


def get_all_section_slots(section_file_path: str) -> list:
    """Return [(slot_id, current_text, is_overridden, default_text), ...]."""
    tex_content = load_file(section_file_path)
    result = []
    for slot_id, default_text in extract_slots(tex_content):
        current_text, is_overridden = get_slot_content(slot_id, default_text)
        result.append((slot_id, current_text, is_overridden, default_text))
    return result


def _extract_brace_content(tex: str, pos: int) -> str:
    """Extract content of a balanced {...} block starting at pos (after opening '{')."""
    depth = 1
    j = pos
    while j < len(tex) and depth > 0:
        if tex[j] == "{" and (j == 0 or tex[j - 1] != "\\"):
            depth += 1
        elif tex[j] == "}" and (j == 0 or tex[j - 1] != "\\"):
            depth -= 1
        j += 1
    return tex[pos:j - 1]


def extract_section_items(tex_content: str, charts_dir: str) -> list:
    """
    Parse a .tex file and return ordered list of editable items.
    Each item is a dict with 'type' key: 'text' or 'chart'.
    """
    items = []
    marker = r"\ECESContent{"

    # Collect text slot positions
    text_positions = []
    i = 0
    while i < len(tex_content):
        pos = tex_content.find(marker, i)
        if pos == -1:
            break
        id_start = pos + len(marker)
        id_end = tex_content.find("}", id_start)
        if id_end == -1:
            break
        slot_id = tex_content[id_start:id_end]
        if id_end + 1 < len(tex_content) and tex_content[id_end + 1] == "{":
            default_text = _extract_brace_content(tex_content, id_end + 2)
            current_text, is_overridden = get_slot_content(slot_id, default_text)
            text_positions.append((pos, {
                "type": "text", "slot_id": slot_id,
                "current_text": current_text, "is_overridden": is_overridden,
                "default_text": default_text,
            }))
        i = id_end + 1

    # Collect chart image positions
    chart_pattern = re.compile(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}")
    chart_positions = []
    for m in chart_pattern.finditer(tex_content):
        fn = m.group(1)
        if fn.lower().endswith((".png", ".jpg", ".jpeg")):
            fp = os.path.join(charts_dir, fn)
            chart_positions.append((m.start(), {
                "type": "chart", "filename": fn, "filepath": fp,
                "exists": os.path.exists(fp),
                "label": CHART_LABELS.get(fn.lower(), fn),
            }))

    all_items = sorted(text_positions + chart_positions, key=lambda x: x[0])
    return [item for _, item in all_items]


def append_text_slot_to_section(file_path: str) -> str:
    """Append a new \\ECESContent text slot. Returns the new slot_id."""
    slot_id = f"cs_p{int(time.time())}"
    new_block = (
        f"\n\\vspace{{0.8em}}\n"
        f"\\ECESContent{{{slot_id}}}{{[TODO: Enter paragraph.]}}\n"
    )
    content = load_file(file_path)
    if "\\clearpage" in content:
        content = content.replace("\\clearpage", new_block + "\\clearpage", 1)
    else:
        content += new_block
    save_file(file_path, content)
    return slot_id


def append_chart_slot_to_section(file_path: str) -> str:
    """Append an image figure block. Returns the image filename."""
    img_id = f"custom_{int(time.time())}.png"
    new_block = (
        f"\n\\vspace{{0.8em}}\n"
        f"%% TODO: Upload {img_id} via Chart Manager\n"
        f"\\begin{{figure}}[h!]\n"
        f"    \\centering\n"
        f"    \\includegraphics[width=\\linewidth]{{{img_id}}}\n"
        f"\\end{{figure}}\n"
    )
    content = load_file(file_path)
    if "\\clearpage" in content:
        content = content.replace("\\clearpage", new_block + "\\clearpage", 1)
    else:
        content += new_block
    save_file(file_path, content)
    return img_id


def remove_text_slot_from_section(file_path: str, slot_id: str):
    content = load_file(file_path)
    pattern = re.compile(
        r"\\vspace\{[^}]+\}\s*\\ECESContent\{" + re.escape(slot_id) + r"\}\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}",
        re.DOTALL,
    )
    content = pattern.sub("", content)
    if slot_id in content:
        pattern2 = re.compile(
            r"\\ECESContent\{" + re.escape(slot_id) + r"\}\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}",
            re.DOTALL,
        )
        content = pattern2.sub("", content)
    save_file(file_path, content)
    reset_slot(slot_id)


def remove_chart_slot_from_section(file_path: str, filename: str):
    content = load_file(file_path)
    pattern = re.compile(
        r"(?:\\vspace\{[^}]+\}\s*)?"
        r"(?:%+\s*TODO[^\n]*\n)?"
        r"\\begin\{figure\}[^\n]*\n.*?"
        r"\\includegraphics(?:\[.*?\])?\{" + re.escape(filename) + r"\}.*?"
        r"\\end\{figure\}",
        re.DOTALL,
    )
    content = pattern.sub("", content)
    save_file(file_path, content)


def reset_all_overrides():
    """Remove all override files."""
    if os.path.exists(OVERRIDES_DIR):
        for f in os.listdir(OVERRIDES_DIR):
            if f.endswith(".tex"):
                os.remove(os.path.join(OVERRIDES_DIR, f))


# ── Label Helpers ─────────────────────────────────────────────────────────────
def get_slot_label(slot_id: str) -> str:
    return SLOT_LABELS.get(slot_id, slot_id.replace("_", " ").title())


# ── Legacy Block Parser (non-migrated sections) ───────────────────────────────
def parse_latex_blocks(content: str) -> list:
    lines = content.splitlines()
    blocks = []
    current_chunk = []
    current_type = None
    latex_cmd_pattern = re.compile(r"^(\\|\%|\{|}|\s*\\)")

    for line in lines:
        is_code = bool(latex_cmd_pattern.match(line.strip())) or line.strip() == ""
        line_type = "code" if is_code else "text"
        if current_type is None:
            current_type = line_type

        if line_type != current_type:
            blocks.append({"type": current_type, "content": "\n".join(current_chunk)})
            current_chunk = [line]
            current_type = line_type
        else:
            current_chunk.append(line)

    if current_chunk:
        blocks.append({"type": current_type, "content": "\n".join(current_chunk)})
    return blocks


def reconstruct_latex(blocks: list) -> str:
    return "\n".join(b["content"] for b in blocks)


# ── Page Header ───────────────────────────────────────────────────────────────
def page_header(icon: str, title: str, subtitle: str = "", accent: str = "#1FBACF"):
    """Render a left-border accent banner."""
    _sub = (
        f"<div style='font-size:0.83rem;color:#94a3b8;margin-top:0.25rem;'>{subtitle}</div>"
        if subtitle else ""
    )
    st.markdown(
        f"<div style='border-left:4px solid {accent};padding:0.55rem 1rem;"
        f"margin-bottom:1rem;background:rgba(255,255,255,0.03);border-radius:0 8px 8px 0;'>"
        f"<span style='font-size:1.45rem;font-weight:700;color:#f1f5f9;'>{icon}&nbsp;{title}</span>"
        f"{_sub}</div>",
        unsafe_allow_html=True,
    )
