from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import clean_text, extract_skills_from_text

def calculate_match_score(resume_text: str, jd_text: str) -> dict:
    """
    Compares resume text and job description text to calculate:
    1. TF-IDF + Cosine Similarity (70% weight)
    2. Key skill overlap coverage (30% weight)
    
    Returns a dictionary of detailed results including individual scores,
    matched keywords, missing keywords, and a final verdict.
    """
    # Clean the input texts
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(jd_text)
    
    # 1. Cosine Similarity via TF-IDF
    cosine_sim_percentage = 0.0
    if cleaned_resume and cleaned_jd:
        try:
            # We use English stop words provided by scikit-learn
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([cleaned_jd, cleaned_resume])
            sim_value = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            cosine_sim_percentage = float(sim_value * 100.0)
        except ValueError:
            # Handle cases where vocabulary is empty (e.g., only stop words or special chars)
            cosine_sim_percentage = 0.0
            
    # 2. Key Skill Overlap (using our predefined skills set)
    jd_skills = extract_skills_from_text(jd_text)
    resume_skills = extract_skills_from_text(resume_text)
    
    matched_skills = jd_skills.intersection(resume_skills)
    missing_skills = jd_skills.difference(resume_skills)
    
    # Keyword coverage score
    if not jd_skills:
        # If no predefined skills are found in the JD, default to 100% to avoid division by zero
        # or penalizing candidates unfairly.
        keyword_coverage = 100.0
    else:
        keyword_coverage = float((len(matched_skills) / len(jd_skills)) * 100.0)
        
    # 3. Final Combined Score (70% Cosine Similarity + 30% Keyword Coverage)
    final_score = (0.7 * cosine_sim_percentage) + (0.3 * keyword_coverage)
    
    # 4. Generate short verdict based on final score
    if final_score >= 50.0:
        verdict = "High Match"
    elif final_score >= 30.0:
        verdict = "Medium Match"
    else:
        verdict = "Low Match"
        
    return {
        "cosine_similarity": round(cosine_sim_percentage, 1),
        "keyword_coverage": round(keyword_coverage, 1),
        "final_score": round(final_score, 1),
        "matched_skills": sorted(list(matched_skills)),
        "missing_skills": sorted(list(missing_skills)),
        "all_resume_skills": sorted(list(resume_skills)),
        "verdict": verdict
    }
