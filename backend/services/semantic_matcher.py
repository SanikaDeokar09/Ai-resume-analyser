
import re

from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None
SentenceTransformer = None


# --------------------------------
# MODEL LOADING
# --------------------------------

def get_model():
    global _model, SentenceTransformer

    if _model is None:
        if SentenceTransformer is None:
            from sentence_transformers import SentenceTransformer as ST
            SentenceTransformer = ST

        _model = SentenceTransformer(MODEL_NAME)

    return _model


# --------------------------------
# TEXT CLEANING
# --------------------------------

def clean_text(text):
    text = re.sub(r"\s+", " ", str(text or ""))
    return text.strip()


# --------------------------------
# RESUME SECTION EXTRACTION
# --------------------------------

SECTION_PATTERNS = {
    "Skills": [
        "technical skills",
        "skills",
        "core competencies",
        "technologies"
    ],
    "Experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "internship"
    ],
    "Projects": [
        "projects",
        "academic projects",
        "personal projects",
        "key projects"
    ],
    "Education": [
        "education",
        "academic background",
        "qualifications"
    ],
    "Certifications": [
        "certifications",
        "certificates",
        "courses"
    ],
    "Achievements": [
        "achievements",
        "accomplishments",
        "awards"
    ]
}


def extract_resume_sections(text):
    lines = str(text or "").splitlines()

    sections = {"General": []}
    current_section = "General"

    for line in lines:
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        normalized = re.sub(
            r"[^a-zA-Z ]",
            "",
            cleaned_line
        ).strip().lower()

        detected_section = None

        for section, headings in SECTION_PATTERNS.items():
            if normalized in headings:
                detected_section = section
                break

        if detected_section:
            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(cleaned_line)

    return {
        section: "\n".join(content).strip()
        for section, content in sections.items()
        if content
    }


# --------------------------------
# JOB REQUIREMENT EXTRACTION
# --------------------------------

def extract_job_requirements(job_description):

    text = str(job_description or "")

    sentences = re.split(
        r"(?<=[.!?])\s+|[\n•]+",
        text
    )

    requirements = []

    for sentence in sentences:
        sentence = sentence.strip(" -*\t")

        if len(sentence.split()) >= 3:
            requirements.append(sentence)

    return list(dict.fromkeys(requirements))


# --------------------------------
# SKILL MATCHING
# --------------------------------

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


def find_skills(text, skill_database):

    found_skills = set()
    text = normalize_skill_text(text)

    for skills in skill_database.values():

        for skill in skills:

            pattern = (
                r"(?<![A-Za-z0-9+#])"
                + re.escape(skill)
                + r"(?![A-Za-z0-9+#])"
            )

            if re.search(pattern, text, re.IGNORECASE):
                found_skills.add(skill)

    # Expand AI and ML abbreviations independently
    if re.search(r"(?<![A-Za-z0-9+#])AI(?![A-Za-z0-9+#])", text, re.IGNORECASE):
        found_skills.add("Artificial Intelligence")

    if re.search(r"(?<![A-Za-z0-9+#])ML(?![A-Za-z0-9+#])", text, re.IGNORECASE):
        found_skills.add("Machine Learning")

    return found_skills


# Equivalent names are compared through a shared canonical label.
# This prevents LLMs and Large Language Models from being treated as different skills.
SKILL_ALIASES = {
    "large language models": "llms",
    "large language model": "llms",
    "llm": "llms",
    "llms": "llms",
    "artificial intelligence": "artificial intelligence",
    "ai": "artificial intelligence",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "react.js": "react",
    "reactjs": "react",
    "node.js": "node.js",
    "nodejs": "node.js",
    "express.js": "express",
    "expressjs": "express",
    "rest apis": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "html5": "html",
    "css3": "css",
}


def canonical_skill(skill):
    key = re.sub(r"\s+", " ", str(skill or "").strip().lower())
    return SKILL_ALIASES.get(key, key)


def skills_intersection(resume_skills, job_skills):
    resume_by_key = {canonical_skill(skill): skill for skill in resume_skills}
    job_by_key = {canonical_skill(skill): skill for skill in job_skills}
    shared = set(resume_by_key).intersection(job_by_key)
    # Return the JD's spelling so the result aligns with the requirement wording.
    return {job_by_key[key] for key in shared}


def extract_job_skills(job_description, skill_database):
    return sorted(find_skills(job_description, skill_database))


# --------------------------------
# REQUIREMENT CLASSIFICATION
# --------------------------------

PREFERRED_CUES = [
    "preferred",
    "preferably",
    "desirable",
    "desired",
    "a plus",
    "big plus",
    "good to have",
    "nice to have",
    "bonus",
    "advantage",
    "added advantage",
    "additional skills",
    "would be beneficial"
]


RESPONSIBILITY_CUES = [
    "responsibilities",
    "key responsibilities",
    "job description",
    "you will",
    "responsible for",
    "duties include"
]


SOFT_SKILL_TERMS = [
    "communication",
    "communication skills",
    "teamwork",
    "collaboration",
    "problem-solving",
    "analytical thinking",
    "leadership",
    "adaptability",
    "self-motivated",
    "independent working"
]


def get_skill_category(skill, job_description):

    text = str(job_description or "")

    skill_pattern = (
        r"(?<![A-Za-z0-9+#])"
        + re.escape(skill)
        + r"(?![A-Za-z0-9+#])"
    )

    # Classify using the skill's own sentence/bullet, rather than a wide
    # character window that can accidentally borrow a cue from another skill.
    units = re.split(r"(?<=[.!?])\s+|[\n•]+", text)

    for unit in units:
        if not re.search(skill_pattern, unit, re.IGNORECASE):
            continue

        normalized = unit.lower()
        if any(cue in normalized for cue in PREFERRED_CUES):
            return "preferred"

    return "mandatory"


def classify_job_skills(job_description, skill_database):

    all_skills = find_skills(
        job_description,
        skill_database
    )

    mandatory_skills = set()
    preferred_skills = set()

    for skill in all_skills:

        category = get_skill_category(
            skill,
            job_description
        )

        if category == "preferred":
            preferred_skills.add(skill)
        else:
            mandatory_skills.add(skill)

    return {
        "mandatory_skills": sorted(mandatory_skills),
        "preferred_skills": sorted(preferred_skills),
        "all_skills": sorted(all_skills)
    }


def extract_soft_skills(job_description):

    text = str(job_description or "").lower()

    return sorted({
        skill
        for skill in SOFT_SKILL_TERMS
        if skill in text
    })


def extract_responsibilities(job_description):

    sentences = extract_job_requirements(job_description)

    results = []

    for sentence in sentences:

        lower_sentence = sentence.lower()

        if any(
            cue in lower_sentence
            for cue in RESPONSIBILITY_CUES
        ):
            results.append(sentence)

    return results


# --------------------------------
# SEMANTIC SIMILARITY
# --------------------------------

def calculate_similarity(resume_text, job_description):

    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    if not resume_text or not job_description:
        raise ValueError(
            "Resume and job description cannot be empty."
        )

    model = get_model()

    embeddings = model.encode(
        [resume_text, job_description],
        normalize_embeddings=True
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    score = round(
        float(similarity) * 100,
        2
    )

    return {
        "semantic_similarity": score,
        "model": MODEL_NAME
    }


# --------------------------------
# SECTION-WISE RELEVANCE
# --------------------------------

def analyze_section_relevance(resume_text, job_description):

    sections = extract_resume_sections(resume_text)

    requirements = extract_job_requirements(
        job_description
    )

    if not sections or not requirements:
        return []

    section_names = list(sections.keys())
    section_texts = list(sections.values())

    model = get_model()

    section_embeddings = model.encode(
        section_texts,
        normalize_embeddings=True
    )

    requirement_embeddings = model.encode(
        requirements,
        normalize_embeddings=True
    )

    similarity_matrix = cosine_similarity(
        requirement_embeddings,
        section_embeddings
    )

    results = []

    for index, requirement in enumerate(requirements):

        best_index = int(
            similarity_matrix[index].argmax()
        )

        similarity = float(
            similarity_matrix[index][best_index]
        )

        results.append({
            "job_requirement": requirement,
            "matched_resume_section": section_names[best_index],
            "resume_evidence": section_texts[best_index],
            "similarity": round(
                similarity * 100,
                2
            )
        })

    return results


# --------------------------------
# COMPLETE JOB MATCH ANALYSIS
# --------------------------------

def analyze_job_match(
    resume_text,
    job_description,
    skill_database
):

    # Keep original line breaks for heading, bullet, and requirement parsing.
    # Use cleaned copies only where a compact text representation is needed.
    raw_resume_text = str(resume_text or "").strip()
    raw_job_description = str(job_description or "").strip()

    resume_text = clean_text(raw_resume_text)
    job_description = clean_text(raw_job_description)

    if not resume_text or not job_description:
        raise ValueError(
            "Resume and job description cannot be empty."
        )

    # Semantic similarity

    semantic_result = calculate_similarity(
        resume_text,
        job_description
    )

    # Resume skills

    resume_skills = find_skills(
        raw_resume_text,
        skill_database
    )

    # Classify job requirements

    classification = classify_job_skills(
        raw_job_description,
        skill_database
    )

    mandatory_skills = set(
        classification["mandatory_skills"]
    )

    preferred_skills = set(
        classification["preferred_skills"]
    )

    all_job_skills = set(
        classification["all_skills"]
    )

    # Mandatory skill matching

    matched_mandatory = sorted(
        skills_intersection(resume_skills, mandatory_skills)
    )

    matched_mandatory_keys = {canonical_skill(x) for x in matched_mandatory}
    missing_mandatory = sorted(
        skill for skill in mandatory_skills
        if canonical_skill(skill) not in matched_mandatory_keys
    )

    # Preferred skill matching

    matched_preferred = sorted(
        skills_intersection(resume_skills, preferred_skills)
    )

    matched_preferred_keys = {canonical_skill(x) for x in matched_preferred}
    missing_preferred = sorted(
        skill for skill in preferred_skills
        if canonical_skill(skill) not in matched_preferred_keys
    )

    # Overall skill matching

    matched_skills = sorted(
        skills_intersection(resume_skills, all_job_skills)
    )

    matched_skill_keys = {canonical_skill(x) for x in matched_skills}
    missing_skills = sorted(
        skill for skill in all_job_skills
        if canonical_skill(skill) not in matched_skill_keys
    )

    # Mandatory coverage

    if mandatory_skills:

        mandatory_match_percentage = round(
            len(matched_mandatory)
            / len(mandatory_skills)
            * 100,
            2
        )

    else:
        mandatory_match_percentage = None

    # Preferred coverage

    if preferred_skills:

        preferred_match_percentage = round(
            len(matched_preferred)
            / len(preferred_skills)
            * 100,
            2
        )

    else:
        preferred_match_percentage = None

    # Overall skill coverage

    if all_job_skills:

        overall_skill_match_percentage = round(
            len(matched_skills)
            / len(all_job_skills)
            * 100,
            2
        )

    else:
        overall_skill_match_percentage = None

    # Section relevance

    section_relevance = analyze_section_relevance(
        raw_resume_text,
        raw_job_description
    )

    if section_relevance:

        average_section_relevance = round(
            sum(
                item["similarity"]
                for item in section_relevance
            ) / len(section_relevance),
            2
        )

    else:
        average_section_relevance = 0

    # Soft skills and responsibilities

    soft_skills = extract_soft_skills(
        raw_job_description
    )

    responsibilities = extract_responsibilities(
        raw_job_description
    )

    matched_soft_skills = sorted(
        skill
        for skill in soft_skills
        if skill.lower() in resume_text.lower()
    )

    missing_soft_skills = sorted(
        set(soft_skills) - set(matched_soft_skills)
    )

    # --------------------------------
    # WEIGHTED JOB COMPATIBILITY SCORE
    # --------------------------------

    mandatory_score = (
        mandatory_match_percentage
        if mandatory_match_percentage is not None
        else 0
    )

    preferred_score = (
        preferred_match_percentage
        if preferred_match_percentage is not None
        else 0
    )

    semantic_score = semantic_result["semantic_similarity"]

    if mandatory_skills and preferred_skills:
        compatibility_score = round(
            (mandatory_score * 0.50)
            + (preferred_score * 0.15)
            + (semantic_score * 0.35),
            2
        )

    elif mandatory_skills:
        compatibility_score = round(
            (mandatory_score * 0.65)
            + (semantic_score * 0.35),
            2
        )

    elif preferred_skills:
        compatibility_score = round(
            (preferred_score * 0.35)
            + (semantic_score * 0.65),
            2
        )

    else:
        compatibility_score = round(semantic_score, 2)

    # Return compatible and expanded API fields

    return {
        **semantic_result,

        "match_percentage": compatibility_score,
        "compatibility_score": compatibility_score,

        "required_skills": sorted(mandatory_skills),

        "mandatory_skills": sorted(mandatory_skills),

        "preferred_skills": sorted(preferred_skills),

        "all_job_skills": sorted(all_job_skills),

        "matched_skills": matched_skills,

        "matching_skills": matched_skills,

        "missing_skills": missing_skills,

        "matched_mandatory_skills": matched_mandatory,

        "missing_mandatory_skills": missing_mandatory,

        "matched_preferred_skills": matched_preferred,

        "missing_preferred_skills": missing_preferred,

        "skill_match_percentage": overall_skill_match_percentage,

        "mandatory_match_percentage": mandatory_match_percentage,

        "preferred_match_percentage": preferred_match_percentage,

        "overall_skill_match_percentage": overall_skill_match_percentage,

        "soft_skills": soft_skills,

        "matched_soft_skills": matched_soft_skills,

        "missing_soft_skills": missing_soft_skills,

        "responsibilities": responsibilities,

        "section_relevance": section_relevance,

        "average_section_relevance": average_section_relevance,

        "matching_method": (
            "Sentence Transformers + "
            "Section-Aware Similarity + "
            "Mandatory and Preferred Skill Classification"
        )
    }