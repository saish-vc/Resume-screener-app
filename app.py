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
    page_title="Resume Screener - AI-Powered Candidate Matching",
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
# Professional UI Styling with Premium Beige Theme
# ---------------------------------------------------------
st.markdown("""
<style>
    :root {
        /* Premium Beige Color Palette */
        --primary-color: #3D3D3D;
        --secondary-color: #5C5148;
        --accent-color: #A67C52;
        --accent-light: #C99A6E;
        --success-color: #7BA96E;
        --warning-color: #D4A574;
        --danger-color: #B85C5C;
        --background: #F5F1ED;
        --card-bg: #FEFCF9;
        --border-color: #E8DFD5;
        --text-primary: #3D3D3D;
        --text-secondary: #8B7E76;
        --beige-light: #F9F6F3;
        --beige-medium: #E8DFD5;
        --beige-dark: #D4C4B8;
    }

    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                     'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                     sans-serif;
    }

    body, .main {
        background: linear-gradient(135deg, var(--background) 0%, var(--beige-light) 100%);
        color: var(--text-primary);
    }

    /* Header & Title Styles */
    .main-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 2rem;
        padding: 2rem;
        border-bottom: 3px solid var(--accent-color);
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--beige-light) 100%);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: var(--primary-color);
        margin: 0;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0.5rem 0 0 0;
        font-weight: 400;
        line-height: 1.5;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--accent-color);
    }

    /* Card Styles */
    .metric-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--beige-light) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: var(--accent-color);
        box-shadow: 0 8px 20px rgba(166, 124, 82, 0.12);
        transform: translateY(-2px);
    }

    /* Verdict Pills */
    .verdict-high {
        display: inline-block;
        background: linear-gradient(135deg, #E8F3E8 0%, #D4E8D4 100%);
        color: #4A6B4A;
        font-weight: 700;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #A8D4A8;
        font-size: 0.9rem;
        box-shadow: 0 2px 4px rgba(123, 169, 110, 0.15);
    }

    .verdict-medium {
        display: inline-block;
        background: linear-gradient(135deg, #F9F1E8 0%, #F0E3D4 100%);
        color: #7A5C3C;
        font-weight: 700;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #D4A574;
        font-size: 0.9rem;
        box-shadow: 0 2px 4px rgba(212, 165, 116, 0.15);
    }

    .verdict-low {
        display: inline-block;
        background: linear-gradient(135deg, #F8E8E8 0%, #EDD4D4 100%);
        color: #7A4C4C;
        font-weight: 700;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #D4A4A4;
        font-size: 0.9rem;
        box-shadow: 0 2px 4px rgba(184, 92, 92, 0.15);
    }

    /* Button Styles */
    .stButton > button {
        width: 100%;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease !important;
        font-size: 0.95rem;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-light) 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(166, 124, 82, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 20px rgba(166, 124, 82, 0.4) !important;
        transform: translateY(-2px);
    }

    .stButton > button[kind="secondary"] {
        background: var(--beige-medium) !important;
        color: var(--primary-color) !important;
        border: 2px solid var(--border-color) !important;
    }

    /* Input Styles */
    .stTextArea, .stFileUploader {
        border-radius: 8px !important;
    }

    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 2px solid var(--border-color) !important;
        background-color: var(--card-bg) !important;
        color: var(--text-primary) !important;
        font-family: 'Fira Code', monospace;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-color) !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--beige-light) 0%, var(--background) 100%);
    }

    .sidebar .sidebar-content {
        background-color: transparent;
    }

    /* Dataframe Styles */
    .stDataFrame {
        border-radius: 12px !important;
        border: 2px solid var(--border-color) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        background-color: var(--card-bg) !important;
    }

    /* Expander Styles */
    .streamlit-expanderHeader {
        border-radius: 8px !important;
        border: 2px solid var(--border-color) !important;
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--beige-light) 100%) !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, var(--beige-light) 0%, var(--background) 100%) !important;
        border-color: var(--accent-color) !important;
        box-shadow: 0 4px 12px rgba(166, 124, 82, 0.1) !important;
    }

    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: var(--background);
        padding: 0.5rem;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600;
        background: var(--beige-medium);
        color: var(--text-primary);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-light) 100%);
        color: white;
    }

    /* Metric Styles */
    .stMetric {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--beige-light) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .stMetric > div > div > label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stMetric > div > div > div {
        font-size: 2rem;
        font-weight: 800;
        color: var(--accent-color);
    }

    /* Progress Bar Styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent-color) 0%, var(--accent-light) 100%);
        border-radius: 4px;
    }

    /* Alert Styles */
    .stAlert {
        border-radius: 8px !important;
        padding: 1rem 1.5rem !important;
        font-weight: 500;
        background-color: var(--card-bg) !important;
        border-left: 4px solid var(--accent-color) !important;
    }

    .stAlert > div > div > div > p {
        margin: 0;
    }

    /* Code Block Styling */
    .stCodeBlock {
        border-radius: 8px !important;
        border: 2px solid var(--border-color) !important;
        background-color: var(--beige-light) !important;
    }

    /* Horizontal Line */
    hr {
        border: none;
        border-top: 2px solid var(--border-color);
        margin: 2rem 0;
    }

    /* Checkbox Styling */
    .stCheckbox {
        padding: 0.5rem 0;
    }

    /* Skill Tags */
    .skill-tag {
        display: inline-block;
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-light) 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem 0.25rem 0.25rem 0;
        box-shadow: 0 2px 4px rgba(166, 124, 82, 0.2);
    }

    .skill-tag-missing {
        display: inline-block;
        background: linear-gradient(135deg, var(--danger-color) 0%, #D17A7A 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem 0.25rem 0.25rem 0;
        box-shadow: 0 2px 4px rgba(184, 92, 92, 0.2);
    }

    /* Info Box Styling */
    .info-box {
        background: linear-gradient(135deg, #F0F4F8 0%, #E8DFD5 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--accent-color);
        color: var(--text-secondary);
    }

    /* Responsive */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .section-header {
            font-size: 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.5rem 0;">
        <h2 style="margin: 0; color: var(--primary-color); font-size: 1.3rem; font-weight: 700;">📁 Resume Input</h2>
        <p style="color: var(--text-secondary); margin: 0.5rem 0 0 0; font-size: 0.9rem;">Upload candidates or use sample data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Upload Files
    uploaded_files = st.file_uploader(
        "📄 Upload Resumes", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    st.markdown("---")
    
    # Sample Resumes Checkbox
    use_samples = st.checkbox(
        "🚀 Use Sample Resumes",
        value=False,
        help="Load 3 pre-built sample resumes to test the app instantly"
    )
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #F9F6F3 0%, #E8DFD5 100%); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--accent-color);">
        <p style="margin: 0; font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Quick Start</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: var(--primary-color); line-height: 1.5;">
            <strong>1.</strong> Paste a job description<br>
            <strong>2.</strong> Upload resumes or use samples<br>
            <strong>3.</strong> Click "Screen & Match"
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Panel Header
# ---------------------------------------------------------
col_header, col_logo = st.columns([4, 1])
with col_header:
    st.markdown("""
    <div class="main-header">
        <div>
            <h1 class="main-title">📄 Resume Screener</h1>
            <p class="subtitle">AI-powered candidate matching and ranking system</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Job Description Section
# ---------------------------------------------------------
st.markdown("<div class='section-header'>💼 Job Description</div>", unsafe_allow_html=True)

# Sample JD text loading helper
sample_jd_content = ""
if os.path.exists("sample_jd.txt"):
    try:
        with open("sample_jd.txt", "r", encoding="utf-8") as f:
            sample_jd_content = f.read()
    except Exception as e:
        sample_jd_content = f"Error loading sample job description: {e}"

# Streamlit session state for managing JD input value
if "jd_input" not in st.session_state:
    st.session_state.jd_input = ""

# Button to load sample
col_btn, col_placeholder = st.columns([1, 4])
with col_btn:
    load_sample_jd = st.button("📝 Load Sample", use_container_width=True)

if load_sample_jd:
    st.session_state.jd_input = sample_jd_content

jd_text = st.text_area(
    label="Paste the Job Description",
    value=st.session_state.jd_input,
    height=220,
    placeholder="Paste detailed requirements here...\n\nInclude:\n• Core responsibilities\n• Required skills & technologies\n• Experience level\n• Nice-to-have qualifications",
    label_visibility="collapsed"
)

# Synchronize session state
st.session_state.jd_input = jd_text

# Trigger analysis button
st.markdown("")  # Spacing
col_btn_screen, col_info = st.columns([2, 3])
with col_btn_screen:
    screen_clicked = st.button("🔍 Screen & Match Resumes", type="primary", use_container_width=True)

with col_info:
    st.info("💡 Analyzing skills, experience, and keyword alignment", icon="ℹ️")

# ---------------------------------------------------------
# Resume Analysis Logic
# ---------------------------------------------------------
if screen_clicked:
    # 1. Validation
    if not jd_text.strip():
        st.error("⚠️ Please provide a job description first!")
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
            st.error("⚠️ Sample resumes directory not found! Try uploading files manually.")
            st.stop()

    # Load uploaded files
    if uploaded_files:
        for uf in uploaded_files:
            files_to_process.append({
                "name": uf.name,
                "stream": io.BytesIO(uf.getvalue())
            })
            
    if not files_to_process:
        st.error("⚠️ No resumes found! Please upload resumes or toggle 'Use Sample Resumes'.")
        st.stop()
        
    # 2. Run Parsing and Matching
    results = []
    skipped_files = []
    
    with st.spinner("🔄 Processing resumes, extracting text, and scoring matches..."):
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
    st.markdown("<div class='section-header'>🎯 Screening Results & Ranking</div>", unsafe_allow_html=True)
    
    # Display any skipped files with errors
    if skipped_files:
        for sf_name, error_msg in skipped_files:
            st.warning(f"⚠️ **{sf_name}** — {error_msg}")
            
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
                help="Weighted: 70% TF-IDF Similarity + 30% Skill Overlap",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        },
        hide_index=True
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
        mime="text/csv",
        use_container_width=True
    )
    
    # 4. Pool Insights & Missing Skills
    st.markdown("---")
    st.markdown("<div class='section-header'>📊 Pool Analytics</div>", unsafe_allow_html=True)
    
    col_insights, col_missing = st.columns([1, 1])
    
    with col_insights:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        avg_score = df_results["Match Score (%)"].mean()
        high_matches = sum(1 for r in results if r["Verdict"] == "High Match")
        med_matches = sum(1 for r in results if r["Verdict"] == "Medium Match")
        low_matches = sum(1 for r in results if r["Verdict"] == "Low Match")
        
        st.markdown(f"<h3 style='margin: 0 0 1rem 0; color: var(--text-secondary); font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>Applicant Pool Overview</h3>", unsafe_allow_html=True)
        
        st.metric("Average Match Score", f"{avg_score:.1f}%")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("🟢 High", high_matches)
        col_m2.metric("🟡 Medium", med_matches)
        col_m3.metric("🔴 Low", low_matches)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_missing:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 0 0 1rem 0; color: var(--text-secondary); font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>Top Missing Skills</h3>", unsafe_allow_html=True)
        
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
                st.markdown(f"🔴 **{skill.title()}** — {percentage:.0f}% of pool")
        else:
            st.success("✅ All job requirements covered!")
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 5. Score Visualization
    st.markdown("---")
    st.markdown("<div class='section-header'>📈 Match Distribution</div>", unsafe_allow_html=True)
    
    # Create simple visualization using streamlit bar chart
    df_chart = df_results[["Candidate / Filename", "Match Score (%)", "Cosine Similarity (%)", "Keyword Overlap (%)"]].copy()
    st.bar_chart(df_chart, x="Candidate / Filename", y=["Match Score (%)", "Cosine Similarity (%)", "Keyword Overlap (%)"], use_container_width=True)
    
    # 6. Detailed Candidate Profiles
    st.markdown("---")
    st.markdown("<div class='section-header'>👥 Detailed Candidate Profiles</div>", unsafe_allow_html=True)
    
    for idx, candidate in enumerate(sorted_results):
        # Color formatting for verdict pill
        verdict_class = "verdict-low"
        if candidate["Verdict"] == "High Match":
            verdict_class = "verdict-high"
        elif candidate["Verdict"] == "Medium Match":
            verdict_class = "verdict-medium"
            
        rank_badge = f"<span style='display: inline-block; background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-light) 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 700; font-size: 0.85rem; margin-right: 0.5rem;'>#{idx + 1}</span>"
        score_display = f"<span style='font-weight: 700; color: var(--accent-color); font-size: 1.1rem;'>{candidate['Match Score (%)']:.1f}%</span>"
        
        header_text = f"{rank_badge} {candidate['Candidate / Filename']}"
        
        with st.expander(header_text, expanded=(idx == 0)):
            # Layout columns inside candidate profile
            c_col1, c_col2 = st.columns([1, 1])
            
            with c_col1:
                st.markdown("### 📞 Contact Information")
                st.markdown(f"📧 **Email:** `{candidate['Email']}`" if candidate['Email'] else "📧 **Email:** _Not found_")
                st.markdown(f"📱 **Phone:** `{candidate['Phone']}`" if candidate['Phone'] else "📱 **Phone:** _Not found_")
                
                st.markdown("### 📐 Match Metrics")
                metric_col1, metric_col2 = st.columns(2)
                
                with metric_col1:
                    st.metric(
                        "TF-IDF Similarity",
                        f"{candidate['Cosine Similarity (%)']}%",
                        delta="70% weight"
                    )
                
                with metric_col2:
                    st.metric(
                        "Skill Overlap",
                        f"{candidate['Keyword Overlap (%)']}%",
                        delta="30% weight"
                    )
                
                # Display Verdict with Custom Colored Pill Style
                st.markdown(f"**Verdict:** <span class='{verdict_class}'>{candidate['Verdict']}</span>", unsafe_allow_html=True)
                
            with c_col2:
                # Skill breakdowns
                st.markdown("### 🛠️ Skills Analysis")
                
                tab_matched, tab_missing, tab_all = st.tabs(["✅ Matched", "❌ Missing", "📋 All"])
                
                with tab_matched:
                    if candidate["Matched Skills"]:
                        skill_html = " ".join([f"<span class='skill-tag'>{s.title()}</span>" for s in candidate["Matched Skills"]])
                        st.markdown(skill_html, unsafe_allow_html=True)
                    else:
                        st.info("No matching predefined skills found.")
                        
                with tab_missing:
                    if candidate["Missing Skills"]:
                        skill_html = " ".join([f"<span class='skill-tag-missing'>{s.title()}</span>" for s in candidate["Missing Skills"]])
                        st.markdown(skill_html, unsafe_allow_html=True)
                    else:
                        st.success("No missing skills! Candidate covers all requirements.")
                        
                with tab_all:
                    if candidate["All Resume Skills"]:
                        all_skills_text = ", ".join([s.title() for s in candidate["All Resume Skills"]])
                        st.markdown(all_skills_text)
                    else:
                        st.info("No predefined skills detected.")
                        
            # Raw Text view option
            st.markdown("---")
            with st.expander("📄 View Extracted Resume Text"):
                st.code(candidate["raw_text"], language="text")

else:
    # Friendly state if no analysis has been run
    st.markdown("---")
    st.info(
        "👋 **Welcome to Resume Screener!**\n\n"
        "1. Paste a job description above\n"
        "2. Upload resumes or use sample data\n"
        "3. Click 'Screen & Match Resumes' to see results",
        icon="ℹ️"
    )
