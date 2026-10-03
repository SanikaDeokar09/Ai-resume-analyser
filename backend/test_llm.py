
from services.llm_engine import generate_ai_response


prompt = """
Explain in two sentences why Python and Flask
are useful skills for a backend developer.
"""

response = generate_ai_response(prompt)

print("\nGEMINI API TEST")
print("-------------------------")
print(response)