import re
import os
import logging
from datetime import datetime
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# إعداد تتبع الأخطاء بشكل احترافي
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))

def calculate_match_score(text, job_description):
    """حساب نسبة التطابق بناءً على الوصف الوظيفي الممرر ديناميكياً"""
    if not job_description or not job_description.strip():
        return 0.0
    docs = [job_description.lower(), text.lower()]
    tfidf = vectorizer.fit_transform(docs)
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(score * 100, 2)

def classify_match(score):
    if score >= 75:
        return "ممتاز"
    elif score >= 50:
        return "متوسط"
    else:
        return "ضعيف"

def clean_text(text):
    text = re.sub(r'[^\w\s@.\-+:/]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            with open(path, "rb") as f:
                return "\n".join(page.extract_text() or "" for page in PdfReader(f).pages)
        elif ext == ".docx":
            doc = docx.Document(path)
            return "\n".join(para.text for para in doc.paragraphs)
        elif ext in [".png", ".jpg", ".jpeg"]:
            return pytesseract.image_to_string(Image.open(path), lang='eng+ara')
        elif ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        logging.error(f"فشلت قراءة الملف {path}. السبب: {str(e)}")
        return ""
    return ""

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r"(?:\+966|00966|966|0)?5\d{8}", text.replace(" ", ""))
    return "+966" + match.group(0)[-9:] if match else ""

def extract_location(text):
    match = re.search(r"(?i)(riyadh|jeddah|dammam|madinah|المدينة|مكة|خميس|ابها|saudi arabia|ksa|اليمن|اليمنية|دبي|أبو ظبي|الإمارات)", text)
    return match.group(0) if match else ""

def extract_nationality(text):
    match = re.search(r"(?i)(nationality|الجنسية)\s*[:\-]?\s*([\w ]+)", text)
    return match.group(2).strip() if match else ""

def extract_experience_years(text):
    match = re.search(r"(\d{1,2})\s*(years|سنة|سنوات)", text)
    return match.group(1) if match else ""

def extract_languages(text):
    langs = re.findall(r"(?i)(arabic|english|الإنجليزية|العربية|french|urdu|spanish|german|hindi)", text)
    return " / ".join(sorted(set([lang.capitalize() for lang in langs])))

def infer_candidate_role(text):
    roles = [
        "Project Engineer", "IT Support", "Network Engineer", "Software Developer",
        "Database Administrator", "System Analyst", "Business Analyst", "Data Scientist",
        "Help Desk", "Technical Support", "Network Administrator"
    ]
    for role in roles:
        if re.search(role, text, re.IGNORECASE):
            return role
    match = re.search(r"(?i)(position|role|مسمى وظيفي|عملت كـ)[:\-]?\s*([\w \-]+)", text)
    if match:
        return match.group(2).strip()
    return ""

def extract_all_data(filepath, job_description):
    text = clean_text(extract_text(filepath))
    if not text.strip():
        return None
    score = calculate_match_score(text, job_description)
    return {
        "name": os.path.splitext(os.path.basename(filepath))[0],
        "file": filepath,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": extract_location(text),
        "nationality": extract_nationality(text),
        "experience_years": extract_experience_years(text),
        "languages": extract_languages(text),
        "candidate_role": infer_candidate_role(text),
        "match_score": score,
        "match_level": classify_match(score),
        "extracted_at": datetime.now()
    }
