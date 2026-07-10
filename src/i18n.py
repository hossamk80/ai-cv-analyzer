# =====================================================================
# BLOCK: TRANSLATIONS (src/i18n.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   Every sentence the user sees, in Arabic AND English. The visitor
#   picks the language from the sidebar.
#
#   TO CHANGE ANY TEXT: find its line below and edit the sentence.
#   TO ADD A LANGUAGE: copy the "en" block, rename it (e.g. "fr"),
#   translate the values, and add the name in LANGUAGES.
#
#   In the code, t("app_title") returns the sentence in the language
#   the visitor selected. Some sentences contain {placeholders} that
#   the code fills in automatically (e.g. {n} = number of CVs).
# =====================================================================

import streamlit as st

# Shown in the language picker  ->  internal code
LANGUAGES = {"العربية": "ar", "English": "en"}

TEXTS = {
    # ------------------------------ ARABIC ---------------------------
    "ar": {
        "app_title": "لوحة تحليل السير الذاتية الاحترافية",
        "language_label": "🌐 اللغة | Language",
        # Source of CV files
        "source_label": "📂 مصدر السير الذاتية",
        "source_folder": "مجلد المشروع (data)",
        "source_upload": "رفع ملفات من جهازي",
        "upload_label": "ارفع السير الذاتية هنا (PDF, Word, صور)",
        "upload_hint": "يمكنك سحب وإفلات عدة ملفات دفعة واحدة",
        "upload_empty": "⬆️ ارفع ملفات السير الذاتية من الشريط الجانبي لبدء التحليل",
        "subfolder_label": "📁 اختر المجلد الفرعي للمشروع",
        "root_folder": "(المجلد الرئيسي)",
        "path_missing": "❌ المسار المحدد غير موجود: {path}",
        "path_hint": "⚠️ أنشئ مجلد data وأضف ملفات السير الذاتية فيه ثم أعد تحميل الصفحة",
        # Job description
        "jd_header": "### 🎯 تخصيص متطلبات المطابقة والتوظيف",
        "jd_label": "📝 الصق الوصف الوظيفي للوظيفة الشاغرة هنا لضبط معايير التطابق آلياً:",
        "spinner": "جاري معالجة وتحليل مستندات السير الذاتية... يرجى الانتظار قليلاً",
        # Loading results
        "loaded_n": "✅ تم تحميل {n} سيرة ذاتية",
        "reanalyze": "🔄 إعادة تحليل الملفات من جديد",
        "no_cvs": "⚠️ لا توجد سير ذاتية صالحة أو مقروءة في المصدر المختار حالياً.",
        "no_cvs_hint": "💡 تأكد من وجود ملفات PDF أو DOCX في المصدر المختار",
        # Warnings about individual files
        "warn_unsupported": "تم تجاهل {file} — الصيغة {ext} غير مدعومة",
        "warn_error": "خطأ في معالجة {file}: {err}",
        "warn_empty": "لم يُستخرج أي نص من {file}",
        "warn_no_ocr": "محرك القراءة الضوئية (Tesseract) غير مثبت — الملفات الممسوحة ضوئياً والصور لن تُقرأ. ثبته ثم أعد تشغيل التطبيق.",
        # Matching criteria (typed by the recruiter)
        "crit_education": "🎓 المستوى التعليمي المطلوب",
        "crit_education_ph": "مثال: بكالوريوس علوم حاسب",
        "crit_certs": "📜 الشهادات المهنية المطلوبة",
        "crit_certs_ph": "مثال: CCNA, ITIL, PMP",
        "crit_skills": "🛠️ المهارات المطلوبة",
        "crit_skills_ph": "مثال: Networking, Windows Server, دعم فني",
        # Filters
        "filter_header": "🔍 تصفية وفلترة المرشحين",
        "city": "المدينة",
        "nationality": "الجنسية",
        "education_filter": "المستوى التعليمي",
        "certs_filter": "الشهادات المهنية",
        "skills_filter": "المهارات",
        "match_level_label": "مستوى التطابق",
        "min_exp": "أقل عدد سنوات خبرة عملية",
        "search": "بحث نصي حر شامل داخل البيانات",
        # Education levels (codes come from config.py)
        "phd": "دكتوراه",
        "master": "ماجستير",
        "bachelor": "بكالوريوس",
        "diploma": "دبلوم",
        "highschool": "ثانوية عامة",
        # Match levels
        "excellent": "ممتاز",
        "fair": "متوسط",
        "poor": "ضعيف",
        # Metrics + table
        "total_cvs": "إجمالي السير الذاتية المعالجة",
        "filtered_count": "عدد النتائج المطابقة للفلترة",
        "avg_score": "متوسط نسبة التطابق",
        "export_csv": "📥 تصدير قائمة المرشحين المفلترة كـ CSV",
        "no_results": "نعتذر! لا توجد نتائج مطابقة لخيارات الفلترة والتصفية الحالية.",
        # Contact section
        "contact_header": "📤 قنوات التواصل والربط مع المرشح",
        "choose_candidate": "اختر اسماً من القائمة لبدء الاتصال وتدقيق الملف الخاص به:",
        "message_label": "📩 نص الرسالة المخصصة (يمكنك تعديلها بحرية):",
        "subject_label": "📝 عنوان موضوع البريد الإلكتروني:",
        "default_subject": "فرصة وظيفية واعدة",
        "default_role": "الدعم الفني",
        "default_message": (
            "السلام عليكم ورحمة الله وبركاته {name},\n"
            "نأمل أن تكون بخير. لقد اطلعنا على سيرتك الذاتية الممتازة ونرى أن خبرتك "
            "في مجال {role} تتطابق مع احتياجاتنا.\n"
            "هل أنت متاح لإجراء مكالمة هاتفية قصيرة لمناقشة الفرص المتاحة هذا الأسبوع؟\n"
            "شاكرين ومقدرين لك."
        ),
        "whatsapp": "📱 أرسل عبر واتساب مباشرة",
        "email_btn": "📧 إرسال بريد إلكتروني رسمي",
        "linkedin": "🔗 فتح حساب المرشح في لينكدإن",
        # Analytics dashboard
        "analytics_header": "📊 لوحة التحليلات — نتائج الفلترة الحالية",
        "chart_levels": "توزيع مستويات التطابق",
        "chart_top_candidates": "أفضل 10 مرشحين حسب نسبة التطابق",
        "chart_skills": "أكثر 10 مهارات شيوعاً بين المرشحين",
        "chart_cities": "توزيع المرشحين حسب المدينة",
        "no_chart_data": "لا توجد بيانات كافية لهذا الرسم",
        # Per-candidate analysis
        "analysis_header": "🧾 الملخص التحليلي للمرشح: {name}",
        "analysis_rank": "الترتيب بين النتائج المفلترة",
        "analysis_score": "نسبة التطابق (مقارنة بالمتوسط)",
        "analysis_level": "مستوى التطابق",
        "analysis_this_candidate": "هذا المرشح",
        "analysis_pool_avg": "متوسط المرشحين",
        "analysis_pool_best": "أفضل مرشح",
        "analysis_matched": "متطلبات موجودة في سيرته",
        "analysis_missing": "متطلبات غير موجودة في سيرته",
        "analysis_none": "لا يوجد",
        "analysis_profile": "📋 ملف المرشح المستخرج آلياً:",
        "analysis_languages": "اللغات",
        # CV preview
        "preview_header": "📄 لوحة المعاينة الفورية لملف السيرة الذاتية",
        "file_missing": "الملف الأصلي لم يعد موجوداً على القرص.",
        "pdf_download": "📂 تحميل نسخة الـ PDF الحالية للملف",
        "pdf_text": "النصوص الكاملة المستخرجة من الـ PDF:",
        "pdf_error": "تعذر استخراج محتويات الـ PDF: {err}",
        "docx_content": "محتويات ملف الوورد:",
        "docx_error": "تعذر قراءة ملف الوورد: {err}",
        "txt_content": "محتويات الملف النصي:",
        "unsupported_preview": "نوع وصيغة هذا الملف غير مدعومة للعرض المباشر.",
    },
    # ------------------------------ ENGLISH --------------------------
    "en": {
        "app_title": "Professional CV Analysis Dashboard",
        "language_label": "🌐 اللغة | Language",
        "source_label": "📂 CV source",
        "source_folder": "Project folder (data)",
        "source_upload": "Upload files from my device",
        "upload_label": "Upload CVs here (PDF, Word, images)",
        "upload_hint": "You can drag & drop several files at once",
        "upload_empty": "⬆️ Upload CV files from the sidebar to start the analysis",
        "subfolder_label": "📁 Choose a project sub-folder",
        "root_folder": "(main folder)",
        "path_missing": "❌ The selected path does not exist: {path}",
        "path_hint": "⚠️ Create a data folder, add CV files to it, then reload the page",
        "jd_header": "### 🎯 Matching & hiring requirements",
        "jd_label": "📝 Paste the job description here to tune the matching automatically:",
        "spinner": "Analysing CV documents... please wait",
        "loaded_n": "✅ Loaded {n} CVs",
        "reanalyze": "🔄 Re-analyse the files",
        "no_cvs": "⚠️ No readable CVs were found in the selected source.",
        "no_cvs_hint": "💡 Make sure the selected source contains PDF or DOCX files",
        "warn_unsupported": "Skipped {file} — the {ext} format is not supported",
        "warn_error": "Error while processing {file}: {err}",
        "warn_empty": "No text could be extracted from {file}",
        "warn_no_ocr": "The OCR engine (Tesseract) is not installed — scanned files and images cannot be read. Install it and restart the app.",
        "crit_education": "🎓 Required education level",
        "crit_education_ph": "e.g. Bachelor of Computer Science",
        "crit_certs": "📜 Required professional certifications",
        "crit_certs_ph": "e.g. CCNA, ITIL, PMP",
        "crit_skills": "🛠️ Required skills",
        "crit_skills_ph": "e.g. Networking, Windows Server, technical support",
        "filter_header": "🔍 Filter candidates",
        "city": "City",
        "nationality": "Nationality",
        "education_filter": "Education level",
        "certs_filter": "Certifications",
        "skills_filter": "Skills",
        "match_level_label": "Match level",
        "min_exp": "Minimum years of experience",
        "search": "Free-text search across all data",
        "phd": "PhD",
        "master": "Master's",
        "bachelor": "Bachelor's",
        "diploma": "Diploma",
        "highschool": "High school",
        "excellent": "Excellent",
        "fair": "Fair",
        "poor": "Weak",
        "total_cvs": "Total CVs processed",
        "filtered_count": "Results matching the filters",
        "avg_score": "Average match score",
        "export_csv": "📥 Export the filtered candidate list as CSV",
        "no_results": "Sorry! No results match the current filters.",
        "contact_header": "📤 Contact channels for the candidate",
        "choose_candidate": "Pick a name from the list to contact them and review their file:",
        "message_label": "📩 Message text (edit it freely):",
        "subject_label": "📝 E-mail subject:",
        "default_subject": "A promising job opportunity",
        "default_role": "technical support",
        "default_message": (
            "Dear {name},\n"
            "We hope you are well. We reviewed your excellent CV and believe your "
            "experience in {role} matches our needs.\n"
            "Would you be available for a short phone call this week to discuss "
            "the opportunity?\n"
            "Kind regards."
        ),
        "whatsapp": "📱 Send via WhatsApp",
        "email_btn": "📧 Send a formal e-mail",
        "linkedin": "🔗 Open the candidate's LinkedIn",
        "analytics_header": "📊 Analytics — current filtered results",
        "chart_levels": "Match level distribution",
        "chart_top_candidates": "Top 10 candidates by match score",
        "chart_skills": "Top 10 skills across candidates",
        "chart_cities": "Candidates by city",
        "no_chart_data": "Not enough data for this chart",
        "analysis_header": "🧾 Analytical summary for: {name}",
        "analysis_rank": "Rank among filtered results",
        "analysis_score": "Match score (vs pool average)",
        "analysis_level": "Match level",
        "analysis_this_candidate": "This candidate",
        "analysis_pool_avg": "Pool average",
        "analysis_pool_best": "Best candidate",
        "analysis_matched": "Requirements found in their CV",
        "analysis_missing": "Requirements NOT found in their CV",
        "analysis_none": "None",
        "analysis_profile": "📋 Automatically extracted candidate profile:",
        "analysis_languages": "Languages",
        "preview_header": "📄 Instant CV file preview",
        "file_missing": "The original file no longer exists on disk.",
        "pdf_download": "📂 Download the current PDF file",
        "pdf_text": "Full text extracted from the PDF:",
        "pdf_error": "Could not extract the PDF contents: {err}",
        "docx_content": "Word file contents:",
        "docx_error": "Could not read the Word file: {err}",
        "txt_content": "Text file contents:",
        "unsupported_preview": "This file type is not supported for direct preview.",
    },
}


def t(key: str, **kwargs) -> str:
    """Return the sentence `key` in the language the visitor selected."""
    lang = st.session_state.get("lang", "ar")
    text = TEXTS.get(lang, TEXTS["ar"]).get(key) or TEXTS["ar"].get(key, key)
    return text.format(**kwargs) if kwargs else text


def current_lang() -> str:
    return st.session_state.get("lang", "ar")


def _set_lang(code: str) -> None:
    st.session_state["lang"] = code


def render_language_picker() -> None:
    """Draw two language BUTTONS at the top of the sidebar.

    The active language is highlighted; clicking the other one
    switches the whole page instantly.
    """
    lang = current_lang()
    col_ar, col_en = st.sidebar.columns(2)
    col_ar.button(
        "العربية",
        type="primary" if lang == "ar" else "secondary",
        use_container_width=True,
        on_click=_set_lang, args=("ar",),
    )
    col_en.button(
        "English",
        type="primary" if lang == "en" else "secondary",
        use_container_width=True,
        on_click=_set_lang, args=("en",),
    )


def apply_page_direction() -> None:
    """Flip the page right-to-left for Arabic, left-to-right for English."""
    if current_lang() == "ar":
        st.markdown(
            """
            <style>
            /* Right-to-left layout for Arabic */
            [data-testid="stAppViewContainer"] .main,
            [data-testid="stSidebarContent"],
            [data-testid="stMain"] {
                direction: rtl;
                text-align: right;
            }
            [data-testid="stSidebar"] { direction: rtl; }
            /* Keep code, links and numbers readable */
            pre, code { direction: ltr; text-align: left; }
            </style>
            """,
            unsafe_allow_html=True,
        )
