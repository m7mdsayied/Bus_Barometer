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
    # ── Executive Summary (EN) ─────────────────────────────────────────
    "title_exec_summary":           "✏️ [TITLE] Executive Summary section heading",
    "exec_intro":                   "📄 Exec Summary – Opening paragraph (p.2)",
    "exec_box_overall":             "📊 Exec Summary – Box: Overall BPI findings (p.2)",
    "exec_box_size":                "📏 Exec Summary – Box: By firm size (p.2)",
    "exec_box_sector":              "🏭 Exec Summary – Box: By sector (p.2)",
    "exec_box_challenges":          "⚠️ Exec Summary – Box: Challenges (p.2)",
    "exec_bpi_analysis":            "📈 Exec Summary – BPI analysis paragraph (p.2, beside chart)",
    "exec_expectations":            "🔮 Exec Summary – Expectations paragraph (p.2, bottom)",
    "exec_size_detail":             "📏 Exec Summary – Size analysis text (p.3, left column)",
    "exec_sector_summary":          "🏭 Exec Summary – Sectorally intro text (p.3)",
    "exec_manufacturing":           "🔧 Exec Summary – Manufacturing sector text (p.3)",
    "exec_best_sector":             "🌟 Exec Summary – Best sector text (p.3)",
    "exec_challenges_headline":     "⚠️ Exec Summary – Challenges bold headline (p.4)",
    "exec_challenges_body":         "📋 Exec Summary – Challenges body (p.4, ranked list)",
    "exec_sme_comparison":          "🏢 Exec Summary – SME vs large firms challenges (p.4)",
    "exec_priorities":              "🎯 Exec Summary – Business priorities paragraph (p.4)",
    "exec_macro_global":            "🌍 Exec Summary – Macro: Global bullet (p.4)",
    "exec_macro_local":             "🇪🇬 Exec Summary – Macro: Local bullet (p.4)",
    # ── Executive Summary (AR) ─────────────────────────────────────────
    "title_exec_summary_ar":        "✏️ [TITLE-AR] ملخص تنفيذي – Section heading (p.2 AR)",
    "exec_intro_ar":                "📄 Exec Summary AR – Opening paragraph (p.2)",
    "exec_box_overall_ar":          "📊 Exec Summary AR – Box: Overall BPI findings (p.2)",
    "exec_box_size_ar":             "📏 Exec Summary AR – Box: By firm size (p.2)",
    "exec_box_sector_ar":           "🏭 Exec Summary AR – Box: By sector (p.2)",
    "exec_box_challenges_ar":       "⚠️ Exec Summary AR – Box: Challenges (p.2)",
    "exec_bpi_analysis_ar":         "📈 Exec Summary AR – BPI analysis paragraph (p.2)",
    "exec_expectations_ar":         "🔮 Exec Summary AR – Expectations paragraph (p.2)",
    "exec_size_detail_ar":          "📏 Exec Summary AR – Size analysis text (p.3)",
    "exec_sector_summary_ar":       "🏭 Exec Summary AR – Sectorally intro text (p.3)",
    "exec_manufacturing_ar":        "🔧 Exec Summary AR – Manufacturing sector text (p.3)",
    "exec_best_sector_ar":          "🌟 Exec Summary AR – Best sector text (p.3)",
    "exec_challenges_headline_ar":  "⚠️ Exec Summary AR – Challenges bold headline (p.4)",
    "exec_challenges_body_ar":      "📋 Exec Summary AR – Challenges body (p.4)",
    "exec_sme_comparison_ar":       "🏢 Exec Summary AR – SME vs large firms challenges (p.4)",
    "exec_priorities_ar":           "🎯 Exec Summary AR – Business priorities paragraph (p.4)",
    "exec_macro_global_ar":         "🌍 Exec Summary AR – Macro: Global bullet (p.4)",
    "exec_macro_local_ar":          "🇪🇬 Exec Summary AR – Macro: Local bullet (p.4)",
    # ── Macro Overview (EN) ───────────────────────────────────────────
    "title_macro_overview":         "✏️ [TITLE] Macroeconomic Overview section heading",
    "macro_global_intro":           "🌍 Macro Overview – Global bold headline (p.8)",
    "macro_global_p1":              "📉 Macro Overview – Global growth paragraph 1 (p.8)",
    "macro_global_p2":              "💹 Macro Overview – Global inflation paragraph (p.8)",
    "macro_global_p3":              "📊 Macro Overview – PMI/Composite paragraph (p.8)",
    "macro_local_p1":               "🇪🇬 Macro Overview – Local headline paragraph (p.8)",
    "macro_local_p2":               "🏦 Macro Overview – IMF/WB review paragraph (p.8)",
    "macro_local_p3":               "📋 Macro Overview – Structural reforms paragraph (p.8)",
    "macro_gdp_growth":             "📈 Macro Overview – GDP bullet (p.9, under Figure 1)",
    "macro_inflation_p1":           "💰 Macro Overview – Inflation bullet (p.9)",
    "macro_inflation_p2":           "💰 Macro Overview – CBE rate paragraph (p.9)",
    "macro_bop_p1":                 "💱 Macro Overview – BOP paragraph 1 (p.10)",
    "macro_bop_p2":                 "📊 Macro Overview – Current account paragraph (p.10)",
    "macro_bop_p3":                 "📊 Macro Overview – BOP additional paragraph (p.10)",
    "macro_nfa_p1":                 "🏦 Macro Overview – Net foreign assets paragraph (p.10)",
    "macro_reserves_p1":            "💵 Macro Overview – International reserves paragraph (p.10)",
    "macro_exchange_rate_p1":       "💱 Macro Overview – Exchange rate paragraph (p.11)",
    "macro_public_finance_intro":   "🏛️ Macro Overview – Budget deficit intro (p.11)",
    "macro_public_finance_b1":      "🏛️ Macro Overview – Budget bullet 1 (p.11)",
    "macro_public_finance_b2":      "🏛️ Macro Overview – Budget bullet 2 (p.11)",
    "macro_public_finance_b3":      "🏛️ Macro Overview – Budget bullet 3 (p.11)",
    # ── Macro Overview (AR) ───────────────────────────────────────────
    "title_macro_overview_ar":      "✏️ [TITLE-AR] نظرة عامة – Macro overview heading (p.8 AR)",
    "macro_global_intro_ar":        "🌍 Macro Overview AR – Global bold headline (p.8)",
    "macro_global_p1_ar":           "📉 Macro Overview AR – Global growth paragraph 1 (p.8)",
    "macro_global_p2_ar":           "💹 Macro Overview AR – Global inflation paragraph (p.8)",
    "macro_global_p3_ar":           "📊 Macro Overview AR – PMI/Composite paragraph (p.8)",
    "macro_local_p1_ar":            "🇪🇬 Macro Overview AR – Local headline paragraph (p.8)",
    "macro_local_p2_ar":            "🏦 Macro Overview AR – IMF/WB review paragraph (p.8)",
    "macro_local_p3_ar":            "📋 Macro Overview AR – Structural reforms paragraph (p.8)",
    # ── Overall Index (EN) ────────────────────────────────────────────
    "title_bbi":                    "✏️ [TITLE] Business Barometer Index (BBI) heading",
    "title_section_i":              "✏️ [TITLE] Section I heading (Overall Index)",
    "overall_intro":                "📊 Overall Index – Bold sub-headline (p.12)",
    "overall_bpi_text":             "📈 Overall Index – BPI analysis text, 1-1 Overall index (p.12)",
    "overall_expectations":         "🔮 Overall Index – Expectations analysis text (p.12)",
    "overall_size_perf":            "📏 Overall Index – 1-2 Size performance text (p.13)",
    "overall_size_exp":             "🔮 Overall Index – 1-2 Size expectations text (p.13)",
    "overall_sector_intro":         "🏭 Overall Index – 1-3 Sector intro text (p.13)",
    "overall_sector_perf_intro":    "📋 Overall Index – Sector analysis standard intro sentence (p.14)",
    "overall_perf_manufacturing":   "🔧 Overall Index – Manufacturing bullet (p.14)",
    "overall_perf_construction":    "🏗️ Overall Index – Construction bullet (p.14)",
    "overall_perf_tourism":         "✈️ Overall Index – Tourism bullet (p.14)",
    "overall_perf_transport":       "🚚 Overall Index – Transport bullet (p.14)",
    "overall_perf_telecom":         "📡 Overall Index – Telecom bullet (p.14)",
    "overall_perf_financial":       "🏦 Overall Index – Financial services bullet (p.14)",
    "overall_sector_exp_intro":     "🔮 Overall Index – Outlook intro sentence (p.14)",
    "overall_exp_manufacturing":    "🔧 Overall Index – Manufacturing outlook bullet (p.14–15)",
    "overall_exp_construction":     "🏗️ Overall Index – Construction outlook bullet (p.15)",
    "overall_exp_tourism":          "✈️ Overall Index – Tourism outlook bullet (p.15)",
    "overall_exp_transport":        "🚚 Overall Index – Transport outlook bullet (p.15)",
    "overall_exp_telecom":          "📡 Overall Index – Telecom outlook bullet (p.15)",
    "overall_exp_financial":        "🏦 Overall Index – Financial services outlook bullet (p.15)",
    # ── Overall Index (AR) ────────────────────────────────────────────
    "title_bbi_ar":                 "✏️ [TITLE-AR] مؤشر بارومتر الأعمال heading (p.12 AR)",
    "title_section_i_ar":           "✏️ [TITLE-AR] أولاً – Section I heading (p.12 AR)",
    "title_subsection_11_ar":       "✏️ [TITLE-AR] 1-1 Overall index sub-heading (p.12 AR)",
    "title_subsection_12_ar":       "✏️ [TITLE-AR] 1-2 By firm size sub-heading (p.13 AR)",
    "title_subsection_13_ar":       "✏️ [TITLE-AR] 1-3 By sector sub-heading (p.14 AR)",
    "overall_intro_ar":             "📊 Overall Index AR – Bold sub-headline (p.12)",
    "overall_bpi_text_ar":          "📈 Overall Index AR – BPI analysis text (p.12)",
    "overall_expectations_ar":      "🔮 Overall Index AR – Expectations analysis text (p.12)",
    "overall_size_perf_ar":         "📏 Overall Index AR – 1-2 Size performance text (p.13)",
    "overall_size_exp_ar":          "🔮 Overall Index AR – 1-2 Size expectations text (p.13)",
    "overall_sector_intro_ar":      "🏭 Overall Index AR – 1-3 Sector intro text (p.13)",
    "overall_sector_perf_intro_ar": "📋 Overall Index AR – Sector analysis intro sentence (p.14)",
    "overall_perf_manufacturing_ar":"🔧 Overall Index AR – Manufacturing bullet (p.14)",
    "overall_perf_construction_ar": "🏗️ Overall Index AR – Construction bullet (p.14)",
    "overall_perf_tourism_ar":      "✈️ Overall Index AR – Tourism bullet (p.14)",
    "overall_perf_transport_ar":    "🚚 Overall Index AR – Transport bullet (p.14)",
    "overall_perf_telecom_ar":      "📡 Overall Index AR – Telecom bullet (p.14)",
    "overall_perf_financial_ar":    "🏦 Overall Index AR – Financial services bullet (p.14)",
    "overall_sector_exp_intro_ar":  "🔮 Overall Index AR – Outlook intro sentence (p.14)",
    "overall_exp_manufacturing_ar": "🔧 Overall Index AR – Manufacturing outlook bullet (p.14–15)",
    "overall_exp_construction_ar":  "🏗️ Overall Index AR – Construction outlook bullet (p.15)",
    "overall_exp_tourism_ar":       "✈️ Overall Index AR – Tourism outlook bullet (p.15)",
    "overall_exp_transport_ar":     "🚚 Overall Index AR – Transport outlook bullet (p.15)",
    "overall_exp_telecom_ar":       "📡 Overall Index AR – Telecom outlook bullet (p.15)",
    "overall_exp_financial_ar":     "🏦 Overall Index AR – Financial services outlook bullet (p.15)",
    # ── Constraints & Priorities (EN) ────────────────────────────────
    "title_section_ii":             "✏️ [TITLE] Section II heading (Constraints & Priorities)",
    "title_constraints_21":         "✏️ [TITLE] Sub-heading 2-1 (Constraints faced)",
    "title_constraints_211":        "✏️ [TITLE] Sub-heading 2-1-1 (By firm size)",
    "title_constraints_212":        "✏️ [TITLE] Sub-heading 2-1-2 (By sector)",
    "title_priorities_22":          "✏️ [TITLE] Sub-heading 2-2 (Priorities)",
    "title_priorities_221":         "✏️ [TITLE] Sub-heading 2-2-1 (Priorities by size)",
    "title_priorities_222":         "✏️ [TITLE] Sub-heading 2-2-2 (Priorities by sector)",
    "title_outlook_community":      "✏️ [TITLE] Business community expectations heading",
    "constraints_intro":            "⚠️ Constraints – 2-1 Bold headline (p.16)",
    "constraints_main_text_p1":     "📋 Constraints – Intro sentence referencing Fig.2-1 (p.16)",
    "constraints_main_text_p2":     "📋 Constraints – Top 5 constraints body text (p.16)",
    "constraints_main_text_p3":     "📋 Constraints – Additional constraints body text (p.16)",
    "constraints_by_size_p1":       "📏 Constraints – 2-1-1 Size intro sentence (p.17)",
    "constraints_by_size_p2":       "📊 Constraints – Large firms constraint ranking (p.17)",
    "constraints_by_size_p3":       "📊 Constraints – SME constraint ranking (p.17)",
    "constraints_by_size_p4":       "📊 Constraints – Figure 2-2 reference sentence (p.17)",
    "constraints_by_sector":        "🏭 Constraints – 2-1-2 Sector constraints text (p.18)",
    "priorities_headline":          "🎯 Priorities – 2-2 Bold headline (p.20)",
    "priorities_all_firms":         "📋 Priorities – All firms body text (p.20)",
    "priorities_large_firms":       "📏 Priorities – Large vs SME differences text (p.20)",
    "priorities_by_size_intro":     "📏 Priorities – 2-2-1 'Comparing priorities...' bold text (p.21)",
    "priorities_by_size":           "📏 Priorities – 2-2-1 Size priorities body text (p.21)",
    "priorities_by_sector_text":    "🏭 Priorities – 2-2-2 Sector priorities body text (p.22)",
    "outlook_community":            "🔮 Constraints – Business expectations intro text (p.23)",
    # ── Constraints & Priorities (AR) ────────────────────────────────
    "title_section_ii_ar":          "✏️ [TITLE-AR] ثانياً – Section II heading (p.16 AR)",
    "title_constraints_12_ar":      "✏️ [TITLE-AR] 1-2 Constraints sub-heading (p.16 AR)",
    "title_constraints_112_ar":     "✏️ [TITLE-AR] 1-1-2 By size sub-heading (p.17 AR)",
    "title_constraints_212_ar":     "✏️ [TITLE-AR] 2-1-2 By sector sub-heading (p.18 AR)",
    "title_priorities_22_ar":       "✏️ [TITLE-AR] 2-2 Priorities heading (p.20 AR)",
    "title_priorities_122_ar":      "✏️ [TITLE-AR] 1-2-2 Priorities by size heading (p.21 AR)",
    "title_priorities_222_ar":      "✏️ [TITLE-AR] 2-2-2 Priorities by sector heading (p.22 AR)",
    "title_outlook_community_ar":   "✏️ [TITLE-AR] Business community expectations heading (p.23 AR)",
    "constraints_intro_ar":         "⚠️ Constraints AR – Bold headline (p.16)",
    "constraints_main_text_p1_ar":  "📋 Constraints AR – Intro sentence referencing Fig.1-2 (p.16)",
    "constraints_main_text_p2_ar":  "📋 Constraints AR – Top constraints body text (p.16)",
    "constraints_main_text_p3_ar":  "📋 Constraints AR – Additional constraints body text (p.16)",
    "constraints_by_size_p1_ar":    "📏 Constraints AR – 1-1-2 Size intro sentence (p.17)",
    "constraints_by_size_p2_ar":    "📊 Constraints AR – Large firms constraint ranking (p.17)",
    "constraints_by_size_p3_ar":    "📊 Constraints AR – SME constraint ranking (p.17)",
    "constraints_by_size_p4_ar":    "📊 Constraints AR – Figure 1-3 reference sentence (p.17)",
    "constraints_by_sector_ar":     "🏭 Constraints AR – 2-1-2 Sector constraints text (p.18)",
    "priorities_headline_ar":       "🎯 Priorities AR – 2-2 Bold headline (p.20)",
    "priorities_all_firms_ar":      "📋 Priorities AR – All firms body text (p.20)",
    "priorities_large_firms_ar":    "📏 Priorities AR – Large vs SME differences text (p.20)",
    "priorities_size_intro_ar":     "📏 Priorities AR – 1-2-2 Bold intro sentence (p.21)",
    "priorities_by_size_p1_ar":     "📏 Priorities AR – 1-2-2 Size priorities body text p.1 (p.21)",
    "priorities_by_size_p2_ar":     "📏 Priorities AR – 1-2-2 Size priorities body text p.2 (p.21)",
    "priorities_by_sector_ar":      "🏭 Priorities AR – 2-2-2 Sector priorities body text (p.22)",
    "constraints_outlook_ar":       "🔮 Constraints AR – Business expectations intro text (p.23)",
    # ── Sub-Indices (EN) ─────────────────────────────────────────────
    "title_section_iii":            "✏️ [TITLE] Section III heading (Sub-Indices)",
    "title_subindices_31":          "✏️ [TITLE] Sub-heading 3.1 (Performance evaluation)",
    "title_subindices_32":          "✏️ [TITLE] Sub-heading 3.2 (Performance expectations)",
    "title_subindices_prices_exp":  "✏️ [TITLE] Prices/Wages expectations heading",
    "title_subindices_inv_exp":     "✏️ [TITLE] Investment/Employment expectations headline",
    "subindices_perf_p1":           "📊 Sub-Indices – 3.1 Large firms production/sales analysis (p.24)",
    "subindices_perf_p2":           "📊 Sub-Indices – 3.1 SME performance analysis (p.24)",
    "subindices_prices_wages_intro":"💰 Sub-Indices – Prices/wages bold headline (p.25)",
    "subindices_prices_wages_p1":   "💰 Sub-Indices – Prices/wages analysis text (p.25)",
    "subindices_inv_emp_intro":     "📈 Sub-Indices – Investment/employment bold headline (p.25)",
    "subindices_inv_emp_large":     "📈 Sub-Indices – Large firms investment/employment bullet (p.25)",
    "subindices_inv_emp_sme":       "📈 Sub-Indices – SME investment/employment bullet (p.25)",
    "subindices_exp_intro":         "🔮 Sub-Indices – 3.2 Expectations bold headline (p.26)",
    "subindices_exp_large":         "🏭 Sub-Indices – 3.2 Large firms expectations text (p.26)",
    "subindices_exp_sme":           "🏭 Sub-Indices – 3.2 SME expectations text (p.26)",
    "subindices_price_wage_exp_headline": "💰 Sub-Indices – Prices/wages expectations bold headline (p.27)",
    "subindices_price_wage_exp_p1": "💰 Sub-Indices – Prices/wages expectations text (p.27)",
    "subindices_price_wage_exp_p2": "💰 Sub-Indices – SME prices/wages expectations text (p.27)",
    "subindices_inv_emp_exp_body":  "📈 Sub-Indices – Investment/employment expectations text (p.27)",
    # ── Sub-Indices (AR) ─────────────────────────────────────────────
    "title_section_iii_ar":         "✏️ [TITLE-AR] ثالثاً – Section III heading (p.23 AR)",
    "title_subindices_31_ar":       "✏️ [TITLE-AR] 3.1 Performance sub-heading (p.23 AR)",
    "title_subindices_32_ar":       "✏️ [TITLE-AR] 3.2 Expectations sub-heading (p.26 AR)",
    "subindices_perf_p1_ar":        "📊 Sub-Indices AR – 3.1 Large firms analysis (p.23)",
    "subindices_perf_p2_ar":        "📊 Sub-Indices AR – 3.1 SME performance analysis (p.23)",
    "subindices_prices_wages_intro_ar":  "💰 Sub-Indices AR – Prices/wages bold headline (p.24)",
    "subindices_prices_wages_p1_ar":     "💰 Sub-Indices AR – Prices/wages analysis text (p.24)",
    "subindices_inv_emp_intro_ar":       "📈 Sub-Indices AR – Investment/employment bold headline (p.24)",
    "subindices_inv_emp_large_ar":       "📈 Sub-Indices AR – Large firms investment/employment bullet (p.24)",
    "subindices_inv_emp_sme_ar":         "📈 Sub-Indices AR – SME investment/employment bullet (p.24)",
    "subindices_exp_intro_ar":           "🔮 Sub-Indices AR – 3.2 Expectations bold headline (p.25)",
    "subindices_exp_large_ar":           "🏭 Sub-Indices AR – 3.2 Large firms expectations text (p.25)",
    "subindices_exp_sme_ar":             "🏭 Sub-Indices AR – 3.2 SME expectations text (p.25)",
    "subindices_exp_prices_wages_intro_ar": "💰 Sub-Indices AR – Prices/wages expectations bold headline (p.26)",
    "subindices_exp_prices_p1_ar":       "💰 Sub-Indices AR – Prices/wages expectations text (p.26)",
    "subindices_exp_wages_sme_ar":       "💰 Sub-Indices AR – SME wages expectations text (p.26)",
    "subindices_exp_inv_emp_intro_ar":   "📈 Sub-Indices AR – Investment/employment expectations headline (p.27)",
    "subindices_exp_inv_emp_p1_ar":      "📈 Sub-Indices AR – Investment/employment expectations text (p.27)",
    # ── Tables (EN) ───────────────────────────────────────────────────
    "title_tables_index":           "✏️ [TITLE] Tables Index section heading (p.28)",
    "title_tables_appendix":        "✏️ [TITLE] Tables Appendix section heading (p.29)",
    # ── Tables (AR) ───────────────────────────────────────────────────
    "title_tables_index_ar":        "✏️ [TITLE-AR] ملحق الجداول heading (p.27 AR)",
    "title_tables_appendix_ar":     "✏️ [TITLE-AR] ملحق الجداول heading (p.28 AR)",
    "title_table3_ar":              "✏️ [TITLE-AR] Table 3 caption (p.28 AR)",
    "title_table4_ar":              "✏️ [TITLE-AR] Table 4 caption (p.28 AR)",
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
    "ch1.png":  "Exec Summary – BPI Overall Index trend chart (p.2, beside analysis)",
    "ch2.png":  "Exec Summary – BPI by Firm Size (p.3, beside size analysis)",
    "ch3.png":  "Exec Summary – BPI by Economic Sector (p.3, full-width)",
    "ch4.png":  "Methodology – Sector / Size Composition chart",
    "ch5.png":  "Methodology – Index Calculation Visual",
    "ch6.png":  "Macro Overview – GDP Growth chart (p.9, Figure 1)",
    "ch7.png":  "Macro Overview – Inflation & CBE Rate chart (p.9, Figure 2)",
    "ch8.png":  "Macro Overview – Public Finance chart (p.11)",
    "ch9.png":  "Overall Index – Fig 1.1 (Performance) + Fig 1.2 (Outlook) combined chart (p.12)",
    "ch10.png": "Overall Index – Fig 1.3 (Perf by size) + Fig 1.4 (Outlook by size) combined (p.13)",
    "ch11.png": "Overall Index – Fig 1.5: BBI by Economic Sectors – Past Performance (p.14)",
    "ch12.png": "Overall Index – Fig 1.6: BBI by Economic Sectors – Outlook (p.15)",
    "ch13.png": "Constraints – Fig 2.1: Constraints ranked by severity, all firms (p.16)",
    "ch14.png": "Constraints – Fig 2.2: Constraints by firm size (Large vs SMEs) (p.17)",
    "ch15.png": "Constraints – Fig 2.3: Constraints by economic sector (p.18)",
    "ch16.png": "Constraints – Fig 2.4: Priorities for all firms (p.20)",
    "ch17.png": "Constraints – Fig 2.5: Priorities by firm size (p.21)",
    "ch18.png": "Constraints – Fig 2.6: Priorities by economic sector (p.22)",
    "ch19.png": "Constraints – Fig 2.7: Business community expectations (govt directions) (p.23)",
    "ch20.png": "Sub-Indices – Fig 3.1: Production & Sales by firm size – Performance (p.24)",
    "ch21.png": "Sub-Indices – Fig 3.2: Price & Production Cost Indices – Performance (p.25)",
    "ch22.png": "Sub-Indices – Fig 3.3: Investment & Employment Indices – Performance (p.25)",
    "ch23.png": "Sub-Indices – Fig 3.4: Production & Sales Indices by firm size – Outlook (p.26)",
    "ch24.png": "Sub-Indices – Fig 3.5: Price & Production Cost Indices – Outlook (p.27)",
    "ch25.png": "Sub-Indices – Fig 3.6: Investment & Employment Indices – Outlook (p.27)",
    "t1.png":   "Tables Index – Table A1: Past performance at sectoral level (p.28)",
    "t2.png":   "Tables Index – Table A2: Outlook at sectoral level (p.28)",
    "t3.png":   "Tables Appendix – Table A3: Past performance by firm size (p.29)",
    "t4.png":   "Tables Appendix – Table A4: Outlook by firm size (p.29)",
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
