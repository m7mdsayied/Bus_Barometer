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
    "title_exec_summary":                "✏️ [TITLE] Executive Summary section heading",
    "exec_subheading_line1":             "✏️ Sub-header line 1: Evaluating performance… (p.2, above box)",
    "exec_subheading_line2":             "✏️ Sub-header line 2: …the outlook based on… (p.2, above box)",
    "exec_box_label_size":               "✏️ Box label: According to size (p.2)",
    "exec_box_label_sector":             "✏️ Box label: Sectorally (p.2)",
    "exec_box_label_challenges":         "✏️ Box label: Challenges (p.2)",
    "exec_intro":                        "📄 Exec Summary – Opening paragraph (p.2)",
    "exec_box_overall":                  "📊 Exec Summary – Box: Overall BPI findings (p.2)",
    "exec_box_size":                     "📏 Exec Summary – Box: By firm size (p.2)",
    "exec_box_sector":                   "🏭 Exec Summary – Box: By sector (p.2)",
    "exec_box_challenges":               "⚠️ Exec Summary – Box: Challenges (p.2)",
    "exec_bpi_analysis":                 "📈 Exec Summary – BPI analysis paragraph (p.2, beside chart)",
    "exec_expectations":                 "🔮 Exec Summary – Expectations paragraph (p.2, bottom)",
    "exec_heading_size":                 "✏️ Section heading: According to size (p.3)",
    "exec_size_detail":                  "📏 Exec Summary – Size analysis text (p.3, left column)",
    "exec_heading_sector":               "✏️ Section heading: Sectorally (p.3)",
    "exec_sector_summary":               "🏭 Exec Summary – Sectorally intro text (p.3)",
    "exec_manufacturing":                "🔧 Exec Summary – Manufacturing sector text (p.3)",
    "exec_best_sector":                  "🌟 Exec Summary – Best sector text (p.3)",
    "exec_heading_challenges":           "✏️ Section heading: Challenges and priorities (p.4)",
    "exec_challenges_headline":          "⚠️ Exec Summary – Challenges bold headline (p.4)",
    "exec_challenges_body":              "📋 Exec Summary – Challenges body (p.4, ranked list)",
    "exec_sme_comparison":               "🏢 Exec Summary – SME vs large firms challenges (p.4)",
    "exec_priorities":                   "🎯 Exec Summary – Business priorities paragraph (p.4)",
    "exec_heading_macro":                "✏️ Section heading: Main Macroeconomic Developments (p.4)",
    "exec_macro_global_label":           "✏️ Bullet label: Globally (p.4)",
    "exec_macro_global":                 "🌍 Exec Summary – Macro: Global bullet (p.4)",
    "exec_macro_local_label":            "✏️ Bullet label: Locally (p.4)",
    "exec_macro_local":                  "🇪🇬 Exec Summary – Macro: Local bullet (p.4)",
    "exec_footnote_macro":               "📌 Footnote: Macro report reference (p.4)",
    # ── Executive Summary (AR) ─────────────────────────────────────────
    "title_exec_summary_ar":             "✏️ [عنوان] الملخص التنفيذي — عنوان القسم (ص.2)",
    "exec_subheading_overall_eval_ar":   "✏️ ترويسة — تقييم الأداء والتوقعات (ص.2، فوق الصندوق)",
    "exec_box_label_size_ar":            "✏️ تسمية صندوق — وفقاً للحجم (ص.2)",
    "exec_box_label_sector_ar":          "✏️ تسمية صندوق — وفقاً للقطاع (ص.2)",
    "exec_box_label_challenges_ar":      "✏️ تسمية صندوق — التحديات (ص.2)",
    "exec_intro_ar":                     "📄 الملخص التنفيذي — الفقرة التمهيدية (ص.2)",
    "exec_box_overall_ar":               "📊 الملخص التنفيذي — صندوق: النتائج الإجمالية (ص.2)",
    "exec_box_size_ar":                  "📏 الملخص التنفيذي — صندوق: حسب حجم الشركات (ص.2)",
    "exec_box_sector_ar":                "🏭 الملخص التنفيذي — صندوق: حسب القطاع (ص.2)",
    "exec_box_challenges_ar":            "⚠️ الملخص التنفيذي — صندوق: التحديات (ص.2)",
    "exec_bpi_analysis_ar":              "📈 الملخص التنفيذي — تحليل مؤشر الأداء (ص.2)",
    "exec_expectations_ar":              "🔮 الملخص التنفيذي — فقرة التوقعات (ص.2)",
    "exec_heading_size_ar":              "✏️ عنوان فرعي — وفقاً للحجم (ص.3)",
    "exec_size_detail_ar":               "📏 الملخص التنفيذي — تفاصيل الأداء حسب الحجم (ص.3)",
    "exec_heading_sector_ar":            "✏️ عنوان فرعي — وفقاً للقطاع (ص.3)",
    "exec_sector_summary_ar":            "🏭 الملخص التنفيذي — ملخص القطاعات (ص.3)",
    "exec_manufacturing_ar":             "🔧 الملخص التنفيذي — قطاع الصناعات التحويلية (ص.3)",
    "exec_best_sector_ar":               "🌟 الملخص التنفيذي — القطاع صاحب أفضل أداء (ص.3)",
    "exec_heading_challenges_ar":        "✏️ عنوان فرعي — التحديات والأولويات (ص.4)",
    "exec_challenges_headline_ar":       "⚠️ الملخص التنفيذي — عنوان التحديات البارز (ص.4)",
    "exec_challenges_body_ar":           "📋 الملخص التنفيذي — تفاصيل التحديات المرتبة (ص.4)",
    "exec_sme_comparison_ar":            "🏢 الملخص التنفيذي — مقارنة الشركات الكبيرة والصغيرة (ص.4)",
    "exec_priorities_ar":                "🎯 الملخص التنفيذي — الأولويات (ص.4)",
    "exec_priorities_label_ar":          "✏️ تسمية صندوق — أهم الأولويات (ص.4، داخل الصندوق)",
    "exec_heading_macro_ar":             "✏️ عنوان فرعي — أهم التطورات الاقتصادية (ص.4)",
    "exec_macro_global_label_ar":        "✏️ تسمية نقطة — عالمياً (ص.4)",
    "exec_macro_global_ar":              "🌍 الملخص التنفيذي — نقطة: عالمياً (ص.4)",
    "exec_macro_local_label_ar":         "✏️ تسمية نقطة — محلياً (ص.4)",
    "exec_macro_local_ar":               "🇪🇬 الملخص التنفيذي — نقطة: محلياً (ص.4)",
    # ── Macro Overview (EN) ───────────────────────────────────────────
    "title_macro_overview":              "✏️ [TITLE] Macroeconomic Overview section heading",
    "macro_global_intro":                "🌍 Macro Overview – Global bold headline (p.8)",
    "macro_global_p1":                   "📉 Macro Overview – Global growth paragraph 1 (p.8)",
    "macro_global_p2":                   "💹 Macro Overview – Global inflation paragraph (p.8)",
    "macro_global_p3":                   "📊 Macro Overview – PMI/Composite paragraph (p.8)",
    "macro_label_local":                 "✏️ Inline label: Locally (p.8)",
    "macro_local_p1":                    "🇪🇬 Macro Overview – Local headline paragraph (p.8)",
    "macro_local_p2":                    "🏦 Macro Overview – IMF/WB review paragraph (p.8)",
    "macro_local_p3":                    "📋 Macro Overview – Structural reforms paragraph (p.8)",
    "macro_footnotes_pg8":               "📌 Macro Overview – Page 8 footnotes",
    "macro_indicators_intro":            "📋 Macro Overview – Indicators intro sentence (p.9)",
    "macro_heading_gdp":                 "✏️ Section heading: I. GDP Growth (p.9)",
    "macro_gdp_growth":                  "📈 Macro Overview – GDP bullet (p.9, under Figure 1)",
    "macro_chart1_caption":              "🖼️ Figure 1 caption: Real GDP Growth (p.9)",
    "macro_chart1_source":               "📌 Figure 1 source (p.9)",
    "macro_footnotes_pg9":               "📌 Macro Overview – Page 9 footnotes",
    "macro_heading_inflation":           "✏️ Section heading: II. Inflation (p.9)",
    "macro_inflation_p1":                "💰 Macro Overview – Inflation bullet (p.9)",
    "macro_inflation_p2":                "💰 Macro Overview – CBE rate paragraph (p.9)",
    "macro_chart2_caption":              "🖼️ Figure 2 caption: Inflation and Interest Rates (p.10)",
    "macro_chart2_source":               "📌 Figure 2 source (p.10)",
    "macro_footnotes_pg10":              "📌 Macro Overview – Page 10 footnotes",
    "macro_heading_foreign":             "✏️ Section heading: III. Foreign transactions (p.10)",
    "macro_label_bop":                   "✏️ Inline label: Balance of payments (p.10)",
    "macro_bop_p1":                      "💱 Macro Overview – BOP paragraph 1 (p.10)",
    "macro_bop_p2":                      "📊 Macro Overview – Current account paragraph (p.10)",
    "macro_bop_p3":                      "📊 Macro Overview – BOP additional paragraph (p.10)",
    "macro_label_nfa":                   "✏️ Inline label: Net foreign assets (p.10)",
    "macro_nfa_p1":                      "🏦 Macro Overview – Net foreign assets paragraph (p.10)",
    "macro_label_reserves":              "✏️ Inline label: Net international reserves (p.10)",
    "macro_reserves_p1":                 "💵 Macro Overview – International reserves paragraph (p.10)",
    "macro_exchange_rate_p1":            "💱 Macro Overview – Exchange rate paragraph (p.11)",
    "macro_chart3_caption":              "🖼️ Figure 3 caption: Net Int'l Reserves & Exchange Rate (p.11)",
    "macro_chart3_source":               "📌 Figure 3 source (p.11)",
    "macro_heading_finance":             "✏️ Section heading: IV. Public Finance (p.11)",
    "macro_footnotes_pg11":              "📌 Macro Overview – Page 11 footnotes",
    "macro_public_finance_intro":        "🏛️ Macro Overview – Budget deficit intro (p.11)",
    "macro_public_finance_b1":           "🏛️ Macro Overview – Budget bullet 1 (p.11)",
    "macro_public_finance_b2":           "🏛️ Macro Overview – Budget bullet 2 (p.11)",
    "macro_public_finance_b3":           "🏛️ Macro Overview – Budget bullet 3 (p.11)",
    # ── Macro Overview (AR) ───────────────────────────────────────────
    "title_macro_overview_ar":           "✏️ [عنوان] نظرة عامة على الاقتصاد الكلي (ص.8)",
    "macro_global_intro_ar":             "🌍 الاقتصاد الكلي — العنوان الرئيسي للمحور العالمي (ص.8)",
    "macro_global_p1_ar":                "📉 الاقتصاد الكلي — فقرة النمو العالمي (ص.8)",
    "macro_global_p2_ar":                "💹 الاقتصاد الكلي — فقرة التضخم العالمي (ص.8)",
    "macro_global_p3_ar":                "📊 الاقتصاد الكلي — فقرة مؤشر PMI (ص.8)",
    "macro_local_p1_ar":                 "🇪🇬 الاقتصاد الكلي — عنوان المحور المحلي (ص.8)",
    "macro_local_p2_ar":                 "🏦 الاقتصاد الكلي — مراجعة صندوق النقد/البنك الدولي (ص.8)",
    "macro_local_p3_ar":                 "📋 الاقتصاد الكلي — الإصلاحات الهيكلية (ص.8)",
    "macro_footnotes_pg8_ar":            "📌 هامش ص.8 — مراجع الاقتصاد الكلي",
    "macro_indicators_intro_ar":         "📋 الاقتصاد الكلي — جملة تمهيدية لمؤشرات الاقتصاد الكلي (ص.9)",
    "macro_heading_gdp_ar":              "✏️ عنوان — أولاً: معدل نمو الناتج المحلي الإجمالي (ص.9)",
    "macro_gdp_growth_ar":               "📈 الاقتصاد الكلي — معدل نمو الناتج المحلي (ص.9)",
    "macro_chart1_caption_ar":           "🖼️ عنوان الشكل 1 — النمو في الناتج المحلي (ص.9)",
    "macro_chart1_source_ar":            "📌 مصدر الشكل 1 (ص.9)",
    "macro_footnotes_pg9_ar":            "📌 هامش ص.9 — مراجع البيانات",
    "macro_heading_inflation_ar":        "✏️ عنوان — ثانياً: معدل التضخم (ص.9)",
    "macro_inflation_p1_ar":             "💰 الاقتصاد الكلي — معدل التضخم (ص.9)",
    "macro_inflation_p2_ar":             "💰 الاقتصاد الكلي — قرار لجنة السياسة النقدية (ص.9)",
    "macro_chart2_caption_ar":           "🖼️ عنوان الشكل 2 — التضخم وأسعار الفائدة (ص.10)",
    "macro_chart2_source_ar":            "📌 مصدر الشكل 2 (ص.10)",
    "macro_footnotes_pg10_ar":           "📌 هامش ص.10 — مراجع البيانات",
    "macro_heading_foreign_ar":          "✏️ عنوان — ثالثاً: المعاملات الخارجية (ص.10)",
    "macro_label_bop_ar":                "✏️ تسمية — ميزان المدفوعات (ص.10)",
    "macro_bop_p1_ar":                   "💱 الاقتصاد الكلي — ميزان المدفوعات (ص.10)",
    "macro_bop_p2_ar":                   "📊 الاقتصاد الكلي — الحساب الجاري (ص.10)",
    "macro_bop_p3_ar":                   "📊 الاقتصاد الكلي — بيانات إضافية لميزان المدفوعات (ص.10)",
    "macro_label_nfa_ar":                "✏️ تسمية — صافي الأصول الأجنبية (ص.10)",
    "macro_nfa_p1_ar":                   "🏦 الاقتصاد الكلي — صافي الأصول الأجنبية (ص.10)",
    "macro_label_reserves_ar":           "✏️ تسمية — صافي الاحتياطيات الدولية (ص.10)",
    "macro_reserves_p1_ar":              "💵 الاقتصاد الكلي — الاحتياطيات الدولية (ص.10)",
    "macro_exchange_rate_p1_ar":         "💱 الاقتصاد الكلي — سعر الصرف (ص.10)",
    "macro_chart3_caption_ar":           "🖼️ عنوان الشكل 3 — الاحتياطيات وسعر الصرف (ص.11)",
    "macro_chart3_source_ar":            "📌 مصدر الشكل 3 (ص.11)",
    "macro_heading_finance_ar":          "✏️ عنوان — رابعاً: المالية العامة (ص.11)",
    "macro_public_finance_intro_ar":     "🏛️ الاقتصاد الكلي — عجز الموازنة العامة (ص.11)",
    "macro_public_finance_b1_ar":        "🏛️ الاقتصاد الكلي — الإيرادات العامة (ص.11)",
    "macro_public_finance_b2_ar":        "🏛️ الاقتصاد الكلي — المصروفات العامة (ص.11)",
    "macro_public_finance_b3_ar":        "🏛️ الاقتصاد الكلي — نسبة الدين للناتج (ص.11)",
    "macro_footnotes_pg11_ar":           "📌 هامش ص.11 — مراجع المالية العامة",
    # ── Overall Index (EN) ────────────────────────────────────────────
    "title_bbi":                         "✏️ [TITLE] Business Barometer Index (BBI) heading",
    "title_section_i":                   "✏️ [TITLE] Section I heading (Overall Index)",
    "title_subsection_11":               "✏️ [TITLE] 1-1 Overall index sub-heading (p.12)",
    "title_subsection_12":               "✏️ [TITLE] 1-2 Index by firm size sub-heading (p.13)",
    "title_subsection_13":               "✏️ [TITLE] 1-3 Index by economic sectors sub-heading (p.13)",
    "overall_intro":                     "📊 Overall Index – Bold sub-headline (p.12)",
    "overall_bpi_text":                  "📈 Overall Index – BPI analysis text, 1-1 Overall index (p.12)",
    "overall_expectations":              "🔮 Overall Index – Expectations analysis text (p.12)",
    "overall_footnotes_pg12":            "📌 Overall Index – Page 12 source/footnotes",
    "overall_size_perf":                 "📏 Overall Index – 1-2 Size performance text (p.13)",
    "overall_size_exp":                  "🔮 Overall Index – 1-2 Size expectations text (p.13)",
    "overall_sector_intro":              "🏭 Overall Index – 1-3 Sector intro text (p.13)",
    "overall_sector_perf_intro":         "📋 Overall Index – Sector analysis standard intro sentence (p.14)",
    "overall_perf_manufacturing":        "🔧 Overall Index – Manufacturing bullet (p.14)",
    "overall_perf_construction":         "🏗️ Overall Index – Construction bullet (p.14)",
    "overall_perf_tourism":              "✈️ Overall Index – Tourism bullet (p.14)",
    "overall_perf_transport":            "🚚 Overall Index – Transport bullet (p.14)",
    "overall_perf_telecom":              "📡 Overall Index – Telecom bullet (p.14)",
    "overall_perf_financial":            "🏦 Overall Index – Financial services bullet (p.14)",
    "overall_sector_exp_intro":          "🔮 Overall Index – Outlook intro sentence (p.14)",
    "overall_exp_manufacturing":         "🔧 Overall Index – Manufacturing outlook bullet (p.14–15)",
    "overall_exp_construction":          "🏗️ Overall Index – Construction outlook bullet (p.15)",
    "overall_exp_tourism":               "✈️ Overall Index – Tourism outlook bullet (p.15)",
    "overall_exp_transport":             "🚚 Overall Index – Transport outlook bullet (p.15)",
    "overall_exp_telecom":               "📡 Overall Index – Telecom outlook bullet (p.15)",
    "overall_exp_financial":             "🏦 Overall Index – Financial services outlook bullet (p.15)",
    "overall_source_pg15":               "📌 Overall Index – Page 15 source",
    # ── Overall Index (AR) ────────────────────────────────────────────
    "title_bbi_ar":                      "✏️ [عنوان] مؤشر بارومتر الأعمال (ص.12)",
    "title_section_i_ar":                "✏️ [عنوان] أولاً: تقييم الأداء والتوقعات (ص.12)",
    "title_subsection_11_ar":            "✏️ [عنوان] 1-1 تطور المؤشر الإجمالي (ص.12)",
    "title_subsection_12_ar":            "✏️ [عنوان] 1-2 المؤشر وفقاً لأحجام الشركات (ص.13)",
    "title_subsection_13_ar":            "✏️ [عنوان] 1-3 المؤشر وفقاً للقطاعات (ص.14)",
    "overall_intro_ar":                  "📊 المؤشر الإجمالي — العنوان الفرعي البارز (ص.12)",
    "overall_bpi_text_ar":               "📈 المؤشر الإجمالي — تحليل مؤشر الأداء 1-1 (ص.12)",
    "overall_expectations_ar":           "🔮 المؤشر الإجمالي — تحليل التوقعات (ص.12)",
    "overall_footnotes_pg12_ar":         "📌 المؤشر الإجمالي — هامش ص.12 (مصدر وملاحظات)",
    "overall_size_perf_ar":              "📏 المؤشر الإجمالي — أداء 1-2 حسب الحجم (ص.13)",
    "overall_size_exp_ar":               "🔮 المؤشر الإجمالي — توقعات 1-2 حسب الحجم (ص.13)",
    "overall_sector_intro_ar":           "🏭 المؤشر الإجمالي — مقدمة 1-3 القطاعات (ص.13)",
    "overall_sector_perf_intro_ar":      "📋 المؤشر الإجمالي — جملة تمهيدية لتحليل القطاعات (ص.14)",
    "overall_perf_manufacturing_ar":     "🔧 المؤشر الإجمالي — الصناعات التحويلية (ص.14)",
    "overall_perf_construction_ar":      "🏗️ المؤشر الإجمالي — التشييد والبناء (ص.14)",
    "overall_perf_tourism_ar":           "✈️ المؤشر الإجمالي — السياحة (ص.14)",
    "overall_perf_transport_ar":         "🚚 المؤشر الإجمالي — النقل (ص.14)",
    "overall_perf_telecom_ar":           "📡 المؤشر الإجمالي — الاتصالات (ص.14)",
    "overall_perf_financial_ar":         "🏦 المؤشر الإجمالي — الخدمات المالية (ص.14)",
    "overall_sector_exp_intro_ar":       "🔮 المؤشر الإجمالي — مقدمة التوقعات القطاعية (ص.14)",
    "overall_exp_manufacturing_ar":      "🔧 المؤشر الإجمالي — توقعات الصناعات التحويلية (ص.14-15)",
    "overall_exp_construction_ar":       "🏗️ المؤشر الإجمالي — توقعات التشييد والبناء (ص.15)",
    "overall_exp_tourism_ar":            "✈️ المؤشر الإجمالي — توقعات السياحة (ص.15)",
    "overall_exp_transport_ar":          "🚚 المؤشر الإجمالي — توقعات النقل (ص.15)",
    "overall_exp_telecom_ar":            "📡 المؤشر الإجمالي — توقعات الاتصالات (ص.15)",
    "overall_exp_financial_ar":          "🏦 المؤشر الإجمالي — توقعات الخدمات المالية (ص.15)",
    "overall_source_pg15_ar":            "📌 المؤشر الإجمالي — مصدر ص.15",
    # ── Constraints & Priorities (EN) ────────────────────────────────
    "title_section_ii":                  "✏️ [TITLE] Section II heading (Constraints & Priorities)",
    "title_constraints_21":              "✏️ [TITLE] Sub-heading 2-1 (Constraints faced)",
    "title_constraints_211":             "✏️ [TITLE] Sub-heading 2-1-1 (By firm size)",
    "title_constraints_212":             "✏️ [TITLE] Sub-heading 2-1-2 (By sector)",
    "title_priorities_22":               "✏️ [TITLE] Sub-heading 2-2 (Priorities)",
    "title_priorities_221":              "✏️ [TITLE] Sub-heading 2-2-1 (Priorities by size)",
    "title_priorities_222":              "✏️ [TITLE] Sub-heading 2-2-2 (Priorities by sector)",
    "title_outlook_community":           "✏️ [TITLE] Business community expectations heading",
    "constraints_intro":                 "⚠️ Constraints – 2-1 Bold headline (p.16)",
    "constraints_main_text_p1":          "📋 Constraints – Intro sentence referencing Fig.2-1 (p.16)",
    "constraints_main_text_p2":          "📋 Constraints – Top 5 constraints body text (p.16)",
    "constraints_main_text_p3":          "📋 Constraints – Additional constraints body text (p.16)",
    "constraints_source_pg17":           "📌 Constraints – Page 17 figure source note",
    "constraints_by_size_p1":            "📏 Constraints – 2-1-1 Size intro sentence (p.17)",
    "constraints_by_size_p2":            "📊 Constraints – Large firms constraint ranking (p.17)",
    "constraints_by_size_p3":            "📊 Constraints – SME constraint ranking (p.17)",
    "constraints_by_size_p4":            "📊 Constraints – Figure 2-2 reference sentence (p.17)",
    "constraints_by_sector":             "🏭 Constraints – 2-1-2 Sector constraints text (p.18)",
    "priorities_headline":               "🎯 Priorities – 2-2 Bold headline (p.20)",
    "priorities_all_firms":              "📋 Priorities – All firms body text (p.20)",
    "priorities_large_firms":            "📏 Priorities – Large vs SME differences text (p.20)",
    "priorities_by_size_intro":          "📏 Priorities – 2-2-1 'Comparing priorities...' bold text (p.21)",
    "priorities_by_size":                "📏 Priorities – 2-2-1 Size priorities body text (p.21)",
    "priorities_by_sector_text":         "🏭 Priorities – 2-2-2 Sector priorities body text (p.22)",
    "outlook_community":                 "🔮 Constraints – Business expectations intro text (p.23)",
    # ── Constraints & Priorities (AR) ────────────────────────────────
    "title_section_ii_ar":               "✏️ [عنوان] ثانياً: المعوقات والأولويات (ص.16)",
    "title_constraints_12_ar":           "✏️ [عنوان] 1-2 المعوقات خلال الربع (ص.16)",
    "title_constraints_112_ar":          "✏️ [عنوان] 1-1-2 المعوقات حسب حجم الشركات (ص.17)",
    "title_constraints_212_ar":          "✏️ [عنوان] 2-1-2 المعوقات حسب القطاعات (ص.18)",
    "title_priorities_22_ar":            "✏️ [عنوان] 2-2 أولويات تحسين مناخ الأعمال (ص.19)",
    "title_priorities_122_ar":           "✏️ [عنوان] 1-2-2 الأولويات حسب أحجام الشركات (ص.20)",
    "title_priorities_222_ar":           "✏️ [عنوان] 2-2-2 الأولويات حسب القطاعات (ص.21)",
    "title_outlook_community_ar":        "✏️ [عنوان] توقعات مجتمع الأعمال (ص.22)",
    "constraints_intro_ar":              "⚠️ المعوقات — العنوان الرئيسي البارز (ص.16)",
    "constraints_main_text_p1_ar":       "📋 المعوقات — جملة تمهيدية مع الشكل 1-2 (ص.16)",
    "constraints_main_text_p2_ar":       "📋 المعوقات — تفاصيل المعوقات الأولى والثانية والثالثة (ص.16)",
    "constraints_main_text_p3_ar":       "📋 المعوقات — تفاصيل المعوقات الرابعة والخامسة (ص.16)",
    "constraints_by_size_p1_ar":         "📏 المعوقات — مقدمة حجم الشركات (ص.17)",
    "constraints_by_size_p2_ar":         "📊 المعوقات — ترتيب الشركات الكبيرة (ص.17)",
    "constraints_by_size_p3_ar":         "📊 المعوقات — ترتيب الشركات الصغيرة والمتوسطة (ص.17)",
    "constraints_by_size_p4_ar":         "📊 المعوقات — إحالة للشكل 1-3 (ص.17)",
    "constraints_by_sector_ar":          "🏭 المعوقات — 2-1-2 المعوقات حسب القطاع (ص.18)",
    "priorities_intro_ar":               "🎯 الأولويات — العنوان البارز 2-2 (ص.19)",
    "priorities_main_text_ar":           "📋 الأولويات — تفاصيل الأولويات (ص.19)",
    "priorities_headline_ar":            "🎯 الأولويات — العنوان الرئيسي البارز (ص.20)",
    "priorities_all_firms_ar":           "📋 الأولويات — كافة الشركات (ص.20)",
    "priorities_large_firms_ar":         "📏 الأولويات — الشركات الكبيرة مقابل الصغيرة (ص.20)",
    "priorities_size_intro_ar":          "📏 الأولويات — مقدمة 1-2-2 (ص.21)",
    "priorities_by_size_p1_ar":          "📏 الأولويات — 1-2-2 نص الأولويات ج.1 (ص.21)",
    "priorities_by_size_p2_ar":          "📏 الأولويات — 1-2-2 نص الأولويات ج.2 (ص.21)",
    "priorities_by_sector_ar":           "🏭 الأولويات — 2-2-2 الأولويات حسب القطاع (ص.22)",
    "constraints_outlook_ar":            "🔮 المعوقات — توقعات مجتمع الأعمال (ص.23)",
    "constraints_outlook_source_pg22_ar":"📌 مصدر ص.22 — نتائج الاستبيان",
    # ── Sub-Indices (EN) ─────────────────────────────────────────────
    "title_section_iii":                 "✏️ [TITLE] Section III heading (Sub-Indices)",
    "title_subindices_31":               "✏️ [TITLE] Sub-heading 3.1 (Performance evaluation)",
    "title_subindices_32":               "✏️ [TITLE] Sub-heading 3.2 (Performance expectations)",
    "title_subindices_prices_exp":       "✏️ [TITLE] Prices/Wages expectations heading",
    "title_subindices_inv_exp":          "✏️ [TITLE] Investment/Employment expectations headline",
    "subindices_perf_p1":                "📊 Sub-Indices – 3.1 Large firms production/sales analysis (p.24)",
    "subindices_perf_p2":                "📊 Sub-Indices – 3.1 SME performance analysis (p.24)",
    "subindices_source_pg24":            "📌 Sub-Indices – Page 24 source note",
    "subindices_prices_wages_intro":     "💰 Sub-Indices – Prices/wages bold headline (p.25)",
    "subindices_prices_wages_p1":        "💰 Sub-Indices – Prices/wages analysis text (p.25)",
    "subindices_source_pg25_1":          "📌 Sub-Indices – Page 25 source note 1",
    "subindices_inv_emp_intro":          "📈 Sub-Indices – Investment/employment bold headline (p.25)",
    "subindices_inv_emp_large":          "📈 Sub-Indices – Large firms investment/employment bullet (p.25)",
    "subindices_inv_emp_sme":            "📈 Sub-Indices – SME investment/employment bullet (p.25)",
    "subindices_exp_intro":              "🔮 Sub-Indices – 3.2 Expectations bold headline (p.26)",
    "subindices_exp_large":              "🏭 Sub-Indices – 3.2 Large firms expectations text (p.26)",
    "subindices_exp_sme":                "🏭 Sub-Indices – 3.2 SME expectations text (p.26)",
    "subindices_price_wage_exp_headline":"💰 Sub-Indices – Prices/wages expectations bold headline (p.27)",
    "subindices_price_wage_exp_p1":      "💰 Sub-Indices – Prices/wages expectations text (p.27)",
    "subindices_price_wage_exp_p2":      "💰 Sub-Indices – SME prices/wages expectations text (p.27)",
    "subindices_inv_emp_exp_body":       "📈 Sub-Indices – Investment/employment expectations text (p.27)",
    # ── Sub-Indices (AR) ─────────────────────────────────────────────
    "title_section_iii_ar":              "✏️ [عنوان] ثالثاً: الأداء والتوقعات وفقاً للمؤشرات الفرعية (ص.23)",
    "title_subindices_31_ar":            "✏️ [عنوان] 3.1 تقييم الأداء (ص.23)",
    "title_subindices_32_ar":            "✏️ [عنوان] 3.2 توقعات الأداء (ص.25)",
    "subindices_perf_p1_ar":             "📊 المؤشرات الفرعية — 3.1 أداء الشركات الكبيرة (ص.23)",
    "subindices_perf_p2_ar":             "📊 المؤشرات الفرعية — 3.1 أداء الشركات الصغيرة والمتوسطة (ص.23)",
    "subindices_source_pg23_ar":         "📌 المؤشرات الفرعية — مصدر ص.23",
    "subindices_prices_wages_intro_ar":  "💰 المؤشرات الفرعية — عنوان الأسعار والأجور (ص.24)",
    "subindices_prices_wages_p1_ar":     "💰 المؤشرات الفرعية — تحليل الأسعار والأجور (ص.24)",
    "subindices_source_pg24_1_ar":       "📌 المؤشرات الفرعية — مصدر ص.24 (الأسعار والأجور)",
    "subindices_inv_emp_intro_ar":       "📈 المؤشرات الفرعية — عنوان الاستثمار والتوظيف (ص.24)",
    "subindices_inv_emp_large_ar":       "📈 المؤشرات الفرعية — الشركات الكبيرة: الاستثمار والتوظيف (ص.24)",
    "subindices_inv_emp_sme_ar":         "📈 المؤشرات الفرعية — الشركات الصغيرة والمتوسطة: الاستثمار والتوظيف (ص.24)",
    "subindices_source_pg24_2_ar":       "📌 المؤشرات الفرعية — مصدر ص.24 (الاستثمار والتوظيف)",
    "subindices_exp_intro_ar":           "🔮 المؤشرات الفرعية — عنوان توقعات 3.2 (ص.25)",
    "subindices_exp_large_ar":           "🏭 المؤشرات الفرعية — توقعات الشركات الكبيرة (ص.25)",
    "subindices_exp_sme_ar":             "🏭 المؤشرات الفرعية — توقعات الشركات الصغيرة والمتوسطة (ص.25)",
    "subindices_source_pg25_ar":         "📌 المؤشرات الفرعية — مصدر ص.25",
    "subindices_exp_prices_wages_intro_ar": "💰 المؤشرات الفرعية — عنوان توقعات الأسعار والأجور (ص.26)",
    "subindices_exp_prices_p1_ar":       "💰 المؤشرات الفرعية — توقعات الأسعار والأجور (ص.26)",
    "subindices_exp_wages_sme_ar":       "💰 المؤشرات الفرعية — توقعات الأجور - الشركات الصغيرة والمتوسطة (ص.26)",
    "subindices_source_pg26_1_ar":       "📌 المؤشرات الفرعية — مصدر ص.26 (الأسعار)",
    "subindices_exp_inv_emp_intro_ar":   "📈 المؤشرات الفرعية — عنوان توقعات الاستثمار والتوظيف (ص.27)",
    "subindices_exp_inv_emp_p1_ar":      "📈 المؤشرات الفرعية — توقعات الاستثمار والتوظيف (ص.27)",
    "subindices_source_pg26_2_ar":       "📌 المؤشرات الفرعية — مصدر ص.26 (الاستثمار والتوظيف)",
    # ── Tables (EN) ───────────────────────────────────────────────────
    "title_tables_index":                "✏️ [TITLE] Tables Index section heading (p.28)",
    "title_tables_appendix":             "✏️ [TITLE] Tables Appendix section heading (p.29)",
    # ── Tables (AR) ───────────────────────────────────────────────────
    "title_tables_index_ar":             "✏️ [عنوان] ملحق الجداول (ص.27)",
    "title_tables_appendix_ar":          "✏️ [عنوان] ملحق الجداول (ص.28)",
    "title_table3_ar":                   "✏️ [عنوان] عنوان الجدول رقم 3 (ص.28)",
    "title_table4_ar":                   "✏️ [عنوان] عنوان الجدول رقم 4 (ص.28)",
    "tables_footnotes_pg27_ar":          "📌 هوامش ص.27 — ملاحظات الجداول",
    "tables_footnotes_pg28_ar":          "📌 هوامش ص.28 — ملاحظات الجداول",
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
