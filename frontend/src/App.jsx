import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import React, { useRef, useState } from "react";
import "./App.css";

import {
  Sparkles,
  Upload,
  FileText,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  Target,
  Zap,
  Menu,
  X,
  LayoutDashboard,
  BriefcaseBusiness,
  FileCheck2,
  RotateCcw,
  TrendingUp,
  AlertCircle,
  Check,
  Lightbulb,
} from "lucide-react";

export default function App() {
  const fileInput = useRef(null);

  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [page, setPage] = useState("Dashboard");
  const [jobDescription, setJobDescription] = useState("");
const [jobMatch, setJobMatch] = useState(null);
const [matchLoading, setMatchLoading] = useState(false);
const [matchError, setMatchError] = useState("");

  const selectFile = (selectedFile) => {
    if (!selectedFile) return;

    if (
      selectedFile.type !== "application/pdf" &&
      !selectedFile.name.toLowerCase().endsWith(".pdf")
    ) {
      setError("Please upload a PDF resume.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10 MB.");
      return;
    }

    setFile(selectedFile);
    setResults(null);
    setError("");
  };

  // Upload resume to the existing Flask backend
  const analyzeResume = async () => {
    if (!file) {
      setError("Please upload your resume first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();

      // Backend expects the field name "file"
      formData.append("file", file);

      const response = await fetch(
        "http://localhost:5000/api/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      console.log("JOB MATCH API RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data.error || "Unable to analyze resume."
        );
      }

      console.log("Resume Analysis Response:", data);

      setResults(data);
      setPage("Results");

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } catch (err) {
      console.error("Resume Analysis Error:", err);

      setError(
        err.message ||
          "Unable to connect to the analysis server."
      );
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    setFile(null);
    setResults(null);
    setError("");
    setPage("Dashboard");

    if (fileInput.current) {
      fileInput.current.value = "";
    }

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };
  const analyzeJobMatch = async () => {
  if (!results?.text) {
    setMatchError("Please analyze your resume first.");
    return;
  }

  if (!jobDescription.trim()) {
    setMatchError("Please enter a job description.");
    return;
  }

  setMatchLoading(true);
  setMatchError("");
  setJobMatch(null);

  try {
    const response = await fetch("http://localhost:5000/api/match", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        resume_text: results.text,
        job_description: jobDescription,
      }),
    });

    const data = await response.json();

    console.log("JOB MATCH API RESPONSE:", data);

    if (!response.ok) {
      throw new Error(data.error || "Unable to analyze job match.");
    }

    // Support both nested and direct backend responses
    const matchData =
      data.match ??
      data.match_result ??
      data.result ??
      data;

    const normalizedMatch = {
      ...matchData,

      match_percentage:
        matchData.match_percentage ??
        matchData.semantic_similarity ??
        matchData.match_score ??
        matchData.similarity_score ??
        matchData.score ??
        matchData.skill_match_percentage ??
        null,

      matching_skills:
        matchData.matching_skills ??
        matchData.matched_skills ??
        matchData.skills_match ??
        [],

      missing_skills:
        matchData.missing_skills ??
        matchData.skill_gaps ??
        matchData.gap_skills ??
        [],

      explanation:
        data.explanation ??
        data.ai_explanation ??
        matchData.explanation ??
        matchData.ai_explanation ??
        matchData.reasoning ??
        matchData.analysis ??
        "",
    };

    console.log("NORMALIZED JOB MATCH:", normalizedMatch);

    setJobMatch(normalizedMatch);

  } catch (err) {
    console.error("Job Match Error:", err);

    setMatchError(
      err.message || "Unable to connect to the backend."
    );
  } finally {
    setMatchLoading(false);
  }
};


  // Backend response mapping
  const analysis = results?.analysis || {};
  const nlp = results?.nlp_analysis || {};
  const nlpAnalysis = nlp;

  const getArray = (object, possibleKeys) => {
    for (const key of possibleKeys) {
      if (Array.isArray(object?.[key])) {
        return object[key];
      }
    }
    return [];
  };

  const getValue = (object, possibleKeys, fallback = "N/A") => {
    for (const key of possibleKeys) {
      if (
        object?.[key] !== undefined &&
        object?.[key] !== null
      ) {
        return object[key];
      }
    }
    return fallback;
  };

  // Handle categorized skills and flat skill arrays
  const categorizedSkills = Object.values(
    analysis.skills || {}
  ).flat();

  const skills = [
    ...new Set([
      ...getArray(nlp, ["detected_skills", "skills"]),
      ...getArray(analysis, [
        "detected_skills",
        "identified_skills",
        "matched_skills",
      ]),
      ...categorizedSkills,
    ]),
  ];

  const strengths = [
    ...getArray(nlp, ["strengths", "positive_points"]),
    ...getArray(analysis, ["strengths", "positive_points"]),
  ];

  const recommendations = [
    ...getArray(nlp, ["recommendations", "suggestions"]),
    ...getArray(analysis, [
      "recommendations",
      "suggestions",
      "improvements",
      "improvement_suggestions",
    ]),
  ];

  const suggestions = recommendations.length
    ? recommendations
    : [
        ...(!analysis.contact?.email
          ? ["Add a professional email address."]
          : []),
        ...(!analysis.contact?.phone
          ? ["Add a contact phone number."]
          : []),
        ...(!analysis.sections_detected?.includes("projects")
          ? ["Add a Projects section with measurable outcomes."]
          : []),
        ...(!analysis.sections_detected?.includes("education")
          ? ["Include a clearly labeled Education section."]
          : []),
        ...((analysis.total_skills || 0) < 5
          ? ["Include relevant technical skills you can demonstrate."]
          : []),
        "Tailor your resume keywords to the target job description.",
      ];

  // const missingSkills = getArray(analysis, [
  //   "missing_skills",
  //   "skill_gaps",
  //   "missing_keywords",
  // ]).concat(
  //   getArray(nlp, [
  //     "missing_skills",
  //     "skill_gaps",
  //     "missing_keywords",
  //   ])
  // );

  const score = getValue(
    analysis,
    ["ats_score", "score", "overall_score", "resume_score"],
    getValue(results, ["ats_score", "score"], null)
  );

  const navigation = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Resume Analyzer", icon: FileText },
    { name: "Job Matching", icon: BriefcaseBusiness },
  ];

  return (
    <div className="app-shell">

      {/* NAVBAR */}

      <header className="navbar">
        <div className="nav-brand">
          <Sparkles size={20} />
          <span>ResuMind</span>
        </div>

        <button
          className="mobile-toggle"
          onClick={() => setMobileMenu(!mobileMenu)}
          aria-label="Toggle navigation"
        >
          {mobileMenu ? <X /> : <Menu />}
        </button>

        <nav
          className={`nav-links ${
            mobileMenu ? "nav-open" : ""
          }`}
        >
          {navigation.map(({ name }) => (
            <button
              key={name}
              className={
                page === name
                  ? "nav-link selected"
                  : "nav-link"
              }
              onClick={() => {
                setPage(name);
                setMobileMenu(false);
              }}
            >
              {name}
            </button>
          ))}
        </nav>

      </header>

      {/* DASHBOARD */}

      {(page === "Dashboard" || page === "Resume Analyzer") && (
        <main className="landing">

          <div className="hero-grid">

            {/* LEFT HERO */}

            <section className="hero-left">

              <div className="hero-badge">
                <Sparkles size={15} />
                AI-POWERED CAREER STUDIO
              </div>

              <h1>
                Unlock Your
                <br />
                <span>Career Potential.</span>
              </h1>

              <p className="hero-description">
                Get an intelligent resume review with AI.
                Discover your ATS compatibility, identify
                skill gaps, and understand how to improve
                your resume for your next career opportunity.
              </p>

              {/* UPLOAD CARD */}

              <div
                className={`upload-card ${
                  dragging ? "dragging" : ""
                }`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setDragging(false);
                  selectFile(e.dataTransfer.files[0]);
                }}
              >
                <input
                  ref={fileInput}
                  type="file"
                  accept=".pdf,application/pdf"
                  hidden
                  onChange={(e) =>
                    selectFile(e.target.files[0])
                  }
                />

                <div className="upload-symbol">
                  {file ? (
                    <FileCheck2 size={29} />
                  ) : (
                    <Upload size={29} />
                  )}
                </div>

                {file ? (
                  <>
                    <h3 className="file-name">
                      {file.name}
                    </h3>

                    <p>
                      {(file.size / (1024 * 1024)).toFixed(2)}
                      {" MB · Ready for analysis"}
                    </p>

                    <button
                      className="change-file"
                      onClick={() =>
                        fileInput.current?.click()
                      }
                    >
                      Choose another file
                    </button>
                  </>
                ) : (
                  <>
                    <h3>Drop your resume here</h3>

                    <p>
                      or choose a file from your computer
                    </p>

                    <span className="file-info">
                      PDF format · Maximum 10 MB
                    </span>

                    <button
                      className="upload-button"
                      onClick={() =>
                        fileInput.current?.click()
                      }
                    >
                      <Upload size={18} />
                      Upload Your Resume
                    </button>
                  </>
                )}

                <div className="privacy-note">
                  <ShieldCheck size={17} />
                  Your resume is handled securely.
                </div>
              </div>

              {error && (
                <div className="error-message">
                  <AlertCircle size={17} />
                  {error}
                </div>
              )}

              {file && (
                <button
                  className="analyze-button"
                  onClick={analyzeResume}
                  disabled={loading}
                >
                  {loading ? (
                    "Analyzing your resume..."
                  ) : (
                    <>
                      Analyze My Resume
                      <ArrowRight size={19} />
                    </>
                  )}
                </button>
              )}

            </section>
            </div>

          {/* FEATURES */}

          <section className="features-section">
            <div className="features-heading">
              <span>YOUR CAREER TOOLKIT</span>

              <h2>Everything you need to stand out</h2>

              <p>
                Turn your resume into a stronger career document
                with intelligent insights.
              </p>
            </div>

            <div className="features-grid">

              <button
                type="button"
                className="feature-card"
              
                onClick={() => {
                  if (!results) {
                    alert("Please upload and analyze your resume first!");
                    setPage("Resume Analyzer");
                  } else {
                    setPage("Results");
                  }
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
              >
                <div className="feature-icon lavender">
                  <Target size={23} />
                </div>

                <h3>ATS Compatibility</h3>

                <p>
                  Understand how your resume aligns with
                  applicant tracking systems.
                </p>
              </button>

              <button
  type="button"
  className="feature-card"
  onClick={() => {
    if (!results) {
      alert("Please upload and analyze your resume first!");
      setPage("Resume Analyzer");
    } else {
      setPage("Results");
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }}
>
    <div className="feature-icon mint">
    <Sparkles size={23} />
  </div>

                <h3>AI Resume Insights</h3>

                <p>
                  Identify strengths, missing information,
                  and areas for improvement.
                </p>
              </button>

            <button
  type="button"
  className="feature-card"
  onClick={() => {
    setPage("Job Matching");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }}
>
      <div className="feature-icon lavender">
    <BriefcaseBusiness size={23} />
  </div>

                <h3>Job Matching</h3>

                <p>
                  Compare your resume against job requirements
                  to discover skill gaps.
                </p>
              </button>

            </div>
          </section>

        </main>
      )}

      {/* RESULTS PAGE */}
      
{/* JOB MATCHING PAGE */}

{page === "Job Matching" && (
  <main className="job-match-page">

    <div className="job-match-header">
      <span className="hero-badge">
        <Sparkles size={15} />
        AI-POWERED CAREER MATCHING
      </span>

      <h1>
        Find Your <span>Career Match.</span>
      </h1>

      <p>
        Compare your resume with a job description to discover
        compatibility, matching skills, missing qualifications,
        and personalized improvement insights.
      </p>
    </div>

    <section className="job-match-card">

      <label htmlFor="job-description">
        Paste Job Description
      </label>

      <textarea
        id="job-description"
        className="job-description-input"
        placeholder="Paste the complete job description here, including responsibilities, required skills, qualifications, and experience..."
        value={jobDescription}
        onChange={(e) => {
          setJobDescription(e.target.value);
          setMatchError("");
          setJobMatch(null);
        }}
      />

      {!results?.text && (
        <div className="job-match-error">
          Please analyze your resume first using the Resume Analyzer.
          Your analyzed resume will be used for job matching.
          <button
            type="button"
            className="change-file"
            onClick={() => setPage("Resume Analyzer")}
          >
            Go to Resume Analyzer
          </button>
        </div>
      )}

      <button
        className="job-match-submit"
        onClick={analyzeJobMatch}
        disabled={matchLoading || !results?.text}
      >
        {matchLoading ? (
          "Analyzing Job Compatibility..."
        ) : (
          <>
            <Sparkles size={18} />
            Analyze Job Match
            <ArrowRight size={18} />
          </>
        )}
      </button>

      {matchError && (
        <div className="job-match-error">
          <AlertCircle size={17} />
          {matchError}
        </div>
      )}

    </section>

    {jobMatch && (
      <section className="job-match-results">

        <div className="job-match-score-card">
          <div>
            <span>JOB COMPATIBILITY</span>
            <h2>Your Matching Overview</h2>
            <p>
              Comparison based on your resume and the supplied
              job description.
            </p>
          </div>

          <div className="job-match-score">
            {(() => {
            const rawScore =
  jobMatch.match_percentage ??
  jobMatch.semantic_similarity ??
  jobMatch.skill_match_percentage ??
  jobMatch.match_score ??
  jobMatch.similarity_score ??
  jobMatch.score;

              const numericScore = Number(rawScore);

              if (!Number.isFinite(numericScore)) return "N/A";

              const percentage =
                numericScore <= 1
                  ? numericScore * 100
                  : numericScore;

              return `${Math.round(percentage)}%`;
            })()}
          </div>
        </div>

        <div className="job-match-result-grid">

          <div className="job-match-result-box">
            <h3>
              <CheckCircle2 size={18} />
              Matching Skills
            </h3>

            <div className="job-match-tags">
              {(
                jobMatch.matching_skills ??
                jobMatch.matched_skills ??
                jobMatch.skills_match ??
                []
              ).length > 0 ? (
                (
                  jobMatch.matching_skills ??
                  jobMatch.matched_skills ??
                  jobMatch.skills_match
                ).map((skill, index) => (
                  <span className="job-match-tag" key={index}>
                    {typeof skill === "string"
                      ? skill
                      : skill.name || JSON.stringify(skill)}
                  </span>
                ))
              ) : (
                <p>No separate matching skills returned.</p>
              )}
            </div>
          </div>

          <div className="job-match-result-box">
            <h3>
              <AlertCircle size={18} />
              Missing Skills
            </h3>

            <div className="job-match-tags">
              {(
                jobMatch.missing_skills ??
                jobMatch.skill_gaps ??
                jobMatch.gap_skills ??
                []
              ).length > 0 ? (
                (
                  jobMatch.missing_skills ??
                  jobMatch.skill_gaps ??
                  jobMatch.gap_skills
                ).map((skill, index) => (
                  <span
                    className="job-match-tag missing"
                    key={index}
                  >
                    {typeof skill === "string"
                      ? skill
                      : skill.name || JSON.stringify(skill)}
                  </span>
                ))
              ) : (
                <p>No separate missing skills returned.</p>
              )}
            </div>
          </div>

        </div>

        
<div className="job-match-explanation">
  <h3>
    <Sparkles size={19} />
    AI Match Explanation
  </h3>

  <div className="ai-explanation-content">
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {String(
        jobMatch.explanation ??
        jobMatch.ai_explanation ??
        jobMatch.reasoning ??
        jobMatch.analysis ??
        jobMatch.message ??
        "The backend returned a matching result. Additional explanation fields are not available."
      )}
    </ReactMarkdown>
  </div>
</div>
        <button
  type="button"
  className="job-match-submit"
  onClick={() => {
    setJobMatch(null);
    setMatchError("");
    setJobDescription("");
    setPage("Job Matching");
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  }}
>
  Analyze Another Job
  <RotateCcw size={17} />
</button>

      </section>
    )}

  </main>
)}

      {page === "Results" && results && (
        <main className="results-page">

          <button
            className="back-button"
            onClick={resetAnalysis}
          >
            <RotateCcw size={17} />
            New Analysis
          </button>

          <div className="results-header">
            <span className="hero-badge">
              <Sparkles size={15} />
              ANALYSIS COMPLETED
            </span>

            <h1>Your Resume Insights</h1>

            <p>{results.filename || file?.name}</p>
          </div>

          {/* SCORE CARDS */}

          <div className="results-grid">

            <div className="result-box main-score">
              <span>ATS Compatibility Score</span>

              <strong>
                {score !== null && score !== "N/A"
                  ? `${score}${typeof score === "number" ? "%" : ""}`
                  : "N/A"}
              </strong>

              <p>Resume analysis score</p>
            </div>

            <div className="result-box">
              <span>Skills Identified</span>

              <strong>{skills.length}</strong>

              <p>Detected resume skills</p>
            </div>

            <div className="result-box">
              <span>Recommendations</span>

              <strong>{suggestions.length}</strong>

              <p>Improvement suggestions</p>
            </div>

          </div>

          {/* SKILLS */}

          <section className="result-details">
            <div className="result-section-heading">
              <div>
                <span className="section-eyebrow">
                  SKILL ANALYSIS
                </span>

                <h2>Skills Identified</h2>
              </div>

              <Target size={23} />
            </div>

            {skills.length > 0 ? (
              <div className="skill-list">
                {skills.map((skill, index) => (
                  <span
                    className="skill-chip"
                    key={`${skill}-${index}`}
                  >
                    <Check size={15} />
                    {typeof skill === "string"
                      ? skill
                      : skill.name || JSON.stringify(skill)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="empty-result">
                No separate skill list was returned by the
                current backend analysis.
              </p>
            )}
          </section>

                    {/* STRENGTHS */}

          <section className="result-details">
            <div className="result-section-heading">
              <div>
                <span className="section-eyebrow">
                  POSITIVE FINDINGS
                </span>

                <h2>Resume Strengths</h2>
              </div>

              {/* <CheckCircle2 size={23} /> */}
            </div>

            {strengths.length > 0 ? (
              <ul className="result-list">
                {[...new Set(
                  strengths
                    .map((item) =>
                      typeof item === "string"
                        ? item.trim()
                        : String(item?.text || item?.description || "")
                    )
                    .filter(Boolean)
                )].map((item, index) => (
                  <li key={`${item}-${index}`}>
                    <CheckCircle2 size={18} />

                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-result">
                Strength details are not separately available
                in this backend response.
              </p>
            )}
          </section>

          {/* MISSING SKILLS

          <section className="result-details">
            <div className="result-section-heading">
              <div>
                <span className="section-eyebrow">
                  SKILL GAPS
                </span>

                <h2>Missing Skills & Keywords</h2>
              </div>

              <AlertCircle size={23} />
            </div>

            {missingSkills.length > 0 ? (
              <div className="skill-list">
                {missingSkills.map((skill, index) => (
                  <span
                    className="skill-chip missing-chip"
                    key={index}
                  >
                    {typeof skill === "string"
                      ? skill
                      : JSON.stringify(skill)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="empty-result">
                No separate missing-skills list was returned.
                Use Job Matching to compare against a specific
                job description.
              </p>
            )}
          </section> */}

          {/* SUGGESTIONS */}

          <section className="result-details">
            <div className="result-section-heading">
              <div>
                <span className="section-eyebrow">
                  ACTION PLAN
                </span>

                <h2>Improvement Suggestions</h2>
              </div>

              <Lightbulb size={23} />
            </div>

            {suggestions.length > 0 ? (
              <div className="suggestion-list">
                {suggestions.map((suggestion, index) => (
                  <div
                    className="suggestion-item"
                    key={index}
                  >
                    <div className="suggestion-number">
                      {index + 1}
                    </div>

                    <p>
                      {typeof suggestion === "string"
                        ? suggestion
                        : JSON.stringify(suggestion)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-result">
                No separate recommendations were returned
                by the current backend.
              </p>
            )}
          </section>

          {/* NLP ANALYSIS */}

          {/* <section className="result-details">
            <div className="result-section-heading">
              <div>
                <span className="section-eyebrow">
                  LANGUAGE ANALYSIS
                </span> */}

                {/* <h2>NLP Insights</h2>
              </div>

              <TrendingUp size={23} />
            </div>

            {Object.keys(nlpAnalysis).length > 0 ? (
              <pre className="analysis-json">
                {JSON.stringify(nlpAnalysis, null, 2)}
              </pre>
            ) : (
              <p className="empty-result">
                No separate NLP analysis was returned.
              </p>
            )}
          </section> */}

          {/* DOCUMENT INFORMATION */}

          <section className="result-details">
            <h2>Document Information</h2>

            <div className="document-info-grid">
              <div>
                <span>File Name</span>
                <strong>
                  {results.filename || file?.name || "Resume"}
                </strong>
              </div>

              <div>
                <span>Pages</span>
                <strong>{results.pages ?? "N/A"}</strong>
              </div>

              <div>
                <span>Extracted Characters</span>
                <strong>{results.characters ?? "N/A"}</strong>
              </div>
            </div>
          </section>

          {/* EXTRACTED TEXT */}

          {results.text && (
            <section className="result-details">
              <h2>Extracted Resume Text</h2>

              <details className="resume-text-details">
                <summary>View extracted text</summary>

                <pre className="analysis-json">
                  {results.text}
                </pre>
              </details>
            </section>
          )}

          <button
            className="analyze-button results-new-button"
            onClick={resetAnalysis}
          >
            Analyze Another Resume
            <ArrowRight size={19} />
          </button>

        </main>
      )}
    </div>
  );
}