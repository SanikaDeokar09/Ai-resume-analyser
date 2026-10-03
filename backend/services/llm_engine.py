
import os
import time
import random

from dotenv import load_dotenv
from google import genai

# --------------------------------
# ENVIRONMENT CONFIGURATION
# --------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Check backend/.env."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.8-flash"


# --------------------------------
# GEMINI RESPONSE GENERATION
# --------------------------------

def generate_ai_response(prompt, retries=3):

    for attempt in range(retries):

        try:
            print(
                f"Gemini request: attempt {attempt + 1}/{retries}"
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "temperature": 0.3,
                    "max_output_tokens": 4096,
                }
            )

            if response and response.text:

                generated_text = response.text.strip()

                print("Gemini response generated successfully.")

                if response.candidates:
                    candidate = response.candidates[0]

                    print(
                        "Gemini finish reason:",
                        candidate.finish_reason
                    )

                if response.usage_metadata:
                    print(
                        "Gemini token usage:",
                        response.usage_metadata
                    )

                print(
                    "AI explanation character count:",
                    len(generated_text)
                )

                print(
                    "AI explanation ending:",
                    generated_text[-300:]
                )

                return generated_text

            print("Gemini returned an empty response.")

            if attempt < retries - 1:
                time.sleep(2)
                continue

            return (
                "The AI service returned an empty response. "
                "Please try again."
            )

        except Exception as e:

            error_message = str(e)
            error_upper = error_message.upper()

            print(
                f"Gemini attempt {attempt + 1} failed: "
                f"{error_message}"
            )

            # --------------------------------
            # DAILY QUOTA EXHAUSTED
            # --------------------------------

            quota_exhausted = (
                "RESOURCE_EXHAUSTED" in error_upper
                or "QUOTA_EXCEEDED" in error_upper
                or (
                    "429" in error_upper
                    and (
                        "PER_DAY" in error_upper
                        or "DAILY" in error_upper
                        or "GENERATE_CONTENT_FREE_TIER_REQUESTS"
                        in error_upper
                    )
                )
            )

            if quota_exhausted:

                print(
                    "Gemini quota exhausted. "
                    "Stopping retries."
                )

                return (
                    "AI explanation is temporarily unavailable "
                    "because the Gemini API quota has been reached. "
                    "Your semantic matching, ATS score, and skill "
                    "analysis are still available. Please try again "
                    "after the quota resets."
                )

            # --------------------------------
            # TEMPORARY ERRORS
            # --------------------------------

            temporary_error = any(
                code in error_upper
                for code in [
                    "429",
                    "503",
                    "UNAVAILABLE",
                    "500",
                    "INTERNAL",
                    "TIMEOUT",
                    "DEADLINE_EXCEEDED",
                    "502",
                    "504"
                ]
            )

            if temporary_error and attempt < retries - 1:

                wait_time = min(
                    2 ** (attempt + 1)
                    + random.uniform(0, 1),
                    10
                )

                print(
                    f"Temporary Gemini failure. "
                    f"Retrying in {wait_time:.1f} seconds..."
                )

                time.sleep(wait_time)
                continue

            return (
                "AI explanation is temporarily unavailable. "
                "Your semantic matching and skill analysis "
                "are still available. Please try again later."
            )

    return "AI explanation could not be generated."


# --------------------------------
# RESUME EXPLANATION
# --------------------------------

def generate_resume_explanation(
    resume_text,
    job_description,
    retrieved_context
):

    prompt = f"""
You are an advanced AI-powered resume analysis
and career matching assistant.

Analyze the candidate's resume against the
provided job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

RETRIEVED RESUME EVIDENCE:
{retrieved_context}

Generate a detailed, evidence-based report
using the following 9 sections.

# 1. Overall Candidate Assessment

Explain the candidate's overall suitability
for the given job role.

Discuss:
- Relevant background
- Alignment with the job requirements
- Important limitations
- Areas requiring improvement

# 2. Matching Skills with Resume Evidence

Create a Markdown table with these columns:

| Skill | Resume Evidence | Relevance to Job |

Include only skills supported by the resume.

# 3. Missing Skills and Skill Gaps

Identify:
- Required skills not demonstrated
- Preferred skills not demonstrated
- Technical knowledge gaps
- Relevant skills that need stronger evidence

Do not assume that a skill is missing merely
because it is not explicitly named if equivalent
evidence is available.

# 4. Relevant Experience and Project Analysis

Analyze the candidate's projects, internships,
education, and experience.

Explain how each relevant item connects
to the job requirements.

Do not invent achievements or responsibilities.

# 5. Mandatory vs Preferred Requirements

Separate the job requirements into:

### Mandatory Requirements

### Preferred Requirements

For each requirement, explain whether the
resume demonstrates it, partially demonstrates
it, or does not provide evidence.

# 6. Candidate Strengths

Identify the candidate's demonstrated strengths
based on resume evidence.

Explain their relevance to the position.

# 7. Improvement Recommendations

Provide specific suggestions for improving
technical readiness for the role.

Prioritize the recommendations based on
the gaps identified.

# 8. Resume Optimization Suggestions

Suggest:
- Relevant keywords to include when truthful
- Improvements to project descriptions
- Better ways to present existing experience
- Missing measurable details the candidate
  could add if accurate

Never fabricate metrics or achievements.

# 9. Final AI Assessment

Provide a concise conclusion covering:

- Main areas of alignment
- Most important skill gaps
- Immediate next steps

Do not provide a new ATS score.
Use the existing calculated score only if
it is explicitly supplied in the input.

INSTRUCTIONS:

- Use only the supplied resume and job description.
- Do not invent qualifications, experience,
  certifications, or skills.
- Distinguish demonstrated skills from inferred
  relevance.
- Use readable Markdown headings, bullet points,
  and tables.
- Keep the explanation detailed, specific,
  and professional.
- Complete all 9 sections.
- Do not omit sections.
"""

    return generate_ai_response(prompt)


# --------------------------------
# RESUME QUESTION ANSWERING
# --------------------------------

def answer_resume_question(
    question,
    retrieved_context
):

    prompt = f"""
You are a resume analysis assistant.

Use the resume evidence below to answer
the candidate's question.

RESUME EVIDENCE:
{retrieved_context}

QUESTION:
{question}

INSTRUCTIONS:

- Answer clearly and accurately.
- Use only the supplied evidence.
- If the evidence does not contain the answer,
  clearly state that the information is unavailable.
- Do not invent information.
- Use Markdown formatting when helpful.
"""

    return generate_ai_response(prompt)