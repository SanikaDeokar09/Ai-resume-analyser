from services.semantic_matcher import analyze_job_match
from services.resume_analyzer import SKILL_DATABASE

resume = """
Python developer with experience in Flask, REST API,
Machine Learning, SQL, Pandas, NumPy and Git.
Developed a productivity tracking web application.
"""

job_description = """
We are looking for a Python developer with experience
in Flask, Machine Learning, SQL, Docker and AWS.
Knowledge of REST API development is required.
"""

result = analyze_job_match(
    resume,
    job_description,
    SKILL_DATABASE
)

print("\nSEMANTIC MATCH RESULT")
print("---------------------")

for key, value in result.items():
    print(f"\n{key}: {value}")