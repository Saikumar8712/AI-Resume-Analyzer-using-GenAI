import { useState, useRef } from "react";

const SAMPLE_JOBS = [
  {
    title: "Python Backend Developer",
    jd: "We are seeking a Python Backend Developer. Requirements: Strong experience in Python, FastAPI or Flask, SQL databases (PostgreSQL/MySQL), REST APIs, Git, and Docker. Experience with unit testing (pytest) and Agile methodologies is required. Familiarity with CI/CD and cloud deployment is a plus.",
  },
  {
    title: "Full Stack Engineer",
    jd: "Looking for a Full Stack Engineer proficient in React, JavaScript, TypeScript, Node.js, and HTML/CSS. Must have experience building scalable REST APIs, managing SQL/NoSQL databases, Git version control, and writing automated tests. Strong communication skills and experience in CI/CD required.",
  },
  {
    title: "Machine Learning Engineer",
    jd: "Seeking an ML Engineer with deep expertise in Python, Machine Learning, Deep Learning (PyTorch or TensorFlow), Pandas, and NLP. Experience deploying models via FastAPI or Docker, SQL database querying, and strong data structures knowledge.",
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
    const jdClean = jd.trim();
    if (jdClean.length < 2) return setErr("Job description is required (at least 2 characters).");
    setErr("");
    onSubmit(file, jdClean, title.trim() || "Target Role");
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
          <span className="field-label">Job Description</span>
          <span className={`char-counter ${jd.trim().length < 2 ? "warn" : "ok"}`}>
            {jd.trim().length}
          </span>
        </div>
        <textarea
          rows="6"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          placeholder="Paste requirements, responsibilities, or job description here..."
          className="text-input textarea"
        />
      </label>

      <div className="samples-box">
        <span className="samples-title">Try quick sample:</span>
        <div className="samples-chips">
          {SAMPLE_JOBS.map((s) => (
            <button
              key={s.title}
              type="button"
              className="chip-btn"
              onClick={() => loadSample(s)}
            >
              + {s.title}
            </button>
          ))}
        </div>
      </div>

      {err && <div className="error-box" role="alert">{err}</div>}

      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? (
          <span className="btn-loading">
            <span className="spinner"></span> Analyzing Resume...
          </span>
        ) : (
          "⚡ Analyze Resume Match"
        )}
      </button>
    </form>
  );
}
