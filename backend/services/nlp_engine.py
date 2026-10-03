
import spacy
import re
from collections import Counter

# Load English NLP model
nlp = spacy.load("en_core_web_sm")


SKILL_KEYWORDS = [
    "Python", "Java", "C++", "C", "JavaScript", "TypeScript",
    "PHP", "SQL", "HTML", "CSS", "React", "Node.js",
    "Express", "Flask", "Django", "REST API",
    "Machine Learning", "Deep Learning",
    "Artificial Intelligence", "NLP",
    "TensorFlow", "PyTorch", "Scikit-learn",
    "Pandas", "NumPy", "Matplotlib",
    "Data Analysis", "Generative AI",
    "MySQL", "MongoDB", "PostgreSQL",
    "SQLite", "Redis", "Git", "GitHub",
    "Docker", "AWS", "Power BI", "Tableau",
    "Linux", "Communication", "Leadership",
    "Problem Solving", "Teamwork"
]


def preprocess_text(text):
    """Clean and normalize resume text."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s@.+#/-]", " ", text)
    return text.strip()


def extract_entities(text):
    """Extract named entities from resume."""
    doc = nlp(text)

    entities = {
        "PERSON": [],
        "ORG": [],
        "GPE": [],
        "DATE": [],
        "PRODUCT": []
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            if ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)

    return entities


def extract_skills(text):
    """Extract skills from resume."""
    found = []

    for skill in SKILL_KEYWORDS:
        pattern = (
            r"(?<![A-Za-z0-9+#])"
            + re.escape(skill)
            + r"(?![A-Za-z0-9+#])"
        )

        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)

    return found


def extract_keywords(text, top_n=15):
    """Extract frequent meaningful keywords."""
    doc = nlp(preprocess_text(text))

    keywords = {}

    for token in doc:
        if (
            token.is_alpha
            and not token.is_stop
            and len(token.text) > 2
            and token.pos_ in ["NOUN", "PROPN", "ADJ"]
        ):
            word = token.lemma_.lower()
            keywords[word] = keywords.get(word, 0) + 1

    sorted_keywords = sorted(
        keywords.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return [
        {"keyword": word, "frequency": count}
        for word, count in sorted_keywords[:top_n]
    ]


def extract_resume_sections(text):
    """Identify common resume sections."""
    section_patterns = {
        "education": r"education|academic background|qualifications",
        "experience": r"experience|work history|employment|internship",
        "projects": r"projects|academic projects|personal projects",
        "certifications": r"certifications|certificates",
        "achievements": r"achievements|accomplishments",
        "skills": r"technical skills|skills|core competencies"
    }

    detected = []

    for section, pattern in section_patterns.items():
        if re.search(
            r"(?im)^\s*(?:" + pattern + r")\s*:?\s*$",
            text
        ):
            detected.append(section)

    return detected


def generate_strengths(skills, sections):
    """Generate rule-based resume strengths."""
    strengths = []

    if skills:
        strengths.append(
            f"Resume demonstrates {len(skills)} identifiable skills."
        )

    if "projects" in sections:
        strengths.append(
            "Projects section is present."
        )

    if "experience" in sections:
        strengths.append(
            "Experience or internship section is present."
        )

    if "education" in sections:
        strengths.append(
            "Educational background is included."
        )

    if "certifications" in sections:
        strengths.append(
            "Certifications section is present."
        )

    return strengths


def generate_recommendations(skills, sections):
    """Generate rule-based resume improvement suggestions."""
    recommendations = []

    if not skills:
        recommendations.append(
            "Add a clearly structured technical skills section."
        )

    if "projects" not in sections:
        recommendations.append(
            "Include relevant projects and describe your contributions."
        )

    if "experience" not in sections:
        recommendations.append(
            "Include relevant internship or practical experience if available."
        )

    if "certifications" not in sections:
        recommendations.append(
            "Add relevant certifications if completed."
        )

    recommendations.append(
        "Use action verbs and measurable achievements in project descriptions."
    )

    recommendations.append(
        "Tailor skills and keywords to the target job description."
    )

    return recommendations


def analyze_text(text):
    """Run the complete NLP pipeline on resume text."""

    cleaned_text = preprocess_text(text)

    entities = extract_entities(text)
    keywords = extract_keywords(text)
    skills = extract_skills(text)
    sections = extract_resume_sections(text)

    doc = nlp(text)

    strengths = generate_strengths(skills, sections)
    recommendations = generate_recommendations(skills, sections)

    return {
        "entities": entities,
        "keywords": keywords,

        "skills": skills,
        "detected_skills": skills,
        "total_skills": len(skills),

        "sections_detected": sections,

        "strengths": strengths,
        "recommendations": recommendations,

        "sentences": len(list(doc.sents)),
        "tokens": len([token for token in doc if not token.is_space]),
        "cleaned_text": cleaned_text
    }