import { useState, useRef } from "react";

const SAMPLE_JOBS = [
  {
    icon: "🤖",
    title: "Generative AI & LLM Engineer",
    jd: "We are seeking a Generative AI & LLM Engineer to develop production AI applications. Requirements: Hands-on experience with Large Language Models (LLMs), LangChain, LlamaIndex, OpenAI / Claude APIs, and RAG (Retrieval-Augmented Generation) architectures. Strong proficiency in Python, FastAPI, vector databases (Pinecone, ChromaDB, Weaviate), prompt engineering, and embeddings. Experience fine-tuning open-source models (Hugging Face) and cloud deployment on AWS or GCP is a plus.",
  },
  {
    icon: "☁️",
    title: "DevOps & Cloud Engineer",
    jd: "Looking for a DevOps & Cloud Engineer to design scalable cloud infrastructure. Requirements: Strong experience in AWS or Microsoft Azure, Docker containerization, and Kubernetes cluster orchestration. Proven skills in CI/CD automation (GitHub Actions, GitLab CI, Jenkins), Infrastructure as Code (Terraform), and Linux shell scripting. Experience with Prometheus, Grafana monitoring, microservices architecture, and cloud security compliance.",
  },
  {
    icon: "📊",
    title: "Data Scientist & AI Specialist",
    jd: "Hiring a Data Scientist & AI Specialist. Requirements: Deep expertise in Python, Machine Learning algorithms, Deep Learning (PyTorch or TensorFlow), Scikit-Learn, Pandas, and NumPy. Proficiency in SQL querying, exploratory data analysis, hypothesis testing, and statistical modeling. Experience deploying ML models via FastAPI or Docker, data visualization (PowerBI, Tableau), and NLP techniques.",
  },
  {
    icon: "📈",
    title: "Big Data & Data Engineer",
    jd: "Seeking a Data Engineer for high-throughput data pipelines. Requirements: Advanced SQL and Python programming skills, hands-on experience with Apache Spark / PySpark, and data workflow orchestration with Apache Airflow. Experience building scalable ETL/ELT pipelines, data lakes, and data warehousing on Snowflake, AWS Redshift, or Google BigQuery. Familiarity with Kafka streaming and data modeling.",
  },
  {
    icon: "🛡️",
    title: "Cyber Security Analyst",
    jd: "We are looking for a Cyber Security Analyst / Security Engineer. Requirements: Hands-on experience in vulnerability assessment, penetration testing concepts, and SIEM monitoring (Splunk, Microsoft Sentinel). Knowledge of network security protocols, firewalls, IDS/IPS, Wireshark packet inspection, and incident response. Familiarity with security frameworks (NIST, CIS, ISO 27001), IAM, and cloud security fundamentals.",
  },
  {
    icon: "☕",
    title: "Java Full Stack Developer",
    jd: "Looking for a Java Full Stack Developer. Requirements: Strong proficiency in Java (11/17+), Spring Boot framework, Spring Security, and Microservices architecture. Experience developing RESTful APIs, object-relational mapping with Hibernate/JPA, and SQL database management (PostgreSQL or MySQL). Frontend proficiency in React or Angular, JavaScript/TypeScript, Docker, Git, CI/CD, and JUnit automated testing.",
  },
  {
    icon: "⚡",
    title: "Frontend Engineer (React / Next.js)",
    jd: "Seeking a Senior Frontend Engineer. Requirements: Expert-level proficiency in React, Next.js (App Router), TypeScript, modern JavaScript (ES6+), and HTML5/CSS3. Deep understanding of Tailwind CSS, state management (Redux Toolkit, Zustand), responsive mobile-first UI development, and REST / GraphQL API integration. Familiarity with Core Web Vitals optimization and automated testing with Jest / React Testing Library.",
  },
  {
    icon: "🧪",
    title: "QA Automation Engineer / SDET",
    jd: "We are hiring a QA Automation Engineer / SDET. Requirements: Extensive experience writing automated test frameworks using Selenium WebDriver, Cypress, or Playwright. Strong programming skills in Python, Java, or TypeScript. Experience in REST API automation using Postman or RestAssured, CI/CD pipeline integration, test execution reporting, and Agile/Scrum workflows.",
  },
  {
    icon: "🐍",
    title: "Python Backend Developer",
    jd: "We are seeking a Python Backend Developer. Requirements: Strong experience in Python, FastAPI or Flask, SQL databases (PostgreSQL/MySQL), SQLAlchemy, REST APIs, Git, and Docker. Experience with background tasks (Celery/Redis), unit testing (pytest), CI/CD pipelines, and cloud deployment is required.",
  },
  {
    icon: "🌐",
    title: "Full Stack Engineer (MERN)",
    jd: "Looking for a Full Stack Engineer proficient in React, JavaScript, TypeScript, Node.js, Express, and HTML/CSS. Must have experience building scalable REST APIs, managing SQL/NoSQL databases (PostgreSQL, MongoDB), Git version control, and writing automated tests. Strong communication skills and experience in CI/CD required.",
  }
];

export default function UploadForm({ onSubmit, loading, onReset }) {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [title, setTitle] = useState("");
  const [err, setErr] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const pick = (f) => {
    if (!f) return;
    const nameLower = f.name.toLowerCase();
    if (!nameLower.endsWith(".pdf") && !nameLower.endsWith(".docx")) {
      return setErr("Please upload a valid PDF or Word (.docx) file.");
    }
    if (f.size > 5 * 1024 * 1024) {
      return setErr("File size exceeds 5 MB limit.");
    }
    setErr("");
    setFile(f);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      pick(e.dataTransfer.files[0]);
    }
  };

  // Automatically removes PDF, job description, job title, and resets analysis
  const clearFile = (e) => {
    if (e) e.stopPropagation();
    setFile(null);
    setTitle("");
    setJd("");
    setErr("");
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (onReset) onReset();
  };

  const submit = (e) => {
    e.preventDefault();
    if (!file) return setErr("Upload your resume as a PDF or Word (.docx) file.");
    setErr("");
    onSubmit(file, jd.trim(), title.trim() || "Target Role");
  };

  const loadSample = (sample) => {
    setTitle(sample.title);
    setJd(sample.jd);
    setErr("");
  };

  return (
    <form className="panel form-panel" onSubmit={submit} noValidate>
      <div className="panel-header">
        <h2 className="panel-title">Upload & Compare</h2>
        <div className="header-actions">
          {(file || title || jd) && (
            <button
              type="button"
              className="text-reset-btn"
              onClick={clearFile}
              title="Clear resume, title, and job description"
            >
              ✕ Clear All
            </button>
          )}
          <span className="badge-pill">Step 1 & 2</span>
        </div>
      </div>

      <div
        className={`drop ${isDragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword"
          onChange={(e) => pick(e.target.files?.[0])}
          style={{ display: "none" }}
        />
        <div className="drop-content">
          <div className="drop-icon">📄</div>
          {file ? (
            <div className="file-info">
              <span className="file-name">{file.name}</span>
              <span className="file-size">({(file.size / 1024).toFixed(0)} KB)</span>
              <button
                type="button"
                className="clear-file-btn"
                onClick={clearFile}
                title="Remove file"
              >
                ✕ Remove
              </button>
            </div>
          ) : (
            <div>
              <p className="drop-prompt">
                <strong>Click to browse</strong> or drag & drop PDF / Word (.docx) resume
              </p>
              <p className="drop-sub">PDF or DOCX up to 5 MB</p>
            </div>
          )}
        </div>
      </div>

      <label className="field-group">
        <span className="field-label">Target Job Title <span className="field-opt">(optional)</span></span>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Senior Python Developer"
          className="text-input"
        />
      </label>

      <label className="field-group">
        <div className="field-header">
          <span className="field-label">Target Job Description <span className="field-opt">(optional — leave blank for general-purpose ATS resume)</span></span>
          <span className={`char-counter ${jd.trim().length > 0 ? "ok" : "muted"}`}>
            {jd.trim().length} chars
          </span>
        </div>
        <textarea
          rows="6"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          placeholder="Paste requirements, responsibilities, or target job description (optional)..."
          className="text-input textarea"
        />
      </label>

      <div className="samples-box">
        <div className="samples-header flex-between">
          <span className="samples-title">⚡ Try Quick Sample Courses & In-Demand Roles:</span>
          <span className="samples-count-tag">{SAMPLE_JOBS.length} Trending Roles</span>
        </div>
        <div className="samples-chips">
          {SAMPLE_JOBS.map((s) => {
            const isSelected = title === s.title;
            return (
              <button
                key={s.title}
                type="button"
                className={`chip-btn ${isSelected ? "active" : ""}`}
                onClick={() => loadSample(s)}
                title={`Click to auto-fill requirements for ${s.title}`}
              >
                <span className="chip-icon">{s.icon || "💼"}</span> {s.title}
              </button>
            );
          })}
        </div>
      </div>

      {err && <div className="error-box" role="alert">{err}</div>}

      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? (
          <span className="btn-loading">
            <span className="spinner"></span> Analyzing Resume...
          </span>
        ) : jd.trim() ? (
          "⚡ Analyze Job Match"
        ) : (
          "⚡ Optimize General-Purpose ATS Resume"
        )}
      </button>
    </form>
  );
}
