# Automated Resume Screener MVP 📄💼

A lightweight, local web application that extracts text from multiple resumes (PDF, DOCX, and TXT), extracts email/phone contact info, identifies matching/missing skills, and scores candidates against a target Job Description. 

This project is designed as a **Minimum Viable Product (MVP)** for recruiters or hiring managers. It's built in Python using **Streamlit** for a rapid, beautiful UI, and **Scikit-Learn** for modern text similarity analytics.

---

## 🚀 Quickstart Guide

Getting the app running locally takes less than 2 minutes.

### 1. Prerequisites
Make sure you have **Python 3.8+** installed on your machine. You can check your version with:
```bash
python --version
```

### 2. Installation
Open your terminal in the project directory and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Generate Sample Resumes (Optional but Automated)
The app will automatically generate sample resumes in the `sample_resumes/` folder on its first boot. If you want to run it manually first, execute:
```bash
python generate_samples.py
```
This will create:
* `sample_resumes/john_doe_resume.docx` (Highly matched full-stack candidate)
* `sample_resumes/jane_smith_resume.txt` (Medium-matched backend developer)
* `sample_resumes/bob_johnson_resume.docx` (Low-matched sales manager candidate)

### 4. Run the Streamlit Application
Start the local server with:
```bash
streamlit run app.py
```
A browser tab should open automatically to `http://localhost:8501`. If it doesn't, copy the URL from your terminal.

---

## 📊 Scoring Approach

The Automated Resume Screener uses a hybrid scoring system designed to evaluate both general context and specific skill requirements.

$$\text{Final Score} = (0.70 \times \text{Cosine Similarity}) + (0.30 \times \text{Keyword Overlap Coverage})$$

1. **TF-IDF + Cosine Similarity (70% Weight)**:
   * **Under the hood**: The text from the job description and the resume are vectorized using Term Frequency-Inverse Document Frequency (TF-IDF). Stop words (common English words like *the, are, dynamic, highly*) are removed to ensure only meaningful words are scored.
   * **Purpose**: Measures the overall thematic similarity of the resume compared to the job description, capturing background, terminology, and semantic context.
   
2. **Key Skill Keyword Overlap (30% Weight)**:
   * **Under the hood**: Both the job description and the resume are scanned against a predefined vocabulary of over 60 common programming languages, frameworks, methodologies, and soft skills (defined in `utils.py`). Let $S_{jd}$ be the skills found in the Job Description, and $S_{res}$ be the skills found in the Resume.
   * **Coverage Score**: If $S_{jd}$ is empty, the score defaults to $100\%$. Otherwise, the score is:
     $$\text{Coverage} = \frac{|S_{jd} \cap S_{res}|}{|S_{jd}|} \times 100$$
   * **Purpose**: Ensures that even if a resume is written with similar verbs/adjectives, candidates are heavily scored based on actual specified toolkits and technology stacks.

### Match Verdict Thresholds
* 🟢 **High Match**: $\ge 50\%$
* 🟡 **Medium Match**: $30\% - 49.9\%$
* 🔴 **Low Match**: $< 30\%$

---

## 📁 Folder Structure

```text
resume-scanner/
├── app.py                # Main Streamlit web application & UI pipeline
├── parser.py             # File parsing logic (PDF, DOCX, TXT)
├── matcher.py            # Scoring implementation (TF-IDF + Cosine, Keyword coverage)
├── utils.py              # Text cleaning, contact regex, and predefined skills list
├── requirements.txt      # List of dependencies
├── sample_jd.txt         # Preloaded sample job description
├── generate_samples.py   # Script to programmatically write sample resumes (.docx, .txt)
├── README.md             # Project documentation (this file)
└── sample_resumes/       # Directory containing generated candidate resumes
    ├── john_doe_resume.docx
    ├── jane_smith_resume.txt
    └── bob_johnson_resume.docx
```

---

## 🛠️ Feature Highlights

### 1. Unified Inputs
* **Sidebar File Uploads**: Upload multiple `.pdf`, `.docx`, or `.txt` resumes at once. Skip unsupported file extensions with clean warnings.
* **Instant Demo Mode**: A checkbox in the sidebar allows you to load the preloaded sample resumes directly from disk without manual upload.
* **Sample Job Description**: Click the button above the Job Description text area to pre-populate it with a Senior Full-Stack Python Developer job description.

### 2. Deep Skill & Context Analytics
* **Contact Information Extraction**: Uses robust regex patterns to find emails and standard phone numbers dynamically.
* **Matched vs. Missing Skills**: Compares extracted skill lists to show exactly which requested skills the candidate possessed, and which ones are missing.
* **Raw Text Inspector**: Toggle open an expander on any candidate to inspect the raw text extracted from their PDF/Word files.

### 3. Recruitment Pool Insights
* **Applicant Pool Overview**: Displays the average pool match score and counts of High, Medium, and Low matches.
* **Top Missing Skills section**: Aggregates all missing skills across the applicant pool and ranks them by how common the omission is. (e.g., "AWS - Missing in 67% of resumes").
* **Score Visualization**: Interactive bar charts mapping candidates against final match scores, cosine similarity, and skill overlap.
* **Export CSV**: Download a single-click generated CSV report containing ranked results with contact information, scores, and verdicts.

---

## 🛡️ Engineering Standards Applied

* **Memory-Safe Uploads**: Streams uploaded files inside RAM (`io.BytesIO`) rather than saving unmanaged files to disk.
* **Graceful Fallbacks**: Automatically falls back to Latin-1 encoding if TXT files cannot be parsed using UTF-8. Skips corrupted or blank files with clean warnings rather than crashing the thread.
* **Robust Keyword Extraction**: Skill parsing uses word boundary matching (`\b` boundaries with custom punctuation handlers) to avoid matching sub-words (e.g., matching the skill `go` will not trigger on `django` or `gopher`).
