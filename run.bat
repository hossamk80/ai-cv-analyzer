@echo off
chcp 65001 >nul

echo 🚀 بدء تشغيل تطبيق تحليل السير الذاتية...
echo.

REM التحقق من Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت. يرجى تثبيته أولاً.
    pause
    exit /b 1
)

echo ✓ Python موجود

REM التحقق من وجود venv
if not exist "venv" (
    echo 📦 إنشاء بيئة افتراضية...
    python -m venv venv
)

REM تفعيل البيئة الافتراضية
echo ✓ تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat

REM تثبيت المتطلبات
echo 📥 تثبيت المكتبات المطلوبة...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM التحقق من وجود مجلد data
if not exist "data" (
    echo 📁 إنشاء مجلد data...
    mkdir data
)

REM تشغيل التطبيق
echo.
echo ✨ جاري تشغيل التطبيق...
echo الرابط: http://localhost:8501
echo.

streamlit run src/dashboard.py

pause
