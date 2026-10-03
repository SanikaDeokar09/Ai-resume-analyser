
from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader
from werkzeug.utils import secure_filename

import io

from services.nlp_engine import analyze_text

from services.resume_analyzer import (
    analyze_resume,
    SKILL_DATABASE
)

from services.semantic_matcher import analyze_job_match

from services.rag_engine import analyze_resume_relevance

from services.llm_engine import generate_resume_explanation


app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# --------------------------------
# HOME ROUTE
# --------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "ResuMind AI Backend is running",
        "status": "success"
    })


# --------------------------------
# RESUME UPLOAD AND ANALYSIS
# --------------------------------

@app.route("/api/upload", methods=["POST"])
def upload_resume():

    if "file" not in request.files:
        return jsonify({
            "error": "No file was provided"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "Please select a PDF file"
        }), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are supported"
        }), 400

    try:
        filename = secure_filename(file.filename)

        reader = PdfReader(io.BytesIO(file.read()))

        if reader.is_encrypted:
            return jsonify({
                "error": "Password-protected PDFs are not supported"
            }), 400

        extracted_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()

        if not extracted_text:
            return jsonify({
                "error": "No readable text found in the PDF"
            }), 422

        # Resume analysis
        analysis = analyze_resume(extracted_text)

        # NLP analysis
        nlp_analysis = analyze_text(extracted_text)

        # --------------------------------
        # TEMPORARY DEBUGGING
        # --------------------------------

        print("\n========== RESUMIND DEBUG ==========")

        print("\nEXTRACTED RESUME TEXT:")
        print(extracted_text)

        print("\nDETECTED RESUME SKILLS:")
        print(analysis.get("skills", []))

        print("\nSKILL DATABASE:")
        print(SKILL_DATABASE)

        print("====================================\n")

        # --------------------------------
        # API RESPONSE
        # --------------------------------

        return jsonify({
            "message": "Resume analyzed successfully",
            "filename": filename,
            "pages": len(reader.pages),
            "characters": len(extracted_text),
            "text": extracted_text,
            "analysis": analysis,
            "nlp_analysis": nlp_analysis
        }), 200

    except Exception:
        app.logger.exception("Resume processing failed")

        return jsonify({
            "error": "Unable to process the resume."
        }), 500


# --------------------------------
# JOB MATCHING
# --------------------------------

@app.route("/api/match", methods=["POST"])
def match_resume():

    data = request.get_json(silent=True) or {}

    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()

    if not resume_text:
        return jsonify({
            "error": "Resume text is required"
        }), 400

    if not job_description:
        return jsonify({
            "error": "Job description is required"
        }), 400

    # STEP 1: SEMANTIC MATCHING

    try:
        result = analyze_job_match(
            resume_text,
            job_description,
            SKILL_DATABASE
        )

    except Exception:
        app.logger.exception("Semantic matching failed")

        return jsonify({
            "error": "Unable to perform semantic resume matching."
        }), 500

    # STEP 2: RAG RETRIEVAL

    rag_result = {}
    retrieved_context = ""

    try:
        rag_result = analyze_resume_relevance(
            resume_text,
            job_description
        )

        if isinstance(rag_result, dict):

            retrieved_context = (
                rag_result.get("context")
                or rag_result.get("retrieved_context")
                or ""
            )

        else:
            retrieved_context = str(rag_result)

    except Exception:
        app.logger.exception("RAG retrieval failed")

        rag_result = {
            "error": (
                "Relevant evidence retrieval is temporarily unavailable."
            ),
            "context": ""
        }

    # STEP 3: GEMINI EXPLANATION

    ai_explanation = ""

    try:
        ai_explanation = generate_resume_explanation(
            resume_text,
            job_description,
            retrieved_context
        )

        if not ai_explanation:
            ai_explanation = (
                "AI explanation is temporarily unavailable. "
                "Your semantic matching and skill analysis "
                "are still available."
            )

    except Exception:
        app.logger.exception("Gemini explanation failed")

        ai_explanation = (
            "AI explanation is temporarily unavailable. "
            "Your semantic matching and skill analysis "
            "are still available."
        )

    # STEP 4: RETURN COMBINED RESULTS

    return jsonify({
        "message": "AI-powered resume matching completed",
        "result": result,
        "rag_analysis": rag_result,
        "ai_explanation": ai_explanation
    }), 200


# --------------------------------
# RUN FLASK SERVER
# --------------------------------

if __name__ == "__main__":

    print("Starting ResuMind Flask Server...", flush=True)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )