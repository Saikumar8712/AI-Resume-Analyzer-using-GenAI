import { useState } from "react";
import ScoreCard from "./ScoreCard.jsx";
import SkillBadge from "./SkillBadge.jsx";
import { pdfUrl, atsResumeUrl } from "../api.js";

export default function ResumeAnalysisReport({ data }) {
  const [tab, setTab] = useState("need_to_improve"); // Default to Need to Improve or overview
  const [copiedSection, setCopiedSection] = useState("");

  if (!data) return null;

  const matchedSkills = data.matched_skills || [];
  const missingSkills = data.missing_skills || [];
  const extraSkills = data.extra_skills || [];
  const needToImprove = data.need_to_improve || [];
  const resumeImprovements = data.resume_improvements || [];
  const bulletRewrites = data.bullet_rewrites || [];
  const recommendations = data.recommendations || [];
  const questions = data.questions || [];
  const checks = data.checks || {};
  const jobRecommendations = data.job_recommendations || [];
  const atsScore = data.ats_score ?? data.score ?? 0;
  const atsGrade = data.ats_grade || "A";
  const atsBreakdown = data.ats_breakdown || {};

  const copyToClipboard = (text, section) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(""), 2000);
  };

  const tabs = [
    { id: "need_to_improve", label: `⚡ Need to Improve (${needToImprove.length})`, badgeClass: "tab-badge-warn" },
    { id: "overview", label: `Overview & Matched (${matchedSkills.length})` },
    { id: "ats_improvements", label: `📋 ATS Resume Fixes (${resumeImprovements.length})` },
    ...(jobRecommendations.length > 0 ? [{ id: "job_recommendations", label: `💼 Job Matches (${jobRecommendations.length})` }] : []),
    ...(bulletRewrites.length > 0 ? [{ id: "bullet_rewrites", label: `✨ Bullet Rewrites (${bulletRewrites.length})` }] : []),
    { id: "questions", label: `🎙️ Interview Prep (${questions.length})` },
  ];

  return (
    <article className="report-card" aria-live="polite">
      <ScoreCard
        score={data.score}
        atsScore={atsScore}
        atsGrade={atsGrade}
        title={data.job_title}
        mode={data.mode}
        breakdown={data.breakdown}
        atsBreakdown={atsBreakdown}
      />

      {data.summary && (
        <div className="summary-banner">
          <div className="summary-icon">💡</div>
          <div className="summary-text">{data.summary}</div>
        </div>
      )}

      <div className="tabs-bar" role="tablist">
        {tabs.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            className={`tab-btn ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="tab-body">
        {/* 1. Dedicated 'Need to Improve' Section */}
        {tab === "need_to_improve" && (
          <div className="need-to-improve-container">
            <div className="section-intro-card">
              <div className="intro-header flex-between">
                <div>
                  <h3 className="section-highlight-title">⚠️ Skills You Need to Improve & Missing Credentials</h3>
                  <p className="section-highlight-desc">
                    These skills are demanded by the job requirements but were not detected in your uploaded resume PDF.
                    Follow the tailored advice below to acquire, build, or add evidence for them.
                  </p>
                </div>
                {needToImprove.length > 0 && (
                  <button
                    type="button"
                    className="copy-btn glow-btn"
                    onClick={() =>
                      copyToClipboard(
                        needToImprove.map((item) => `Skill: ${item.skill}\nPriority: ${item.priority}\nAdvice: ${item.suggestion}`).join("\n\n"),
                        "need_to_improve"
                      )
                    }
                  >
                    {copiedSection === "need_to_improve" ? "✓ Copied Plan!" : "📋 Copy Improvement Plan"}
                  </button>
                )}
              </div>
            </div>

            {needToImprove.length > 0 ? (
              <div className="need-to-improve-grid">
                {needToImprove.map((item, idx) => (
                  <div key={idx} className="improve-skill-card">
                    <div className="improve-card-top">
                      <div className="skill-title-group">
                        <span className="skill-name-badge">{item.skill}</span>
                        <span className="skill-status-tag">Missing in Resume</span>
                      </div>
                      <span className={`priority-pill priority-${item.priority ? item.priority.toLowerCase() : "high"}`}>
                        {item.priority || "High"} Priority
                      </span>
                    </div>

                    <div className="improve-advice-box">
                      <span className="advice-label">🎯 How to Improve & Add to Resume:</span>
                      <p className="advice-text">{item.suggestion}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state-perfect">
                <span className="perfect-icon">🎉</span>
                <h4>Zero Skill Gaps Detected!</h4>
                <p>Your resume satisfies all primary skills mentioned in this job description.</p>
              </div>
            )}
          </div>
        )}

        {/* 2. Overview & Matched Skills */}
        {tab === "overview" && (
          <div className="overview-content">
            <div className="skills-row">
              <section className="skills-box matched-box">
                <div className="box-header">
                  <h3>✅ Matched Core Skills ({matchedSkills.length})</h3>
                  <span className="box-sub">Skills verified in your extracted PDF</span>
                </div>
                <ul className="badges-list">
                  {matchedSkills.length ? (
                    matchedSkills.map((s) => <SkillBadge key={s} label={s} variant="match" />)
                  ) : (
                    <li className="empty-notice">No required core skills detected in resume.</li>
                  )}
                </ul>
              </section>

              <section className="skills-box missing-box">
                <div className="box-header flex-between">
                  <div>
                    <h3>⚠️ Skills to Strengthen ({missingSkills.length})</h3>
                    <span className="box-sub">Gaps identified in target role</span>
                  </div>
                  <button type="button" className="quick-switch-btn" onClick={() => setTab("need_to_improve")}>
                    View Detailed Advice →
                  </button>
                </div>
                <ul className="badges-list">
                  {missingSkills.length ? (
                    missingSkills.map((s) => <SkillBadge key={s} label={s} variant="gap" />)
                  ) : (
                    <li className="empty-notice ok">All required skills present!</li>
                  )}
                </ul>
              </section>
            </div>

            {extraSkills.length > 0 && (
              <section className="skills-box extra-box">
                <div className="box-header">
                  <h3>➕ Additional Discovered Skills ({extraSkills.length})</h3>
                  <span className="box-sub">Valuable strengths found in your resume</span>
                </div>
                <ul className="badges-list">
                  {extraSkills.map((s) => (
                    <SkillBadge key={s} label={s} variant="extra" />
                  ))}
                </ul>
              </section>
            )}

            <section className="recs-box">
              <div className="box-header flex-between">
                <div>
                  <h3>🎯 Executive Recommendations</h3>
                  <span className="box-sub">Tailoring steps to maximize callback rates</span>
                </div>
                <button
                  type="button"
                  className="copy-btn"
                  onClick={() => copyToClipboard(recommendations.join("\n• "), "recs")}
                >
                  {copiedSection === "recs" ? "✓ Copied!" : "📋 Copy"}
                </button>
              </div>
              <ol className="recs-list">
                {recommendations.map((r, i) => (
                  <li key={i} className="rec-item">
                    <span className="rec-num">{i + 1}</span>
                    <span className="rec-text">{r}</span>
                  </li>
                ))}
              </ol>
            </section>
          </div>
        )}

        {/* 3. Dedicated ATS & Resume Extracted PDF Fixes */}
        {tab === "ats_improvements" && (
          <div className="ats-fixes-container">
            <div className="ats-summary-banner">
              <div className="ats-score-display flex-between">
                <div>
                  <span className="ats-badge-large">ATS Score: {atsScore}%</span>
                  <span className="ats-grade-tag">Rating: {atsGrade}</span>
                </div>
                <a
                  className="btn btn-download glow-btn"
                  href={atsResumeUrl(data.id)}
                  download={`ats-resume-${data.id}.pdf`}
                  title="Download an ATS-compliant, single-column formatted version of your resume"
                >
                  📄 Download ATS-Friendly Resume (PDF)
                </a>
              </div>
              <p className="ats-desc">
                Based on parsing your extracted PDF document, here are specific structural and content improvements
                to ensure applicant tracking systems (Workday, Greenhouse, Lever, Taleo) parse your qualifications accurately.
              </p>
            </div>

            <section className="improvements-section">
              <div className="box-header flex-between">
                <div>
                  <h3>📝 What You Need to Improve in Your Extracted Resume</h3>
                  <span className="box-sub">Direct fixes based on your actual document content</span>
                </div>
                <button
                  type="button"
                  className="copy-btn"
                  onClick={() => copyToClipboard(resumeImprovements.join("\n• "), "resume_improvements")}
                >
                  {copiedSection === "resume_improvements" ? "✓ Copied!" : "📋 Copy Fixes"}
                </button>
              </div>

              <div className="improvements-cards-list">
                {resumeImprovements.map((imp, idx) => (
                  <div key={idx} className="improvement-item-card">
                    <span className="imp-icon">💡</span>
                    <div className="imp-content">
                      <span className="imp-title">Resume Recommendation #{idx + 1}</span>
                      <p className="imp-text">{imp}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="checks-sub-section">
              <div className="box-header">
                <h3>🔍 Document Structure Checkpoints</h3>
                <span className="box-sub">Standard screening sections detected in your PDF</span>
              </div>
              <ul className="checks-grid">
                {Object.entries(checks).map(([k, ok]) => (
                  <li key={k} className={`check-card ${ok ? "check-pass" : "check-fail"}`}>
                    <span className="check-icon">{ok ? "✓" : "✕"}</span>
                    <div className="check-info">
                      <span className="check-title">{k}</span>
                      <span className="check-status">{ok ? "Detected in document" : "Missing or not detected"}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        )}

        {/* Dedicated AI Bullet Rewrites Tab */}
        {tab === "bullet_rewrites" && (
          <div className="bullet-rewrites-container">
            <div className="section-intro-card">
              <div className="intro-header flex-between">
                <div>
                  <h3 className="section-highlight-title">✨ AI High-Impact Bullet Point Rewrites</h3>
                  <p className="section-highlight-desc">
                    Transform weak or unquantified resume bullet points into high-impact, results-driven achievements with measurable impact.
                  </p>
                </div>
                {bulletRewrites.length > 0 && (
                  <button
                    type="button"
                    className="copy-btn glow-btn"
                    onClick={() =>
                      copyToClipboard(
                        bulletRewrites.map((b) => `Original: ${b.original}\nRewrite: ${b.improved}`).join("\n\n"),
                        "bullet_rewrites"
                      )
                    }
                  >
                    {copiedSection === "bullet_rewrites" ? "✓ Copied Rewrites!" : "📋 Copy Rewrites"}
                  </button>
                )}
              </div>
            </div>

            <div className="rewrites-grid">
              {bulletRewrites.map((item, idx) => (
                <div key={idx} className="rewrite-card">
                  <div className="rewrite-col rewrite-original">
                    <span className="rewrite-tag original-tag">⚠️ Original (Weak / Unquantified)</span>
                    <p className="rewrite-text">{item.original}</p>
                  </div>
                  <div className="rewrite-divider">➔</div>
                  <div className="rewrite-col rewrite-improved">
                    <span className="rewrite-tag improved-tag">🚀 AI High-Impact Rewrite</span>
                    <p className="rewrite-text">{item.improved}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Dedicated Relevant Job Matches Tab */}
        {tab === "job_recommendations" && (
          <div className="need-to-improve-container">
            <div className="section-intro-card">
              <div className="intro-header flex-between">
                <div>
                  <h3 className="section-highlight-title">💼 Recommended Job Roles for Your Profile</h3>
                  <p className="section-highlight-desc">
                    Target roles aligned with your verified technical skills, core competencies, and career trajectory.
                  </p>
                </div>
              </div>
            </div>

            <div className="need-to-improve-grid">
              {jobRecommendations.map((job, idx) => (
                <div key={idx} className="improve-skill-card">
                  <div className="improve-card-top">
                    <div className="skill-title-group">
                      <span className="skill-name-badge">{job.title}</span>
                      <span className="skill-status-tag">{job.match_score}% Skill Fit</span>
                    </div>
                    <span className="priority-pill priority-high">
                      {job.match_level}
                    </span>
                  </div>

                  <div className="improve-advice-box">
                    <span className="advice-label">🎯 Why You Match:</span>
                    <p className="advice-text">{job.reason}</p>
                    {job.matching_skills && job.matching_skills.length > 0 && (
                      <p className="advice-text" style={{ marginTop: "6px" }}>
                        <b>Matching Strengths:</b> {job.matching_skills.join(", ")}
                      </p>
                    )}
                    {job.growth_skills && job.growth_skills.length > 0 && (
                      <p className="advice-text" style={{ marginTop: "4px" }}>
                        <b>Growth Skills to Add:</b> {job.growth_skills.join(", ")}
                      </p>
                    )}
                    {job.company && (
                      <div style={{ fontSize: "0.82rem", color: "var(--text-muted, #94a3b8)", marginTop: "8px", borderTop: "1px dashed rgba(255,255,255,0.1)", paddingTop: "6px" }}>
                        🏢 <b>{job.company}</b> &nbsp;|&nbsp; 📍 {job.location || "Remote / Hybrid"} ({job.work_mode || "Flexible"}) &nbsp;|&nbsp; 🎓 {job.experience_level || "All Levels"}
                      </div>
                    )}
                    {job.apply_url && (
                      <div style={{ marginTop: "8px", display: "flex", justifyContent: "flex-end" }}>
                        <a
                          href={job.apply_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="copy-btn glow-btn"
                          style={{ fontSize: "0.78rem", padding: "4px 10px", textDecoration: "none" }}
                        >
                          🔍 Search Verified Listings ↗
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 4. Interview Prep */}
        {tab === "questions" && (
          <div className="questions-content">
            <div className="box-header flex-between">
              <div>
                <h3>🎙️ Curated Practice Questions</h3>
                <span className="box-sub">Tailored to your matched strengths and missing gaps</span>
              </div>
              <button
                type="button"
                className="copy-btn"
                onClick={() => copyToClipboard(questions.map((q, i) => `${i + 1}. ${q}`).join("\n\n"), "questions")}
              >
                {copiedSection === "questions" ? "✓ Copied All!" : "📋 Copy All"}
              </button>
            </div>
            <ol className="questions-list">
              {questions.map((q, i) => (
                <li key={i} className="question-card">
                  <div className="q-badge">Q{i + 1}</div>
                  <div className="q-text">{q}</div>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>

      <div className="report-footer">
        <p className="disclaimer-note">
          ℹ️ {data.disclaimer}
        </p>
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", justifyContent: "flex-end" }}>
          <a
            className="btn btn-download glow-btn"
            href={atsResumeUrl(data.id)}
            download={`ats-resume-${data.id}.pdf`}
            title="Download clean, single-column ATS-formatted resume"
          >
            📄 Download ATS-Friendly Resume
          </a>
          <a
            className="btn btn-download"
            href={pdfUrl(data.id)}
            download={`report-${data.id}.pdf`}
          >
            📥 Download Complete Report
          </a>
        </div>
      </div>
    </article>
  );
}

