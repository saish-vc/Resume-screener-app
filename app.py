import streamlit as st
import pandas as pd
import io
import os
import collections

# Import custom modules
from utils import extract_contact_info, extract_skills_from_text
from parser import parse_resume
from matcher import calculate_match_score

# Set page configurations
st.set_page_config(
    page_title="Automated Resume Screener MVP",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Automated generation of sample files on startup if they don't exist
if not os.path.exists("sample_resumes") or len(os.listdir("sample_resumes")) < 3:
    try:
        import subprocess
        subprocess.run(["python", "generate_samples.py"], capture_output=True)
    except Exception as e:
        pass

# ---------------------------------------------------------
# UI Layout Styling
# ---------------------------------------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .verdict-high {
        color: #15803D;
        font-weight: 600;
        background-color: #DCFCE7;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .verdict-medium {
        color: #B45309;
        font-weight: 600;
        background-color: #FEF3C7;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .verdict-low {
        color: #B91C1C;
        font-weight: 600;
        background-color: #FEE2E2;
        padding: 4px 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------
st.sidebar.title("📁 Resume Inputs")
st.sidebar.markdown("Upload candidate resumes below or use preloaded samples to test instantly.")

# Upload Files
uploaded_files = st.sidebar.file_uploader(
    "Upload Resumes (.pdf, .docx, .txt)", 
    type=["pdf", "docx", "txt"], 
    accept_multiple_files=True
)

st.sidebar.markdown("---")

# Sample Resumes Checkbox
use_samples = st.sidebar.checkbox("🚀 Use 3 Preloaded Sample Resumes", value=False, 
                                 help="Automatically load John Doe (high match), Jane Smith (medium match), and Bob Johnson (low match) to test the app.")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### How to run locally:
1. Install requirements:
   `pip install -r requirements.txt`
2. Run Streamlit:
   `streamlit run app.py`
""")

# ---------------------------------------------------------
# Main Panel
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>📄 Automated Resume Screener MVP</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>A lightweight application to evaluate, score, and rank candidates by matching resumes against a target job description.</p>", unsafe_allow_html=True)

# Job Description block
st.subheader("💼 Job Description Input")

# Sample JD text loading helper
sample_jd_content = ""
if os.path.exists("sample_jd.txt"):
    try:
        with open("sample_jd.txt", "r", encoding="utf-8") as f:
            sample_jd_content = f.read()
    except Exception as e:
        sample_jd_content = f"Error loading sample job description: {e}"

# Pre-populate JD or let user paste
col_jd_btns, _ = st.columns([1, 3])
with col_jd_btns:
    load_sample_jd = st.button("📝 Load Sample Job Description")

# Streamlit session state for managing JD input value
if "jd_input" not in st.session_state:
    st.session_state.jd_input = ""

if load_sample_jd:
    st.session_state.jd_input = sample_jd_content

jd_text = st.text_area(
    "Paste the Job Description here:", 
    value=st.session_state.jd_input, 
    height=250, 
    placeholder="Paste detailed requirements here... include skills, framework requirements, databases, and general experience keywords."
)

# Synchronize session state
st.session_state.jd_input = jd_text

# Trigger analysis button
screen_clicked = st.button(" Screen & Match Resumes", type="primary")

# ---------------------------------------------------------
# Resume Analysis Logic
# ---------------------------------------------------------
if screen_clicked:
    # 1. Validation
    if not jd_text.strip():
        st.error(" Please provide a job description first!")
        st.stop()
        
    files_to_process = []
    
    # Check if we should load samples
    if use_samples:
        sample_dir = "sample_resumes"
        if os.path.exists(sample_dir):
            for fname in os.listdir(sample_dir):
                fpath = os.path.join(sample_dir, fname)
                if os.path.isfile(fpath) and fname.split('.')[-1].lower() in ['txt', 'docx', 'pdf']:
                    try:
                        with open(fpath, "rb") as f:
                            file_bytes = f.read()
                            files_to_process.append({
                                "name": fname,
                                "stream": io.BytesIO(file_bytes)
                            })
                    except Exception as e:
                        st.sidebar.error(f"Failed to read sample file {fname}: {e}")
        else:
            st.error(" Sample resumes directory not found! Try uploading files manually.")
            st.stop()

    # Load uploaded files
    if uploaded_files:
        for uf in uploaded_files:
            files_to_process.append({
                "name": uf.name,
                "stream": io.BytesIO(uf.getvalue())
            })
            
    if not files_to_process:
        st.error(" No resumes found! Please upload one or more resumes in the sidebar or toggle 'Use 3 Preloaded Sample Resumes'.")
        st.stop()
        
    # 2. Run Parsing and Matching
    results = []
    skipped_files = []
    
    with st.spinner("Processing resumes, extracting text, and scoring match..."):
        for item in files_to_process:
            fname = item["name"]
            stream = item["stream"]
            
            try:
                # Extract text
                raw_text = parse_resume(stream, fname)
                
                # Check if we got any text
                if not raw_text.strip():
                    skipped_files.append((fname, "Empty text extracted from file."))
                    continue
                    
                # Extract contact info from raw text
                contact_info = extract_contact_info(raw_text)
                
                # Calculate Match Metrics
                metrics = calculate_match_score(raw_text, jd_text)
                
                # Build Result dictionary
                results.append({
                    "Candidate / Filename": fname,
                    "Email": contact_info["email"],
                    "Phone": contact_info["phone"],
                    "Cosine Similarity (%)": metrics["cosine_similarity"],
                    "Keyword Overlap (%)": metrics["keyword_coverage"],
                    "Match Score (%)": metrics["final_score"],
                    "Verdict": metrics["verdict"],
                    "Matched Skills": metrics["matched_skills"],
                    "Missing Skills": metrics["missing_skills"],
                    "All Resume Skills": metrics["all_resume_skills"],
                    "raw_text": raw_text
                })
                
            except Exception as e:
                skipped_files.append((fname, str(e)))
                
    # 3. Render Results UI
    st.markdown("---")
    st.subheader(" Screening Results & Ranking")
    
    # Display any skipped files with errors
    if skipped_files:
        for sf_name, error_msg in skipped_files:
            st.warning(f"⚠️ Skipped **{sf_name}**: {error_msg}")
            
    if not results:
        st.error("❌ No resumes could be successfully parsed or matched.")
        st.stop()
        
    # Sort results by final score descending
    sorted_results = sorted(results, key=lambda x: x["Match Score (%)"], reverse=True)
    
    # Create pandas dataframe for the main ranked table
    df_results = pd.DataFrame(sorted_results)
    
    # Prepare formatted df for clean presentation
    df_display = df_results[[
        "Candidate / Filename", 
        "Email", 
        "Phone", 
        "Match Score (%)", 
        "Verdict"
    ]].copy()
    
    # Render main overview table
    st.dataframe(
        df_display, 
        use_container_width=True,
        column_config={
            "Match Score (%)": st.column_config.ProgressColumn(
                "Match Score (%)",
                help="Weighted Match: 70% TF-IDF Cosine Similarity + 30% Skill Overlap",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        }
    )
    
    # CSV Download Button
    csv_buffer = io.StringIO()
    df_export = df_results.drop(columns=["raw_text"]) # drop raw text for cleaner CSV export
    df_export.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    
    st.download_button(
        label="📥 Export Results to CSV",
        data=csv_bytes,
        file_name="resume_screener_results.csv",
        mime="text/csv"
    )
    
    # 4. Score Visualization
    st.markdown("---")
    st.subheader("📈 Match Score Distribution")
    
    # Create simple visualization using streamlit bar chart
    df_chart = df_results[["Candidate / Filename", "Match Score (%)", "Cosine Similarity (%)", "Keyword Overlap (%)"]].copy()
    st.bar_chart(df_chart, x="Candidate / Filename", y=["Match Score (%)", "Cosine Similarity (%)", "Keyword Overlap (%)"])
    
    # 5. Nice Small Enhancements: Pool Insights
    st.markdown("---")
    col_insights, col_missing = st.columns([1, 1])
    
    with col_insights:
        st.subheader("💡 Applicant Pool Overview")
        avg_score = df_results["Match Score (%)"].mean()
        high_matches = sum(1 for r in results if r["Verdict"] == "High Match")
        med_matches = sum(1 for r in results if r["Verdict"] == "Medium Match")
        low_matches = sum(1 for r in results if r["Verdict"] == "Low Match")
        
        st.metric("Average Pool Match Score", f"{avg_score:.1f}%")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("🟢 High Matches", high_matches)
        col_m2.metric("🟡 Medium Matches", med_matches)
        col_m3.metric("🔴 Low Matches", low_matches)
        
    with col_missing:
        st.subheader("🚨 Top Missing Skills in Applicant Pool")
        # Collect missing skills from all candidates
        all_missing = []
        for r in results:
            all_missing.extend(r["Missing Skills"])
            
        if all_missing:
            missing_counts = collections.Counter(all_missing)
            # Display top 5 missing skills
            top_missing = missing_counts.most_common(5)
            
            # Simple custom display list
            for skill, count in top_missing:
                percentage = (count / len(results)) * 100
                st.markdown(f"**{skill.title()}** - Missing in **{percentage:.0f}%** of resumes ({count}/{len(results)} applicants)")
        else:
            st.success("🎉 Excellent! All skills specified in the job description are fully covered by the applicant pool!")
            
    # 6. Detailed Candidate Profiles
    st.markdown("---")
    st.subheader("🔍 Detailed Candidate Profile Breakdown")
    
    for idx, candidate in enumerate(sorted_results):
        # Color formatting for verdict pill
        verdict_class = "verdict-low"
        if candidate["Verdict"] == "High Match":
            verdict_class = "verdict-high"
        elif candidate["Verdict"] == "Medium Match":
            verdict_class = "verdict-medium"
            
        header_text = f"Rank #{idx+1}: {candidate['Candidate / Filename']} — Score: {candidate['Match Score (%)']}% ({candidate['Verdict']})"
        
        with st.expander(header_text):
            # Layout columns inside candidate profile
            c_col1, c_col2 = st.columns([1, 1])
            
            with c_col1:
                st.markdown("### 📞 Contact Details")
                st.markdown(f"**📧 Email:** {candidate['Email']}")
                st.markdown(f"**📱 Phone:** {candidate['Phone']}")
                
                st.markdown("### 📐 Metric Scores")
                st.write(f"- **TF-IDF Cosine Similarity (70% Weight):** {candidate['Cosine Similarity (%)']}%")
                st.write(f"- **Key Skill Keyword Overlap (30% Weight):** {candidate['Keyword Overlap (%)']}%")
                
                # Display Verdict with Custom Colored Pill Style
                st.markdown(f"**Verdict Status:** <span class='{verdict_class}'>{candidate['Verdict']}</span>", unsafe_allow_html=True)
                
            with c_col2:
                # Skill breakdowns
                st.markdown("### 🛠️ Skills Analysis")
                
                tab_matched, tab_missing, tab_all = st.tabs(["✅ Matched Skills", "❌ Missing Skills", "📋 All Skills Found"])
                
                with tab_matched:
                    if candidate["Matched Skills"]:
                        for s in candidate["Matched Skills"]:
                            st.markdown(f"🟢 **{s.title()}**")
                    else:
                        st.info("No matching predefined skills found in this resume.")
                        
                with tab_missing:
                    if candidate["Missing Skills"]:
                        for s in candidate["Missing Skills"]:
                            st.markdown(f"🔴 **{s.title()}**")
                    else:
                        st.success("No missing predefined skills! The candidate matches all job requirements.")
                        
                with tab_all:
                    if candidate["All Resume Skills"]:
                        st.write(", ".join([s.title() for s in candidate["All Resume Skills"]]))
                    else:
                        st.info("No predefined skills detected in the candidate's resume.")
                        
            # Raw Text view option
            st.markdown("---")
            with st.expander(" View Extracted Resume Raw Text"):
                st.code(candidate["raw_text"], language="text")
else:
    # Friendly state if no analysis has been run
    st.info(" Welcome! Upload resumes in the sidebar (or toggle 'Use 3 Preloaded Sample Resumes') and provide a job description. Then click 'Screen & Match Resumes' to see results.")
