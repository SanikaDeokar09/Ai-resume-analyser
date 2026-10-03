import re

SKILL_DATABASE = {
    "Programming Languages": [
        "Python", "Java", "C++", "C", "JavaScript",
        "TypeScript", "PHP", "R", "SQL"
    ],
    "Web Development": [
        "HTML", "CSS", "React", "Node.js", "Express",
        "Flask", "Django", "REST API", "Tailwind CSS",
        "FastAPI"
    ],
    "Data Science & AI": [
        "Machine Learning", "Deep Learning",
        "Artificial Intelligence", "NLP",
        "TensorFlow", "PyTorch", "Scikit-learn",
        "Pandas", "NumPy", "Matplotlib",
        "Data Analysis", "Generative AI",
        "RAG", "Vector Embeddings", "Large Language Models",
        "LLMs", "Ollama", "Knowledge Graphs",
        "Multi-Agent Systems"
    ],
    "Databases": [
        "MySQL", "MongoDB", "PostgreSQL",
        "SQLite", "Redis"
    ],
    "Tools & Platforms": [
        "Git", "GitHub", "Docker", "AWS",
        "Power BI", "Tableau", "VS Code",
        "Linux", "Postman"
    ]
}

# Common equivalent names. Canonical names are returned in analysis.
SKILL_ALIASES = {
    "Python": ["python3"],
    "JavaScript": ["JS", "ECMAScript"],
    "TypeScript": ["TS"],
    "C++": ["cpp"],
    "SQL": ["Structured Query Language"],
    "HTML": ["HTML5"],
    "CSS": ["CSS3"],
    "React": ["React.js", "ReactJS"],
    "Node.js": ["Node", "NodeJS"],
    "Express": ["Express.js", "ExpressJS"],
    "REST API": ["REST APIs", "RESTful API", "RESTful APIs"],
    "Machine Learning": ["ML"],
    "Deep Learning": ["DL"],
    "Artificial Intelligence": ["AI"],
    "NLP": ["Natural Language Processing"],
    "Scikit-learn": ["sklearn", "scikit learn"],
    "PyTorch": ["torch"],
    "TensorFlow": ["tf"],
    "Pandas": ["pd"],
    "MongoDB": ["Mongo"],
    "PostgreSQL": ["Postgres"],
    "GitHub": ["Git Hub"],
    "Power BI": ["PowerBI"],
    "Tailwind CSS": ["Tailwind"],
    "FastAPI": ["Fast API"],
    "Vector Embeddings": ["Vector Embedding", "Embeddings"],
    "Large Language Models": ["Large Language Model"],
    "LLMs": ["LLM"],
    "Knowledge Graphs": ["Knowledge Graph"],
    "Multi-Agent Systems": ["Multi Agent Systems", "Multi-agent AI"]
}


def skill_pattern(skill):
    # Use boundaries that allow punctuation in names such as C++, Node.js.
    return (
        r"(?<![A-Za-z0-9+#])"
        + re.escape(skill)
        + r"(?![A-Za-z0-9+#])"
    )


def extract_email(text):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text or "")
    return match.group(0) if match else None


def extract_phone(text):
    pattern = r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
    match = re.search(pattern, text or "")
    return match.group(0) if match else None


def normalize_skill_text(text):
    """Separate common PDF-extracted skill headings from their first value."""
    text = str(text or "")
    heading_patterns = [
        r"Programming",
        r"Web Development",
        r"AI\s*/\s*ML",
        r"Backend\s*&\s*APIs",
        r"Databases",
        r"Tools",
        r"Soft Skills",
    ]

    for heading in heading_patterns:
        text = re.sub(
            rf"(?i)(?<![A-Za-z])({heading})\s*(?=[A-Z])",
            r"\1 ",
            text,
        )

    # Some PDF extractors join the "ML" in an "AI / ML" heading
    # directly to the following "LLMs" skill.
    text = re.sub(r"(?i)(AI\s*/\s*ML\s+)MLLMs\b", r"\1LLMs", text)
    return text


def extract_skills(text):
    text = normalize_skill_text(text)
    found_skills = {}

    for category, skills in SKILL_DATABASE.items():
        matched = []

        for skill in skills:
            variants = [skill] + SKILL_ALIASES.get(skill, [])

            if any(
                re.search(skill_pattern(variant), text, re.IGNORECASE)
                for variant in variants
            ):
                matched.append(skill)

        if matched:
            found_skills[category] = matched

    return found_skills


def extract_sections(text):
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
            text or ""
        ):
            detected.append(section)

    return detected


def generate_strengths(skills, sections, word_count):
    strengths = []

    if skills:
        strengths.append(
            f"Demonstrates technical skills across {len(skills)} skill categories."
        )

    if "projects" in sections:
        strengths.append(
            "Includes a projects section to showcase practical work."
        )

    if "experience" in sections:
        strengths.append("Includes an experience section.")

    if "education" in sections:
        strengths.append("Educational background is included.")

    if "certifications" in sections:
        strengths.append("Includes a certifications section.")

    if word_count >= 250:
        strengths.append("Contains substantial resume content.")

    if not strengths:
        strengths.append(
            "Resume text was extracted successfully and is ready for review."
        )

    return strengths


def generate_recommendations(skills, sections, word_count):
    recommendations = []

    if not skills:
        recommendations.append(
            "Add a clearly labeled Technical Skills section."
        )

    if "projects" not in sections:
        recommendations.append(
            "Add a Projects section with technologies and measurable outcomes."
        )

    if "experience" not in sections:
        recommendations.append(
            "Include relevant internship, work, or practical experience if available."
        )

    if "certifications" not in sections:
        recommendations.append(
            "Include relevant certifications if you have completed any."
        )

    if "achievements" not in sections:
        recommendations.append(
            "Add relevant achievements, awards, or measurable accomplishments."
        )

    if word_count < 250:
        recommendations.append(
            "Add more relevant details about projects, skills, and responsibilities."
        )

    recommendations.append(
        "Use action verbs and measurable results in project and experience descriptions."
    )

    return recommendations


def calculate_resume_score(text, skills, sections):
    score = 0
    breakdown = {}
    word_count = len(text.split())

    content_score = min(20, round(word_count / 30))
    breakdown["Content"] = content_score
    score += content_score

    skill_count = sum(len(items) for items in skills.values())
    skill_score = min(30, skill_count * 3)
    breakdown["Skills"] = skill_score
    score += skill_score

    section_score = min(30, len(sections) * 6)
    breakdown["Sections"] = section_score
    score += section_score

    contact_score = 0

    if extract_email(text):
        contact_score += 10

    if extract_phone(text):
        contact_score += 10

    breakdown["Contact Information"] = contact_score
    score += contact_score

    return min(100, score), breakdown


def analyze_resume(text):
    text = str(text or "")

    skills = extract_skills(text)
    sections = extract_sections(text)

    score, breakdown = calculate_resume_score(
        text,
        skills,
        sections
    )

    detected_skills = [
        skill
        for category_skills in skills.values()
        for skill in category_skills
    ]

    word_count = len(text.split())

    strengths = generate_strengths(
        skills,
        sections,
        word_count
    )

    recommendations = generate_recommendations(
        skills,
        sections,
        word_count
    )

    return {
        "contact": {
            "email": extract_email(text),
            "phone": extract_phone(text)
        },
        "skills": skills,
        "detected_skills": detected_skills,
        "total_skills": len(detected_skills),
        "sections_detected": sections,
        "strengths": strengths,
        "recommendations": recommendations,
        "score": score,
        "score_breakdown": breakdown,
        "word_count": word_count
    }
