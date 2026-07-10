# AI CV Analyzer

An automated, intelligent résumé parsing and screening application designed to streamline human resources and recruitment workflows. Built entirely in Python using Streamlit, this platform leverages multi-provider Large Language Models (LLMs) to extract, analyze, and score candidate CVs against custom job criteria with cross-language support.

---

## 🚀 Key Features

* **Multi-Provider AI Engine:** Dynamic connections to leading AI providers with built-in token usage metering to track API consumption in real time.
* **Intelligent Document Processing:** Native browser-based CV uploading with robust support for standard document types (`.doc`, `.docx`, `.pdf`) and integrated **OCR (Optical Character Recognition)** for processing scanned images or PDFs.
* **Advanced Evaluation Framework:** Automated screening, candidate analysis, matching criteria scoring, and top multi-candidate comparisons.
* **Bi-directional Localization (RTL/LTR):** Complete dual-language support for both **Arabic and English** interfaces, seamlessly adjusting layout direction dynamically based on your preference.
* **Enterprise-Ready Deployment:** Containerized setup for quick local deployment or production orchestration.

---

## 🛠️ Tech Stack

* **Frontend & UI:** [Streamlit](https://streamlit.io/)
* **Core Backend:** Python 3.11+
* **Environment & DevOps:** Docker, Docker Compose, GitHub Actions (CI/CD)
* **Supported Execution Environments:** Linux/Unix (`run.sh`), Windows (`run.bat`)

---

## 📁 Project Structure

```text
ai-cv-analyzer/
├── .devcontainer/        # Local containerized development settings
├── .github/workflows/    # Automated CI security & code scanning pipelines
├── .streamlit/           # Streamlit deployment configurations
├── data/                 # Sample data and evaluation storage
├── src/                  # Core application source code (Modules, AI configuration, UI)
├── tests/                # Automated testing suite
├── Dockerfile            # Multi-stage Docker build file
├── docker-compose.yml    # Local multi-container orchestration profile
├── requirements.txt      # Python dependencies
└── packages.txt          # System-level dependencies (required for OCR/document parsers)
==============================================================================================================================

⚙️ Installation & Setup
Option 1: Local Installation (Python)
1.Clone the Repository:
git clone [https://github.com/hossamk80/ai-cv-analyzer.git](https://github.com/hossamk80/ai-cv-analyzer.git)
cd ai-cv-analyzer

2. Install System Dependencies:
Ensure your local system has the necessary binary packages installed for document processing (e.g., tesseract for OCR, antiword or similar for older .doc formats). Reference packages.txt for details.

3.Install Python Packages:
pip install -r requirements.txt

4.Run the Application:
* Windows: Double-click run.bat or run it via Command Prompt.
* Linux/macOS: Run chmod +x run.sh && ./run.sh.
=========================================================================================================================================
Option 2: Docker Deployment 🐳
Deploying the analyzer via Docker ensures all document parsing libraries, OCR environments, and font sets are configured correctly out-of-the-box.
Using Docker Compose (Recommended)
To launch the complete application environment locally:
docker-compose up --build
Once the container finishes initializing, open your web browser and navigate to http://localhost:8501.

Using the Dockerfile Alone
docker build -t ai-cv-analyzer .
docker run -p 8501:8501 ai-cv-analyzer
=========================================================================================================================================

🛠️ Configuration & Usage
1. AI Setup: Navigate to the AI Settings page in the application sidebar to select your preferred AI provider, input your API credentials, and monitor your token meter consumption.
2. Set Criteria: Define your target job descriptions, mandatory skills, or evaluation benchmarks.
3. Upload & Analyze: Drop one or multiple CV files into the browser interface. The system will auto-detect document layouts, apply OCR if necessary, and output clean analytical reports and compatibility matrices.
