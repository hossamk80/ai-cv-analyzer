# =====================================================================
# BLOCK: CONFIGURATION (src/config.py)
# ---------------------------------------------------------------------
# WHAT THIS FILE IS:
#   Every "tunable" value of the system lives HERE and only here.
#   If you want to change a threshold, a default text, or a list of
#   job roles, edit this file — you never need to touch the logic files.
#
# HOW TO SEND THIS TO AN AI FOR CHANGES:
#   Copy this whole file. Say what you want changed (e.g. "add Kuwait
#   cities to KNOWN_LOCATIONS"). Paste the answer back over this file.
# =====================================================================

import os

# ---------------------------------------------------------------------
# 1. FILE & FOLDER SETTINGS
# ---------------------------------------------------------------------

# The ONLY folder the app is allowed to read CVs from by default.
# This protects the server: users of the web page cannot type a path
# like /etc or C:\Users and browse your machine.
DATA_ROOT = os.environ.get("CV_DATA_ROOT", "./data")

# Set the environment variable CV_ANALYZER_ALLOW_ANY_PATH=1 ONLY when
# you run the app on your own computer and want to point it at any
# folder (e.g. D:\CVS project). Never enable this on a public server.
ALLOW_ANY_PATH = os.environ.get("CV_ANALYZER_ALLOW_ANY_PATH", "0") == "1"

# File types the system knows how to read.
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".txt"}

# ---------------------------------------------------------------------
# 2. MATCH-SCORE SETTINGS
# ---------------------------------------------------------------------
# The raw score is a similarity percentage between the job description
# and the CV text (TF-IDF cosine similarity). Because a job description
# is short and a CV is long, raw scores are naturally small (often
# 1–10%), so the old fixed thresholds of 75/50 marked EVERY candidate
# as "weak". Candidates are therefore graded RELATIVE to the best
# match in the current batch:
RELATIVE_EXCELLENT = 0.70   # >= 70% of the best score -> "ممتاز"
RELATIVE_FAIR = 0.40        # >= 40% of the best score -> "متوسط"

# Legacy absolute thresholds (used only by the old one-file helper).
SCORE_EXCELLENT = 35.0
SCORE_FAIR = 15.0

LEVEL_EXCELLENT = "ممتاز"
LEVEL_FAIR = "متوسط"
LEVEL_POOR = "ضعيف"

# Words ignored during matching because they carry no meaning.
STOP_WORDS = [
    # English
    "the", "and", "of", "to", "in", "a", "an", "for", "with", "on",
    "at", "by", "or", "is", "are", "as", "from",
    # Arabic
    "في", "من", "على", "الى", "إلى", "عن", "مع", "او", "أو", "ثم",
    "ان", "أن", "هذا", "هذه", "ذلك", "التي", "الذي",
]

# ---------------------------------------------------------------------
# 3. EXTRACTION SETTINGS (what we look for inside a CV)
# ---------------------------------------------------------------------

# Cities / countries recognised by the location detector.
# Add more by appending to this list — no other change needed.
KNOWN_LOCATIONS = (
    r"(?i)(riyadh|jeddah|dammam|madinah|makkah|abha|tabuk|hail|jizan"
    r"|الرياض|جدة|الدمام|المدينة|مكة|خميس|ابها|أبها|تبوك|حائل|جازان"
    r"|saudi arabia|ksa|السعودية"
    r"|اليمن|اليمنية|دبي|أبو ظبي|الإمارات|الكويت|قطر|البحرين|عمان|مصر|الأردن)"
)

# Job titles the system recognises directly. Add your own titles here.
KNOWN_ROLES = [
    "Project Engineer", "IT Support", "Network Engineer", "Software Developer",
    "Database Administrator", "System Analyst", "Business Analyst",
    "Data Scientist", "Help Desk", "Technical Support", "Network Administrator",
    "System Engineer", "HR Specialist", "Accountant",
]

# Languages the system recognises in a CV.
KNOWN_LANGUAGES = (
    r"(?i)(arabic|english|french|urdu|spanish|german|hindi"
    r"|الإنجليزية|الانجليزية|العربية|الفرنسية|الأردية)"
)

# ---------------------------------------------------------------------
# 4. USER-INTERFACE DEFAULT TEXTS
# ---------------------------------------------------------------------

PAGE_TITLE = "لوحة تحليل السير الذاتية الاحترافية"

DEFAULT_JOB_DESCRIPTION = (
    "مأمور دعم فني | Technical support officer - "
    "خبرة في الشبكات والدعم الفني وصيانة الحواسب والأنظمة الفنية"
)

DEFAULT_EMAIL_SUBJECT = "فرصة وظيفية واعدة"

# {name} and {role} are filled in automatically for each candidate.
DEFAULT_CONTACT_MESSAGE = """السلام عليكم ورحمة الله وبركاته {name},
نأمل أن تكون بخير. لقد اطلعنا على سيرتك الذاتية الممتازة ونرى أن خبرتك في مجال {role} تتطابق مع احتياجاتنا.
هل أنت متاح لإجراء مكالمة هاتفية قصيرة لمناقشة الفرص المتاحة هذا الأسبوع؟
شاكرين ومقدرين لك."""
