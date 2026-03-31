"""
Central configuration — constants, labels, and project structure maps.
No Streamlit imports here; this module is pure Python.
"""
import os

# ── Directory Paths ────────────────────────────────────────────────────
BASE_DIR         = os.getcwd()
CHARTS_EN_DIR    = os.path.join(BASE_DIR, "images", "charts")
CHARTS_AR_DIR    = os.path.join(BASE_DIR, "images", "charts_ar")
STATIC_IMG_DIR   = os.path.join(BASE_DIR, "images", "static")
BACKUP_DIR       = os.path.join(BASE_DIR, "templates_backup")
OVERRIDES_DIR    = os.path.join(BASE_DIR, "overrides")
CUSTOM_SECTIONS_FILE = os.path.join(BASE_DIR, "custom_sections.json")

# ── Auth Paths ─────────────────────────────────────────────────────────
USERS_FILE    = os.path.join(BASE_DIR, "users.json")
ACTIVITY_LOG  = os.path.join(BASE_DIR, "activity.log")
SESSION_TIMEOUT_MINUTES = 30

# ── Role Permissions (ordered to match the report-production workflow) ─
ROLE_PERMISSIONS = {
    "admin": [
        "📁 Issue Manager",
        "⚙️ Report Variables",
        "📊 Chart Manager",
        "📝 Report Sections",
        "🚀 Finalize & Publish",
        "📋 Activity Log",
        "👥 User Management",
    ],
    "editor": [
        "📁 Issue Manager",
        "⚙️ Report Variables",
        "📊 Chart Manager",
        "📝 Report Sections",
        "🚀 Finalize & Publish"
    ],
    "viewer": ["📝 Report Sections"],
}

# ── Workflow Step Definitions ──────────────────────────────────────────
WORKFLOW_STEPS = [
    {"num": 1, "view_key": "📁 Issue Manager",     "label": "Issue Manager",     "short": "Pick / create issue",    "icon": "📁"},
    {"num": 2, "view_key": "⚙️ Report Variables",  "label": "Report Variables",  "short": "Set number & dates",     "icon": "⚙️"},
    {"num": 3, "view_key": "📊 Chart Manager",      "label": "Chart Manager",     "short": "Upload chart images",    "icon": "📊"},
    {"num": 4, "view_key": "📝 Report Sections",    "label": "Report Sections",   "short": "Edit written content",   "icon": "📝"},
    {"num": 5, "view_key": "🚀 Finalize & Publish", "label": "Finalize & Publish","short": "Compile & download PDF", "icon": "🚀"},
]

# ── Project File Maps ──────────────────────────────────────────────────
PROJECT_CONFIG = {
    "English": {
        "main":     "main.tex",
        "config":   "config.tex",
        "preamble": "preamble.tex",
        "sections": {
            "Executive Summary":       "content/01_exec_summary.tex",
            "Macroeconomic Overview":  "content/02_macro_overview.tex",
            "Analysis: Overall Index": "content/03_analysis_overall.tex",
            "Analysis: Constraints":   "content/04_constraints.tex",
            "Analysis: Sub-Indices":   "content/05_subindices.tex",
            "Appendix: Data Tables":   "content/06_tables.tex",
            "Cover Page Text":         "static_sections/00_cover.tex",
            "About ECES":              "static_sections/00_about_eces.tex",
            "Methodology":             "static_sections/00_methodology.tex",
        },
    },
    "Arabic": {
        "main":     "main_ar.tex",
        "config":   "config_ar.tex",
        "preamble": "preamble_ar.tex",
        "sections": {
            "Executive Summary":       "content/01_exec_summary_ar.tex",
            "Macroeconomic Overview":  "content/02_macro_overview_ar.tex",
            "Analysis: Overall Index": "content/03_analysis_overall_ar.tex",
            "Analysis: Constraints":   "content/04_constraints_ar.tex",
            "Analysis: Sub-Indices":   "content/05_subindices_ar.tex",
            "Appendix: Data Tables":   "content/06_tables_ar.tex",
            "Cover Page Text":         "static_sections/00_cover_ar.tex",
            "About ECES":              "static_sections/00_about_eces_ar.tex",
            "Methodology":             "static_sections/00_methodology_ar.tex",
        },
    },
}

# ── Custom Section Templates ───────────────────────────────────────────
SECTION_TEMPLATES = {
    "text": (
        "% =========================================================\n"
        "% Custom Section: {title}\n"
        "% =========================================================\n"
        "\\newgeometry{{left=2cm, right=2cm, top=3cm, bottom=2.5cm}}\n\n"
        "\\noindent\n"
        "{{\\fontsize{{18}}{{22}}\\selectfont \\textbf{{\\color{{ecestitle}} {title}}}}}\n"
        "\\vspace{{1em}}\n\n"
        "\\ECESContent{{{id}_p1}}{{[TODO: Enter paragraph 1.]}}\n\n"
        "\\vspace{{0.8em}}\n\n"
        "\\ECESContent{{{id}_p2}}{{[TODO: Enter paragraph 2.]}}\n\n"
        "\\clearpage\n"
    ),
    "chart": (
        "% =========================================================\n"
        "% Custom Section: {title}\n"
        "% =========================================================\n"
        "\\newgeometry{{left=2cm, right=2cm, top=3cm, bottom=2.5cm}}\n\n"
        "\\noindent\n"
        "{{\\fontsize{{18}}{{22}}\\selectfont \\textbf{{\\color{{ecestitle}} {title}}}}}\n"
        "\\vspace{{1em}}\n\n"
        "%% TODO: Upload chart image via Chart Manager\n"
        "\\begin{{figure}}[h!]\n"
        "    \\centering\n"
        "    \\includegraphics[width=\\linewidth]{{custom_chart.png}}\n"
        "\\end{{figure}}\n\n"
        "\\clearpage\n"
    ),
    "mixed": (
        "% =========================================================\n"
        "% Custom Section: {title}\n"
        "% =========================================================\n"
        "\\newgeometry{{left=2cm, right=2cm, top=3cm, bottom=2.5cm}}\n\n"
        "\\noindent\n"
        "{{\\fontsize{{18}}{{22}}\\selectfont \\textbf{{\\color{{ecestitle}} {title}}}}}\n"
        "\\vspace{{1em}}\n\n"
        "\\ECESContent{{{id}_intro}}{{[TODO: Enter introduction text.]}}\n\n"
        "\\vspace{{0.8em}}\n\n"
        "%% TODO: Upload chart image via Chart Manager\n"
        "\\begin{{figure}}[h!]\n"
        "    \\centering\n"
        "    \\includegraphics[width=\\linewidth]{{custom_chart.png}}\n"
        "\\end{{figure}}\n\n"
        "\\ECESContent{{{id}_analysis}}{{[TODO: Enter analysis text.]}}\n\n"
        "\\clearpage\n"
    ),
    "table": (
        "% =========================================================\n"
        "% Custom Section: {title}\n"
        "% =========================================================\n"
        "\\newgeometry{{left=2cm, right=2cm, top=3cm, bottom=2.5cm}}\n\n"
        "\\noindent\n"
        "{{\\fontsize{{18}}{{22}}\\selectfont \\textbf{{\\color{{ecestitle}} {title}}}}}\n"
        "\\vspace{{1em}}\n\n"
        "\\ECESContent{{{id}_caption}}{{[TODO: Table caption.]}}\n\n"
        "%% TODO: Upload table image via Chart Manager\n"
        "\\begin{{figure}}[h!]\n"
        "    \\centering\n"
        "    \\includegraphics[width=\\linewidth, height=0.38\\textheight, keepaspectratio]{{custom_table.png}}\n"
        "\\end{{figure}}\n\n"
        "\\clearpage\n"
    ),
}

# ── Human-readable Labels ──────────────────────────────────────────────
SLOT_LABELS = {
    "exec_intro":              "📄 Introduction Paragraph",
    "exec_box_overall":        "📊 Key Findings — Overall Index",
    "exec_box_size":           "📏 Key Findings — By Firm Size",
    "exec_box_sector":         "🏭 Key Findings — By Sector",
    "exec_box_challenges":     "⚠️ Key Findings — Challenges",
    "exec_bpi_analysis":       "📈 BPI Performance Analysis",
    "exec_expectations":       "🔮 Performance Expectations",
    "exec_size_detail":        "📏 Detailed Size Analysis",
    "exec_sector_summary":     "🏭 Sector Overview",
    "exec_manufacturing":      "🔧 Manufacturing Sector Detail",
    "exec_best_sector":        "🌟 Best Performing Sector Detail",
    "exec_challenges_headline":"⚠️ Challenges — Headline",
    "exec_challenges_body":    "📋 Challenges — Full Analysis",
    "exec_sme_comparison":     "🏢 SMEs vs Large Firms",
    "exec_priorities":         "🎯 Business Priorities",
    "exec_macro_global":       "🌍 Macro — Global Outlook",
    "exec_macro_local":        "🇪🇬 Macro — Local Outlook",
    "macro_global_intro":      "🌍 Global Overview — Introduction",
    "macro_global_growth":     "📉 Global Growth Forecasts",
    "macro_global_inflation":  "💹 Global Inflation Trends",
    "macro_global_pmi":        "📊 Global PMI Analysis",
    "macro_local_intro":       "🇪🇬 Local Economy — Introduction",
    "macro_imf_review":        "🏦 IMF Review & Outlook",
    "macro_imf_reforms":       "📋 Structural Reform Priorities",
    "macro_gdp_growth":        "📈 GDP Growth Analysis",
    "macro_inflation":         "💰 Inflation Analysis",
    "macro_foreign_bop":       "💱 Balance of Payments",
    "macro_foreign_current":   "📊 Current Account",
    "macro_foreign_petroleum": "⛽ Petroleum Trade Balance",
    "macro_foreign_assets":    "🏦 Net Foreign Assets",
    "macro_foreign_reserves":  "💵 International Reserves",
    "macro_foreign_exchange":  "💱 Exchange Rate",
    "macro_public_finance":    "🏛️ Public Finance",
    "overall_intro":           "📊 Overall Index — Introduction",
    "overall_bpi_text":        "📈 BPI Performance Text",
    "overall_expectations":    "🔮 Expectations Analysis",
    "overall_size_text":       "📏 Performance by Firm Size",
    "overall_expectations_size":"🔮 Expectations by Firm Size",
    "overall_sector_intro":    "🏭 Sector Performance Intro",
    "overall_sector_analysis": "📋 Detailed Sector Analysis",
    "overall_sector_outlook_intro": "🔮 Sector Outlook Introduction",
    "overall_sector_outlook":  "📊 Sector Outlook Details",
    "constraints_intro":       "⚠️ Constraints — Introduction",
    "constraints_main":        "📋 Main Constraints Analysis",
    "constraints_by_size_intro":"📏 Constraints by Size — Intro",
    "constraints_by_size":     "📊 Constraints by Size — Detail",
    "constraints_by_sector":   "🏭 Constraints by Sector",
    "priorities_intro":        "🎯 Priorities — Introduction",
    "priorities_main":         "📋 Priorities Analysis",
    "priorities_by_size":      "📏 Priorities by Firm Size",
    "priorities_by_sector":    "🏭 Priorities by Sector",
    "outlook_community":       "🔮 Business Community Outlook",
    "sub_performance_intro":   "📊 Sub-Indices Performance Intro",
    "sub_production_sales":    "🏭 Production & Sales Analysis",
    "sub_prices_wages":        "💰 Prices & Wages Analysis",
    "sub_investment_employment":"📈 Investment & Employment",
    "sub_expectations_intro":  "🔮 Sub-Indices Expectations Intro",
    "sub_expectations_production":"🏭 Production Expectations",
    "sub_expectations_prices": "💰 Price Expectations",
    "sub_expectations_investment":"📈 Investment Expectations",
}

VARIABLE_LABELS = {
    "IssueNumber":          "Issue Number",
    "CurrentQuarterText":   "Current Quarter",
    "NextQuarterText":      "Next Quarter",
    "PreviousQuarterText":  "Previous Quarter",
    "CorrespQuarterText":   "Corresponding Quarter (Last Year)",
    "CurrentFiscalYear":    "Fiscal Year",
}

CHART_LABELS = {
    "ch1.png":  "Executive Summary — BPI Overall Index",
    "ch2.png":  "Executive Summary — Performance by Firm Size",
    "ch3.png":  "Executive Summary — Challenges & Macro Overview",
    "ch4.png":  "Methodology — Sector / Size Composition",
    "ch5.png":  "Methodology — Index Calculation Visual",
    "ch6.png":  "Macro Overview — GDP Growth",
    "ch7.png":  "Macro Overview — Inflation",
    "ch8.png":  "Macro Overview — Public Finance",
    "ch9.png":  "Overall Analysis — BBI Overall Index",
    "ch10.png": "Overall Analysis — BBI by Firm Size",
    "ch11.png": "Overall Analysis — BBI by Sector",
    "ch12.png": "Overall Analysis — Sector Outlook",
    "ch13.png": "Constraints — Overall Constraints",
    "ch14.png": "Constraints — By Firm Size",
    "ch15.png": "Constraints — By Sector",
    "ch16.png": "Constraints — Business Priorities",
    "ch17.png": "Constraints — Priorities by Firm Size",
    "ch18.png": "Constraints — Priorities by Sector",
    "ch19.png": "Constraints — Business Community Outlook",
    "ch20.png": "Sub-Indices — Performance Overview",
    "ch21.png": "Sub-Indices — Prices & Wages",
    "ch22.png": "Sub-Indices — Investment & Employment",
    "ch23.png": "Sub-Indices — Expectations Overview",
    "ch24.png": "Sub-Indices — Price & Wage Expectations",
    "ch25.png": "Sub-Indices — Investment & Employment Expectations",
    "t1.png":   "Table A-1 — Performance Index by Firm Size",
    "t2.png":   "Table A-2 — Performance Index by Sector",
    "t3.png":   "Table A-3 — Constraints Ranking",
    "t4.png":   "Table A-4 — Priorities Ranking",
}

CHART_SECTIONS = {
    "Executive Summary":  ["ch1.png", "ch2.png", "ch3.png"],
    "Methodology":        ["ch4.png", "ch5.png"],
    "Macro Overview":     ["ch6.png", "ch7.png", "ch8.png"],
    "Overall Analysis":   ["ch9.png", "ch10.png", "ch11.png", "ch12.png"],
    "Constraints":        ["ch13.png", "ch14.png", "ch15.png", "ch16.png",
                           "ch17.png", "ch18.png", "ch19.png"],
    "Sub-Indices":        ["ch20.png", "ch21.png", "ch22.png",
                           "ch23.png", "ch24.png", "ch25.png"],
    "Tables":             ["t1.png", "t2.png", "t3.png", "t4.png"],
}
