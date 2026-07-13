import re
import string

# Comprehensive list of predefined technical and professional skills
PREDEFINED_SKILLS = {
    # Programming Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "ruby", "php", "go", "rust", 
    "swift", "kotlin", "scala", "r", "sql", "html", "css", "bash", "shell", "powershell",
    
    # Frameworks & Libraries
    "django", "flask", "fastapi", "react", "angular", "vue", "node.js", "next.js", "express", 
    "spring boot", "laravel", "rails", "asp.net", "jquery", "bootstrap", "tailwind", "pandas", 
    "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "spark", "hadoop",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "gitlab", "jenkins", 
    "ansible", "terraform", "ci/cd", "linux", "nginx", "apache", "prometheus", "grafana",
    
    # Databases & Tools
    "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "elasticsearch", "cassandra",
    
    # Methodologies & Concepts
    "agile", "scrum", "devops", "machine learning", "deep learning", "nlp", "computer vision", 
    "data science", "api", "rest api", "graphql", "microservices", "testing", "unit testing", 
    "integration testing", "system architecture", "oop", "object-oriented",
    
    # Soft & Professional Skills
    "communication", "leadership", "teamwork", "problem solving", "analytical", "project management",
    "scrum master", "product management", "collaboration", "presentation", "negotiation", "creativity"
}

def clean_text(text: str) -> str:
    """
    Cleans raw text by converting to lowercase, removing special characters 
    (while retaining c++, c#, .net), and removing extra whitespace.
    """
    if not text:
        return ""
    # Lowercase
    text = text.lower()
    
    # Replace newlines and tabs with spaces
    text = re.sub(r'[\r\n\t]+', ' ', text)
    
    # Custom cleaning to keep skill characters like #, +, .
    # Retain letters, numbers, spaces, and '+', '#', '.'
    text = re.sub(r'[^a-z0-9\s\+#\.]', ' ', text)
    
    # Normalize multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_contact_info(text: str) -> dict:
    """
    Extracts email and a standard phone number pattern from text using regular expressions.
    """
    info = {"email": "Not Found", "phone": "Not Found"}
    if not text:
        return info
    
    # Email regex
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, text)
    if emails:
        info["email"] = emails[0].strip()
        
    # Phone number regex: matches various formats like (123) 456-7890, 123-456-7890, +1-123-456-7890, etc.
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    if phones:
        info["phone"] = phones[0].strip()
        
    return info

def extract_skills_from_text(text: str) -> set:
    """
    Extracts skills that are present in both the text and the PREDEFINED_SKILLS set.
    """
    cleaned_text = clean_text(text)
    # Tokenize by splitting on spaces and removing punctuation around words
    words = cleaned_text.split()
    
    found_skills = set()
    
    # Match exact skills in PREDEFINED_SKILLS
    for skill in PREDEFINED_SKILLS:
        # Match word boundaries for skills to prevent partial matches 
        # (e.g. "go" in "django" or "aws" in "awesome")
        # Handle skills with special characters safely
        escaped_skill = re.escape(skill)
        
        # Define boundary conditions. If skill starts or ends with a special char (+, #, .),
        # standard \b word boundaries might fail, so we handle it programmatically or with custom regex boundaries.
        pattern = rf'(?:^|[\s,.\(\)\/]){escaped_skill}(?:$|[\s,.\(\)\/])'
        if re.search(pattern, cleaned_text):
            found_skills.add(skill)
            
    return found_skills
