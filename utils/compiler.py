"""
LaTeX compiler helpers: MiKTeX path cleaning, log parsing,
live preview generation, cross-browser PDF rendering, and DOCX conversion.
"""
import base64
import json
import logging
import os
import subprocess

import streamlit as st

_log = logging.getLogger("eces_compiler")


# ── MiKTeX Helpers ────────────────────────────────────────────────────────────
def _get_miktex_env() -> dict:
    """Return os.environ copy with non-directory PATH entries removed.
    MiKTeX throws Windows API error 267 if a PATH entry is a file (e.g. claude.exe)."""
    env = os.environ.copy()
    raw_path = env.get("PATH", "")
    clean_parts = [p for p in raw_path.split(os.pathsep)
                   if p.strip() and not os.path.isfile(p.strip())]
    env["PATH"] = os.pathsep.join(clean_parts)
    return env


def _clear_miktex_issues() -> None:
    """Clear MiKTeX issues.json to silence the 'check for updates' nag."""
    issues_path = os.path.join(
        os.environ.get("APPDATA", ""),
        "MiKTeX", "miktex", "config", "issues.json",
    )
    if os.path.exists(issues_path):
        try:
            with open(issues_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if any("not checked for updates" in (item.get("message") or "") for item in data):
                with open(issues_path, "w", encoding="utf-8") as fh:
                    json.dump([], fh)
        except Exception as e:
            _log.warning("Could not clear MiKTeX issues.json: %s", e)


# ── Log Parser ────────────────────────────────────────────────────────────────
def parse_latex_log(log_path: str) -> str:
    if not os.path.exists(log_path):
        return "Log file not found."
    errors = []
    try:
        with open(log_path, "r", encoding="latin-1", errors="ignore") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("!"):
                context = lines[i:i + 3]
                errors.append("".join(context).strip())
    except Exception:
        return "Could not parse log."
    return "\n\n".join(errors) if errors else "Unknown error. Check syntax."


# ── LaTeX Reference Toolbar ───────────────────────────────────────────────────
def render_toolbar():
    """Static LaTeX reference card — read-only, no rerun risk."""
    _snippets = [
        ("Bold",        r"\textbf{Text}"),
        ("Italic",      r"\textit{Text}"),
        ("Underline",   r"\underline{Text}"),
        ("Color",       r"\textcolor{ECEScyan}{Text}"),
        ("Superscript", r"\textsuperscript{th}"),
        ("Footnote",    r"\footnote{Note text}"),
        ("Line Break",  r"\\"),
        ("Escape %",    r"\%"),
        ("Spacing",     r"\vspace{0.5cm}"),
        ("En-dash",     "--"),
        ("Em-dash",     "---"),
        ("Arabic ،",    "،"),
    ]
    _cols = st.columns(4)
    for i, (_name, _code) in enumerate(_snippets):
        with _cols[i % 4]:
            st.code(_code, language="latex")
            st.caption(_name)

    with st.expander("📋 Block Templates", expanded=False):
        st.caption("Bulleted List")
        st.code("\\begin{itemize}\n    \\item Point 1\n    \\item Point 2\n\\end{itemize}", language="latex")
        st.caption("Numbered List")
        st.code("\\begin{enumerate}\n    \\item First\n    \\item Second\n\\end{enumerate}", language="latex")
        st.caption("Table")
        st.code("\\begin{tabular}{l|r}\n    Header & Value \\\\\n    \\hline\n    Row 1 & 100 \\\\\n\\end{tabular}", language="latex")


# ── Preview Generator ─────────────────────────────────────────────────────────
def generate_preview(content_latex: str, preamble_file: str, config_file: str, base_dir: str):
    """
    Compile a standalone PDF snippet using the active language's preamble.
    Returns: (pdf_path, error_msg) — one of the two will be None.
    """
    # Use a per-session unique name to prevent collisions when multiple users
    # generate previews simultaneously (they share the same container filesystem).
    _pid = st.session_state.get("_preview_id")
    if not _pid:
        import uuid
        _pid = uuid.uuid4().hex[:8]
        st.session_state["_preview_id"] = _pid
    preview_filename = f"preview_temp_{_pid}"
    preview_tex = f"{preview_filename}.tex"
    preview_pdf = f"{preview_filename}.pdf"
    preview_log = f"{preview_filename}.log"

    if os.path.exists(preview_pdf):
        os.remove(preview_pdf)
    if os.path.exists(preview_log):
        os.remove(preview_log)

    full_latex_code = (
        f"\\documentclass[a4paper,12pt]{{article}}\n"
        f"\\usepackage[margin=1cm]{{geometry}}\n"
        f"\\input{{{preamble_file}}}\n"
        f"\\input{{{config_file}}}\n"
        "\\begin{document}\n"
        + content_latex
        + "\n\\end{document}"
    )

    with open(preview_tex, "w", encoding="utf-8") as f:
        f.write(full_latex_code)

    try:
        _clear_miktex_issues()
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", preview_tex],
            cwd=base_dir,
            capture_output=True, text=True,
            env=_get_miktex_env(),
        )
        if result.returncode != 0:
            _log.warning("Preview xelatex exited with code %d", result.returncode)
        # Clean up auxiliary files
        for ext in (".aux", ".log", ".out", ".toc"):
            _aux = os.path.join(base_dir, f"{preview_filename}{ext}")
            if os.path.exists(_aux):
                try:
                    os.remove(_aux)
                except OSError:
                    pass
        if os.path.exists(preview_pdf):
            return preview_pdf, None
        else:
            error_msg = parse_latex_log(os.path.join(base_dir, preview_log))
            return None, error_msg
    except Exception as e:
        return None, str(e)


# ── PDF Renderer ──────────────────────────────────────────────────────────────
def display_pdf(pdf_path: str, display_width: int = 700):
    """Render PDF pages as PNG images for cross-browser compatibility (pymupdf)."""
    if not os.path.exists(pdf_path):
        st.error("Preview file not found.")
        return
    try:
        import fitz  # pymupdf

        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        # Page state keyed per PDF so navigation survives reruns
        _page_key = f"pdf_page_{os.path.basename(pdf_path)}"
        if _page_key not in st.session_state:
            st.session_state[_page_key] = 0

        # Prev / Next navigation
        _c1, _c2, _c3 = st.columns([1, 2, 1])
        with _c1:
            if st.button("◀ Prev", key=f"{_page_key}_prev",
                         disabled=st.session_state[_page_key] == 0,
                         use_container_width=True):
                st.session_state[_page_key] -= 1
                st.rerun()
        with _c2:
            st.markdown(
                f"<div style='text-align:center;padding:6px 0;font-size:0.85rem;"
                f"color:#94a3b8;font-weight:600;'>"
                f"Page {st.session_state[_page_key] + 1} of {total_pages}</div>",
                unsafe_allow_html=True,
            )
        with _c3:
            if st.button("Next ▶", key=f"{_page_key}_next",
                         disabled=st.session_state[_page_key] >= total_pages - 1,
                         use_container_width=True):
                st.session_state[_page_key] += 1
                st.rerun()

        # Render at resolution matched to display width
        _scale = max(2.0, display_width / 595.0)
        page = doc[st.session_state[_page_key]]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(_scale, _scale))
        # Use raw HTML <img> to bypass Streamlit's wrapper divs that cap width
        _img_b64 = base64.b64encode(pixmap.tobytes("png")).decode()
        st.markdown(
            f'<div style="overflow-x:auto;">'
            f'<img src="data:image/png;base64,{_img_b64}" '
            f'style="width:{display_width}px !important; max-width:none !important; display:block;">'
            f'</div>',
            unsafe_allow_html=True,
        )

    except ImportError:
        st.warning("pymupdf not installed. Run: pip install pymupdf")
    except Exception as e:
        st.error(f"Could not render PDF: {e}")


# ── PDF → DOCX Conversion ───────────────────────────────────────────────────
def convert_pdf_to_docx(pdf_path: str, docx_path: str) -> tuple:
    """
    Convert a compiled PDF to an editable DOCX using pdf2docx.
    Returns (docx_path, error_msg) — one will be None.
    """
    try:
        from pdf2docx import Converter
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        if os.path.exists(docx_path):
            return docx_path, None
        return None, "DOCX file was not created."
    except ImportError:
        return None, "pdf2docx is not installed. Run: pip install pdf2docx"
    except Exception as e:
        _log.warning("DOCX conversion failed: %s", e)
        return None, f"DOCX conversion failed: {e}"
