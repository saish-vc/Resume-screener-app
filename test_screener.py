import io
import os
from parser import parse_resume
from matcher import calculate_match_score

def test_resume_screener():
    print("🧪 Running Automated Resume Screener Validation...")
    
    # 1. Load Sample Job Description
    assert os.path.exists("sample_jd.txt"), "sample_jd.txt is missing"
    with open("sample_jd.txt", "r", encoding="utf-8") as f:
        jd_text = f.read()
    print("✅ Sample Job Description loaded successfully.")
    
    # 2. Test Parser and Matcher for Jane Smith (TXT Resume)
    jane_path = os.path.join("sample_resumes", "jane_smith_resume.txt")
    assert os.path.exists(jane_path), "Jane Smith resume is missing"
    with open(jane_path, "rb") as f:
        jane_bytes = f.read()
        jane_stream = io.BytesIO(jane_bytes)
    
    jane_text = parse_resume(jane_stream, "jane_smith_resume.txt")
    assert "JANE SMITH" in jane_text, "Failed to parse content from Jane Smith resume"
    print("✅ Parser successfully extracted text from Jane Smith (TXT).")
    
    jane_results = calculate_match_score(jane_text, jd_text)
    print(f"   Jane Smith final score: {jane_results['final_score']}% ({jane_results['verdict']})")
    assert "final_score" in jane_results, "Missing final_score in matching results"
    assert "verdict" in jane_results, "Missing verdict in matching results"
    print("✅ Matcher successfully processed Jane Smith.")
    
    # 3. Test Parser and Matcher for John Doe (DOCX Resume)
    john_path = os.path.join("sample_resumes", "john_doe_resume.docx")
    assert os.path.exists(john_path), "John Doe resume is missing"
    with open(john_path, "rb") as f:
        john_bytes = f.read()
        john_stream = io.BytesIO(john_bytes)
        
    john_text = parse_resume(john_stream, "john_doe_resume.docx")
    assert "JOHN DOE" in john_text, "Failed to parse content from John Doe resume"
    print("✅ Parser successfully extracted text from John Doe (DOCX).")
    
    john_results = calculate_match_score(john_text, jd_text)
    print(f"   John Doe final score: {john_results['final_score']}% ({john_results['verdict']})")
    assert john_results['final_score'] > jane_results['final_score'], "John Doe's match score should be higher than Jane Smith's"
    print("✅ Matcher successfully processed John Doe and verified ranking.")
    
    # 4. Test Parser and Matcher for Bob Johnson (DOCX Resume)
    bob_path = os.path.join("sample_resumes", "bob_johnson_resume.docx")
    assert os.path.exists(bob_path), "Bob Johnson resume is missing"
    with open(bob_path, "rb") as f:
        bob_bytes = f.read()
        bob_stream = io.BytesIO(bob_bytes)
        
    bob_text = parse_resume(bob_stream, "bob_johnson_resume.docx")
    assert "BOB JOHNSON" in bob_text, "Failed to parse content from Bob Johnson resume"
    print("✅ Parser successfully extracted text from Bob Johnson (DOCX).")
    
    bob_results = calculate_match_score(bob_text, jd_text)
    print(f"   Bob Johnson final score: {bob_results['final_score']}% ({bob_results['verdict']})")
    assert bob_results['final_score'] < jane_results['final_score'], "Bob Johnson's match score should be lower than Jane Smith's"
    print("✅ Matcher successfully processed Bob Johnson and verified ranking.")
    
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! The parser, matcher, and scoring engine are in perfect shape.")

if __name__ == "__main__":
    test_resume_screener()
