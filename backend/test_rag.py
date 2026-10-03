
from services.rag_engine import analyze_resume_relevance


resume_text = """
Srushti Deokar

Skills:
Python, Flask, Machine Learning, SQL, REST API,
Pandas, NumPy, Git.

Projects:
Developed a productivity tracking web application
using Flask and Python.

Education:
B.E. Artificial Intelligence and Data Science.
"""


job_description = """
We need a Python developer with Flask experience.
Knowledge of Machine Learning, SQL, Docker and AWS
is required. REST API development is preferred.
"""


result = analyze_resume_relevance(
    resume_text,
    job_description,
    top_k=2
)

print("\nChunks created:", result["chunks_count"])

print("\nRetrieved evidence:")

for item in result["retrieved_evidence"]:
    print("\nRequirement:", item["query"])
    print("Evidence:", item["resume_evidence"])
    print("Similarity:", item["similarity"], "%")

print("\nFinal context:")
print(result["context"])