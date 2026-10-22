import { useState } from "react";

export default function ScoreCard({
  score = 0,
  atsScore = 0,
  atsGrade = "B",
  title = "Target Role",
  mode = "basic",
  breakdown = {},
  atsBreakdown = {}
}) {
  const [activeMetric, setActiveMetric] = useState("role"); // 'role' | 'ats'

  const matchTone = score >= 75 ? "high" : score >= 50 ? "mid" : "low";
  const matchLabel = score >= 75 ? "Strong Role Fit" : score >= 50 ? "Moderate Fit" : "Skills Gap";

  const atsTone = atsScore >= 80 ? "high" : atsScore >= 60 ? "mid" : "low";
  const atsLabel = atsScore >= 80 ? `Grade ${atsGrade} · ATS Ready` : `Grade ${atsGrade} · Needs Work`;

  // Circular calculations
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const matchOffset = circumference - (score / 100) * circumference;
  const atsOffset = circumference - (atsScore / 100) * circumference;

  return (
    <section className="score-card-advanced" aria-labelledby="score-h">
      <div className="scores-dual-container">
        {/* 1. Job Match Score Meter */}
        <div className={`score-unit match-unit tone-${matchTone}`}>
          <div className="ring-wrapper">
            <div className={`neon-glow glow-${matchTone}`}></div>
            <svg className="score-svg" viewBox="0 0 90 90" role="img" aria-label={`Job match score: ${score}%`}>
              <defs>
                <linearGradient id="grad-job-fit-high" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#10b981" />
                  <stop offset="50%" stopColor="#14b8a6" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
                <linearGradient id="grad-job-fit-mid" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#f59e0b" />
                  <stop offset="100%" stopColor="#fbbf24" />
                </linearGradient>
                <linearGradient id="grad-job-fit-low" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#f43f5e" />
                  <stop offset="100%" stopColor="#fb7185" />
                </linearGradient>
              </defs>
              <circle className="ring-track" cx="45" cy="45" r={radius} />
              <circle
                className={`ring-meter meter-${matchTone}`}
                cx="45" cy="45" r={radius}
                strokeDasharray={circumference}
                strokeDashoffset={matchOffset}
              />
            </svg>
            <div className="ring-center-content">
              <span className="meter-val">{score}</span>
              <span className="meter-sym">%</span>
            </div>
          </div>
          <div className="unit-label-group">
            <span className="unit-title">Job Fit Match</span>
            <span className={`status-tag tag-${matchTone}`}>{matchLabel}</span>
          </div>
        </div>

        {/* 2. Separate ATS Score Meter */}
        <div className={`score-unit ats-unit tone-${atsTone}`}>
          <div className="ring-wrapper">
            <div className={`neon-glow glow-${atsTone}`}></div>
            <svg className="score-svg" viewBox="0 0 90 90" role="img" aria-label={`ATS compatibility score: ${atsScore}%`}>
              <defs>
                <linearGradient id="grad-ats-meter-high" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#06b6d4" />
                  <stop offset="45%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#6366f1" />
                </linearGradient>
                <linearGradient id="grad-ats-meter-mid" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#f59e0b" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
                <linearGradient id="grad-ats-meter-low" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#f43f5e" />
                  <stop offset="100%" stopColor="#e11d48" />
                </linearGradient>
              </defs>
              <circle className="ring-track" cx="45" cy="45" r={radius} />
              <circle
                className={`ring-meter meter-ats meter-${atsTone}`}
                cx="45" cy="45" r={radius}
                strokeDasharray={circumference}
                strokeDashoffset={atsOffset}
              />
            </svg>
            <div className="ring-center-content">
              <span className="meter-val">{atsScore}</span>
              <span className="meter-sym">%</span>
            </div>
          </div>
          <div className="unit-label-group">
            <span className="unit-title">ATS Compatibility</span>
            <span className={`status-tag tag-${atsTone}`}>{atsLabel}</span>
          </div>
        </div>
      </div>

      <div className="score-main-content">
        <div className="score-header-row">
          <div>
            <h2 id="score-h" className="job-heading">{title}</h2>
            <div className="score-meta-badges">
              <span className={`mode-badge mode-${mode}`}>
                {mode === "ai" ? "✨ AI-Enhanced (Gemini)" : "⚡ Advanced ATS Parser"}
              </span>
              <span className="ats-compliance-badge">
                🛡️ ATS Screening Checked
              </span>
            </div>
          </div>

          <div className="breakdown-toggle-pill">
            <button
              type="button"
              className={`toggle-tab ${activeMetric === "role" ? "active" : ""}`}
              onClick={() => setActiveMetric("role")}
            >
              Role Fit
            </button>
            <button
              type="button"
              className={`toggle-tab ${activeMetric === "ats" ? "active" : ""}`}
              onClick={() => setActiveMetric("ats")}
            >
              ATS Metrics
            </button>
          </div>
        </div>

        <div className="breakdown-grid-modern">
          {activeMetric === "role" ? (
            Object.entries(breakdown || {}).map(([k, v]) => (
              <div key={k} className="metric-pill-card">
                <div className="metric-info">
                  <span className="metric-name">{k}</span>
                  <span className="metric-number">{v}%</span>
                </div>
                <div className="metric-track">
                  <div
                    className={`metric-fill fill-${matchTone}`}
                    style={{ width: `${Math.min(Math.max(v, 0), 100)}%` }}
                  />
                </div>
              </div>
            ))
          ) : (
            Object.entries(atsBreakdown || {}).map(([k, v]) => (
              <div key={k} className="metric-pill-card ats-metric-card">
                <div className="metric-info">
                  <span className="metric-name">{k}</span>
                  <span className="metric-number">{v}%</span>
                </div>
                <div className="metric-track">
                  <div
                    className={`metric-fill fill-${atsTone}`}
                    style={{ width: `${Math.min(Math.max(v, 0), 100)}%` }}
                  />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}

