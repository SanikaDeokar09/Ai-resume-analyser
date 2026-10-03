# ResuMind – AI Resume Analyzer

An AI-powered resume analysis and job description matching platform designed to help users understand their resume compatibility, identify skill gaps, and improve their applications.

## Overview

ResuMind is a web-based application that analyzes resumes using Natural Language Processing (NLP), semantic matching, and AI-driven techniques. It evaluates resume content against a given job description and provides insights to help users understand their qualifications and areas for improvement.

The platform combines a React-based frontend with a Python Flask backend to deliver an interactive resume analysis experience.

## Features

* **Resume Upload:** Upload resumes for automated analysis.
* **ATS Compatibility Analysis:** Evaluate resume content against job requirements.
* **Job Description Matching:** Compare resume skills and experience with a target job description.
* **Semantic Matching:** Identify contextual similarities beyond exact keyword matches.
* **Skill Gap Identification:** Highlight relevant skills that may be missing from the resume.
* **AI-Powered Insights:** Generate analysis and improvement suggestions.
* **Interactive Dashboard:** View resume analysis results through a user-friendly interface.

## Technology Stack

### Frontend

* React.js
* Vite
* JavaScript
* CSS
* Lucide React

### Backend

* Python
* Flask
* Natural Language Processing (NLP)
* Semantic Matching
* AI-Based Analysis

## Project Structure

```text
ResuMind/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── services/
│       ├── llm_engine.py
│       ├── nlp_engine.py
│       ├── rag_engine.py
│       ├── resume_analyzer.py
│       └── semantic_matcher.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── eslint.config.js
│
├── .gitignore
└── README.md
```

## Installation and Setup

### Prerequisites

* Python 3.10+
* Node.js and npm
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/SanikaDeokar09/Ai-resume-analyser.git
cd Ai-resume-analyser
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
python app.py
```

### 3. Frontend Setup

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed in the terminal to access ResuMind.

## Application Workflow

1. Upload a resume.
2. Enter the target job description.
3. Submit the information for analysis.
4. Review the resume compatibility results.
5. Explore matching insights and skill gaps.
6. Use the suggestions to improve the resume.

## Future Enhancements

* Resume section-wise analysis.
* Enhanced ATS scoring and evaluation.
* Personalized resume improvement recommendations.
* Support for additional resume formats.
* Secure user authentication and analysis history.
* Cloud deployment.

## Author

**Sanika Deokar**

GitHub: [SanikaDeokar09](https://github.com/SanikaDeokar09)

---

*ResuMind – Making resume analysis smarter and more accessible.*
