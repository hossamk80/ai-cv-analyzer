import streamlit as st
import pandas as pd
import urllib.parse
import os
import fitz  # PyMuPDF
import glob
from extract_cv_data import extract_all_data

st.set_page_config(page_title="لوحة تحليل السير الذاتية المطورة", layout="wide")
st.title("📄 لوحة تحليل السير الذاتية الاحترافية")

# إدارة الإعدادات والمسارات عبر شريط جانبي آمن مرن
BASE_FOLDER = st.sidebar.text_input("📁 مسار مجلد السير الذاتية الأساسي", value=r"D:\CVS project")

if not os.path.exists(BASE_FOLDER):
    st.sidebar.error("المسار المحلي المحدد غير موجود! يرجى تصحيحه.")
    st.stop()

subfolders = [f.name for f in os.scandir(BASE_FOLDER) if f.is_dir()]
if subfolders:
    selected_subfolder = st.sidebar.selectbox("📁 اختر المجلد الفرعي للمشروع", subfolders)
    CV_FOLDER = os.path.join(BASE_FOLDER, selected_subfolder)
else:
    CV_FOLDER = BASE_FOLDER

# إضافة صندوق نصي ديناميكي للوصف الوظيفي (Business & Product Management improvement)
st.markdown("### 🎯 تخصيص متطلبات المطابقة والتوظيف")
default_jd = "مأمور دعم فني | Technical support officer - خبرة في الشبكات والدعم الفني وصيانة الحواسب والأنظمة الفنية"
job_description = st.text_area("📝 الصق الوصف الوظيفي للوظيفة الشاغرة هنا لضبط معايير التطابق آلياً:", value=default_jd, height=120)

# تحسين كفاءة النظام والأداء باستخدام الـ Caching (Systems Engineering Improvement)
@st.cache_data(show_spinner="جاري معالجة وتحليل مستندات السير الذاتية... يرجى الانتظار قليلاً")
def parse_and_load_cvs(folder_path, jd):
    records = []
    search_path = os.path.join(folder_path, '*')
    for filepath in glob.glob(search_path):
        if os.path.isfile(filepath):
            record = extract_all_data(filepath, jd)
            if record:
                records.append(record)
    return pd.DataFrame(records)

# استدعاء البيانات المعالجة بشكل مخزن مؤقتاً
df = parse_and_load_cvs(CV_FOLDER, job_description)

if df.empty:
    st.warning("لا توجد سير ذاتية صالحة أو مقروءة في المجلد المختار حالياً.")
    st.stop()

# زر إعادة ضبط الفلاتر التفاعلية
if st.sidebar.button("🔄 إعادة تعيين الفلاتر"):
    st.rerun()

# الفلاتر واللوحات الجانبية المتقدمة
with st.sidebar:
    st.header("تصفية وفلترة المرشحين")
    city = st.selectbox("اختر المدينة", options=[""] + sorted(df.location.dropna().unique()))
    nationality = st.selectbox("اختر الجنسية", options=[""] + sorted(df.nationality.dropna().unique()))
    match_level = st.multiselect("مستوى التطابق المستهدف", options=sorted(df.match_level.unique()), default=sorted(df.match_level.unique()))
    min_experience = st.slider("أقل عدد سنوات خبرة عملية", min_value=0, max_value=30, value=0)
    search_text = st.text_input("🔍 بحث نصي حر شامل داخل الملفات")

# تطبيق الفلاتر برمجياً على الداتا فريم
filtered_df = df.copy()
if city:
    filtered_df = filtered_df[filtered_df.location.str.contains(city, case=False, na=False)]
if nationality:
    filtered_df = filtered_df[filtered_df.nationality.str.contains(nationality, case=False, na=False)]
if match_level:
    filtered_df = filtered_df[filtered_df.match_level.isin(match_level)]
if 'experience_years' in filtered_df.columns:
    filtered_df['experience_years'] = pd.to_numeric(filtered_df['experience_years'], errors='coerce')
    filtered_df = filtered_df[(filtered_df['experience_years'].isna()) | (filtered_df['experience_years'] >= min_experience)]
if search_text:
    filtered_df = filtered_df[filtered_df.apply(lambda row: search_text.lower() in str(row).lower(), axis=1)]

# عرض ملخص البيانات والإحصائيات الحيوية لمدراء المنتج
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("إجمالي السير الذاتية المعالجة", len(df))
with col2:
    st.metric("عدد النتائج المطابقة للفلترة", len(filtered_df))
with col3:
    excel_status = "جاهز للتصدير" if not filtered_df.empty else "فارغ"
    st.metric("حالة ملف المخرجات", excel_status)

# زر تصدير النتائج لملفات العمل والـ Excel
st.download_button(
    label="📥 تصدير قائمة المرشحين المفلترة كـ CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8-sig'),
    file_name='optimized_candidates_report.csv',
    mime='text/csv'
)

# عرض الجدول الرئيسي لأعمدة البيانات المتاحة
columns_to_show = [
    "name", "email", "phone", "location", "nationality", "candidate_role", "experience_years", "languages", "match_score", "match_level"
]
actual_columns = [col for col in columns_to_show if col in filtered_df.columns]
st.dataframe(filtered_df[actual_columns], use_container_width=True)

# بوابات التواصل المباشر مع المرشحين المختبرين
st.markdown("---")
st.header("📤 قنوات التواصل والربط مع المرشح")
if not filtered_df.empty:
    selected_name = st.selectbox("اختر اسماً من القائمة لبدء الاتصال وتدقيق الملف الخاص به:", filtered_df.name)
    row = filtered_df[filtered_df.name == selected_name].iloc[0]

    # رسالة تواصل ديناميكية احترافية مستنبطة من مخرجات كود تحليل الدور الوظيفي
    default_msg = f"""
السلام عليكم ورحمة الله وبركاته {row['name']},
نأمل أن تكون بخير. لقد اطلعنا على سيرتك الذاتية الممتازة ونرى أن خبرتك في مجال {row.get('candidate_role', 'الدعم الفني')} متوافقة وممتازة مع متطلباتنا الوظيفية الحالية.
هل أنت متاح لإجراء مكالمة هاتفية قصيرة لمناقشة الفرص المتاحة هذا الأسبوع؟
شاكرين ومقدرين لك.
""".strip()

    msg_template = st.text_area("📩 نص الرسالة المخصصة (يمكنك تعديلها بحرية):", value=default_msg, height=140)
    subject_text = st.text_input("📝 عنوان موضوع البريد الإلكتروني الافتراضي (Subject):", value="فرصة وظيفية واعدة ومناقشة السيرة الذاتية")
    
    encoded_msg = urllib.parse.quote(msg_template)
    email_subject = urllib.parse.quote(subject_text)
    email_body = urllib.parse.quote(msg_template)

    # أزرار الربط التفاعلية السريعة
    c1, c2, c3 = st.columns(3)
    with c1:
        if pd.notnull(row.get("phone")):
            phone_str = str(row["phone"]).replace('+', '').replace('.0', '')
            whatsapp_url = f"https://wa.me/{phone_str}?text={encoded_msg}"
            st.markdown(f"[📱 أرسل عبر واتساب مباشرة]({whatsapp_url})")
    with c2:
        if pd.notnull(row.get("email")):
            mailto_url = f"mailto:{row['email']}?subject={email_subject}&body={email_body}"
            st.markdown(f"[📧 إرسال بريد إلكتروني رسمي]({mailto_url})")
    with c3:
        if pd.notnull(row.get("linkedin")):
            st.markdown(f"[🔗 فتح حساب المرشح في لينكدإن]({row['linkedin']})")

    # بوابة استعراض محتويات السيرة الذاتية وعرضها محلياً بأمان
    st.markdown("---")
    st.subheader("📄 لوحة المعاينة الفورية لملف السيرة الذاتية")
    if os.path.exists(row['file']):
        ext = os.path.splitext(row['file'])[1].lower()
        if ext == '.pdf':
            with open(row['file'], "rb") as f:
                st.download_button("📂 تحميل نسخة الـ PDF الحالية للملف", f, file_name=os.path.basename(row['file']))
            try:
                doc = fitz.open(row['file'])
                text = "\n\n".join([page.get_text() for page in doc])
                st.text_area("النصوص الكاملة المستخرجة من سياق الـ PDF الحالي للمراجعة العميقة:", text, height=350)
            except Exception as e:
                st.warning(f"تعذر استخراج وعرض محتويات الـ PDF النصية بالكامل تلقائياً: {e}")
        elif ext in ['.png', '.jpg', '.jpeg']:
            st.image(row['file'], caption=row['name'])
        elif ext in ['.txt', '.docx']:
            with open(row['file'], "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                st.text_area("محتويات الملف النصي المفتوح:", content, height=350)
        else:
            st.info("نوع وصيغة هذا الملف غير مدعومة للعرض الهيكلي الفوري مباشرة داخل لوحة التحكم.")
else:
    st.warning("نعتذر! لا توجد نتائج مطابقة لخيارات الفلترة والتصفية الحالية.")
