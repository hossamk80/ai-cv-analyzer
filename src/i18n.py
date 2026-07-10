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
        # Filters
        "filter_header": "تصفية وفلترة المرشحين",
        "city": "اختر المدينة",
        "nationality": "اختر الجنسية",
        "match_level_label": "مستوى التطابق المستهدف",
        "min_exp": "أقل عدد سنوات خبرة عملية",
        "search": "🔍 بحث نصي حر شامل داخل البيانات",
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
        "filter_header": "Filter candidates",
        "city": "Choose a city",
        "nationality": "Choose a nationality",
        "match_level_label": "Target match level",
        "min_exp": "Minimum years of experience",
        "search": "🔍 Free-text search across all data",
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


def render_language_picker() -> None:
    """Draw the language selector at the top of the sidebar."""
    choice = st.sidebar.selectbox("🌐 اللغة | Language", list(LANGUAGES))
    st.session_state["lang"] = LANGUAGES[choice]
