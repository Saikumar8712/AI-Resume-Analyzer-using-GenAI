import { useState } from "react";

export default function ScoreCard({
  score = 0,
  matchGrade = "B",
  resumeQualityScore = 80,
  qualityGrade = "A",
  atsScore = 90,
  atsGrade = "A",
  title = "Target Role",
  mode = "basic",
  breakdown = {},
  qualityBreakdown = {},
  atsBreakdown = {},
  scoreReasons = {},
  isGeneralPurpose = false
}) {
  const [activeMetric, setActiveMetric] = useState("quality"); // 'quality' | 'match' | 'ats'

  const qualityTone = resumeQualityScore >= 80 ? "high" : resumeQualityScore >= 60 ? "mid" : "low";
  const matchTone = score >= 75 ? "high" : score >= 50 ? "mid" : "low";
  const atsTone = atsScore >= 80 ? "high" : atsScore >= 60 ? "mid" : "low";

  const qualityLabel = `Grade ${qualityGrade} · ${resumeQualityScore >= 80 ? "Executive Ready" : "Good Base"}`;
  const matchLabel = isGeneralPurpose ? "General Profile" : score >= 75 ? "Strong Role Fit" : score >= 50 ? "Moderate Fit" : "Skills Gap";
  const atsLabel = `Grade ${atsGrade} · ${atsScore >= 80 ? "1-Page ATS Ready" : "Format Review"}`;

  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const qualityOffset = circumference - (resumeQualityScore / 100) * circumference;
  const matchOffset = circumference - (score / 100) * circumference;
  const atsOffset = circumference - (atsScore / 100) * circumference;

  return (
    <section className="score-card-advanced" aria-labelledby="score-h">
      {/* 3 Transparent Score Meters (Requirement C) */}
      <div className="scores-triple-container">
        {/* 1. Resume Quality Score */}
        <div
          className={`score-unit quality-unit tone-${qualityTone} ${activeMetric === "quality" ? "selected-unit" : ""}`}
          onClick={() => setActiveMetric("quality")}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && setActiveMetric("quality")}
          title="Click to view detailed Resume Quality breakdown"
        >
          <div className="ring-wrapper">
            <div className={`neon-glow glow-${qualityTone}`}></div>
            <svg className="score-svg" viewBox="0 0 80 80" role="img" aria-label={`Resume quality score: ${resumeQualityScore}%`}>
              <circle className="ring-track" cx="40" cy="40" r={radius} />
              <circle
                className={`ring-meter meter-${qualityTone}`}
                cx="40" cy="40" r={radius}
                strokeDasharray={circumference}
                strokeDashoffset={qualityOffset}
              />
            </svg>
            <div className="ring-center-content">
              <span className="meter-val">{resumeQualityScore}</span>
              <span className="meter-sym">%</span>
            </div>
          </div>
          <div className="unit-label-group">
            <span className="unit-title">1. Resume Quality</span>
            <span className={`status-tag tag-${qualityTone}`}>{qualityLabel}</span>
          </div>
        </div>

        {/* 2. Job Match Fit Score */}
        <div
          className={`score-unit match-unit tone-${matchTone} ${activeMetric === "match" ? "selected-unit" : ""}`}
          onClick={() => setActiveMetric("match")}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && setActiveMetric("match")}
          title="Click to view Job Match Fit breakdown"
        >
          <div className="ring-wrapper">
            <div className={`neon-glow glow-${matchTone}`}></div>
            <svg className="score-svg" viewBox="0 0 80 80" role="img" aria-label={`Job match score: ${score}%`}>
              <circle className="ring-track" cx="40" cy="40" r={radius} />
              <circle
                className={`ring-meter meter-${matchTone}`}
                cx="40" cy="40" r={radius}
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
            <span className="unit-title">{isGeneralPurpose ? "2. General Readiness" : "2. Job Fit Match"}</span>
            <span className={`status-tag tag-${matchTone}`}>{matchLabel}</span>
          </div>
        </div>

        {/* 3. Formatting & Parsing Compatibility Score */}
        <div
          className={`score-unit ats-unit tone-${atsTone} ${activeMetric === "ats" ? "selected-unit" : ""}`}
          onClick={() => setActiveMetric("ats")}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && setActiveMetric("ats")}
          title="Click to view ATS Formatting breakdown"
        >
          <div className="ring-wrapper">
            <div className={`neon-glow glow-${atsTone}`}></div>
            <svg className="score-svg" viewBox="0 0 80 80" role="img" aria-label={`ATS compatibility score: ${atsScore}%`}>
              <circle className="ring-track" cx="40" cy="40" r={radius} />
              <circle
                className={`ring-meter meter-ats meter-${atsTone}`}
                cx="40" cy="40" r={radius}
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
            <span className="unit-title">3. ATS Format Fit</span>
            <span className={`status-tag tag-${atsTone}`}>{atsLabel}</span>
          </div>
        </div>
      </div>

      <div className="score-main-content">
        <div className="score-header-row">
          <div>
            <h2 id="score-h" className="job-heading">
              {title} {isGeneralPurpose && <span className="general-purpose-chip">🌐 General-Purpose Mode</span>}
            </h2>
            <div className="score-meta-badges">
              <span className={`mode-badge mode-${mode}`}>
                {mode === "ai" ? "✨ AI-Enhanced Specialist Review" : "⚡ Deterministic Transparent Engine"}
              </span>
              <span className="ats-compliance-badge">
                🛡️ 1-Page A4 ATS Compliant
              </span>
            </div>
          </div>

          <div className="breakdown-toggle-pill" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={activeMetric === "quality"}
              className={`toggle-tab ${activeMetric === "quality" ? "active" : ""}`}
              onClick={() => setActiveMetric("quality")}
            >
              Quality Factors
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeMetric === "match"}
              className={`toggle-tab ${activeMetric === "match" ? "active" : ""}`}
              onClick={() => setActiveMetric("match")}
            >
              Role Fit
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeMetric === "ats"}
              className={`toggle-tab ${activeMetric === "ats" ? "active" : ""}`}
              onClick={() => setActiveMetric("ats")}
            >
              ATS Structure
            </button>
          </div>
        </div>

        {/* Detailed Breakdown for the selected score */}
        <div className="breakdown-grid-modern">
          {activeMetric === "quality" && (
            Object.entries(qualityBreakdown && Object.keys(qualityBreakdown).length ? qualityBreakdown : {
              "Contact Completeness": 90,
              "Section Headings": 85,
              "Quantified Impact": 75,
              "Action Verbs": 80,
              "Content Depth": 85
            }).map(([k, v]) => (
              <div key={k} className="metric-pill-card">
                <div className="metric-info">
                  <span className="metric-name">{k}</span>
                  <span className="metric-number">{v}%</span>
                </div>
                <div className="metric-track">
                  <div
                    className={`metric-fill fill-${qualityTone}`}
                    style={{ width: `${Math.min(Math.max(v, 0), 100)}%` }}
                  />
                </div>
              </div>
            ))
          )}

          {activeMetric === "match" && (
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
          )}

          {activeMetric === "ats" && (
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

        {/* Strengths & Weaknesses Explanation Callout */}
        {scoreReasons?.quality_reasons && activeMetric === "quality" && (
          <div className="score-rationale-box">
            <span className="rationale-title">🔍 Quality Diagnostic Insights:</span>
            <ul className="rationale-list">
              {scoreReasons.quality_reasons.strengths?.map((s, idx) => (
                <li key={`str-${idx}`} className="rationale-item strength">
                  <span className="bullet-indicator">✓</span> {s}
                </li>
              ))}
              {scoreReasons.quality_reasons.weaknesses?.map((w, idx) => (
                <li key={`weak-${idx}`} className="rationale-item weakness">
                  <span className="bullet-indicator">⚠️</span> {w}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
