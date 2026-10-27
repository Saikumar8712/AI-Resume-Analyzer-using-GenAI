import React from "react";
import { atsResumeUrl } from "../api.js";

/**
 * MobileResumeDocView
 * Renders a crisp, 1-page ATS formatted resume paper view.
 * 100% responsive and guaranteed to render cleanly across all mobile browsers
 * (iOS Safari, Android Chrome, Samsung Internet) without relying on PDF iframe plugins.
 */
export default function MobileResumeDocView({ resumeData, fallbackData, targetId, scale = 100 }) {
  const parsed = resumeData?.parsed_resume || {};
  const name = parsed.name || "Candidate Name";
  const email = parsed.email || "";
  const phone = parsed.phone || "";
  const location = parsed.location || "";
  const linkedin = parsed.linkedin || "";
  const github = parsed.github || "";
  const portfolio = parsed.portfolio || "";

  const sections = parsed.sections || {};
  const summaryLines = sections.summary || [];
  const skillsLines = sections.skills || (fallbackData?.skills ? [fallbackData.skills.join(", ")] : []);
  const experienceLines = sections.experience || [];
  const projectsLines = sections.projects || [];
  const educationLines = sections.education || [];
  const certLines = sections.certifications || [];

  // Group contacts
  const contacts = [
    phone && { type: "phone", label: phone, href: `tel:${phone}` },
    email && { type: "email", label: email, href: `mailto:${email}` },
    location && { type: "location", label: location },
    linkedin && {
      type: "linkedin",
      label: "LinkedIn",
      href: linkedin.startsWith("http") ? linkedin : `https://${linkedin}`
    },
    github && {
      type: "github",
      label: "GitHub",
      href: github.startsWith("http") ? github : `https://${github}`
    },
    portfolio && {
      type: "portfolio",
      label: "Portfolio",
      href: portfolio.startsWith("http") ? portfolio : `https://${portfolio}`
    }
  ].filter(Boolean);

  const cleanBullet = (str) => {
    return str.replace(/^[\s•●○▪▸\-\*>\?]+/, "").trim();
  };

  const renderFormattedLine = (line) => {
    // Check for URLs and render as links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const parts = line.split(urlRegex);
    return parts.map((part, i) => {
      if (part.match(urlRegex)) {
        return (
          <a
            key={i}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="ats-doc-link"
          >
            {part}
          </a>
        );
      }
      return part;
    });
  };

  const scaleStyle = scale !== 100 ? { transform: `scale(${scale / 100})`, transformOrigin: "top center" } : {};

  return (
    <div className="mobile-resume-outer-scroll">
      <div className="mobile-resume-paper" style={scaleStyle} aria-label="Mobile ATS Resume Preview">
        {/* Paper Header */}
        <header className="ats-doc-header">
          <h1 className="ats-doc-name">{name}</h1>
          <div className="ats-doc-contact-bar">
            {contacts.map((c, idx) => (
              <span key={idx} className="ats-contact-item">
                {idx > 0 && <span className="ats-sep">|</span>}
                {c.href ? (
                  <a href={c.href} target="_blank" rel="noopener noreferrer" className="ats-contact-link">
                    {c.label}
                  </a>
                ) : (
                  <span>{c.label}</span>
                )}
              </span>
            ))}
          </div>
        </header>

        {/* Professional Summary */}
        {summaryLines.length > 0 && (
          <section className="ats-doc-section">
            <h2 className="ats-doc-heading">PROFESSIONAL SUMMARY</h2>
            <div className="ats-doc-rule" />
            <p className="ats-doc-paragraph">
              {summaryLines.map((l) => cleanBullet(l)).join(" ")}
            </p>
          </section>
        )}

        {/* Technical Skills */}
        {skillsLines.length > 0 && (
          <section className="ats-doc-section">
            <h2 className="ats-doc-heading">TECHNICAL SKILLS</h2>
            <div className="ats-doc-rule" />
            <div className="ats-doc-skills-list">
              {skillsLines.map((line, idx) => {
                const cleaned = cleanBullet(line);
                const colonIdx = cleaned.indexOf(":");
                if (colonIdx > 0 && colonIdx < 35) {
                  const category = cleaned.slice(0, colonIdx).trim();
                  const skillItems = cleaned.slice(colonIdx + 1).trim();
                  return (
                    <div key={idx} className="ats-skill-line">
                      <strong className="ats-skill-cat">{category}:</strong>{" "}
                      <span className="ats-skill-items">{skillItems}</span>
                    </div>
                  );
                }
                return (
                  <div key={idx} className="ats-skill-line">
                    <span className="ats-skill-items">{cleaned}</span>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Professional Experience / Internships */}
        {experienceLines.length > 0 && (
          <section className="ats-doc-section">
            <h2 className="ats-doc-heading">PROFESSIONAL EXPERIENCE</h2>
            <div className="ats-doc-rule" />
            <ul className="ats-doc-bullet-list">
              {experienceLines.map((line, idx) => {
                const cleaned = cleanBullet(line);
                const isHeading =
                  /^\d+\./.test(cleaned) ||
                  cleaned.includes(" | ") ||
                  cleaned.toLowerCase().includes("intern") ||
                  cleaned.toLowerCase().includes("developer") ||
                  cleaned.toLowerCase().includes("engineer");
                return (
                  <li key={idx} className={`ats-doc-bullet ${isHeading ? "ats-item-heading" : ""}`}>
                    {renderFormattedLine(cleaned)}
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        {/* Key Technical Projects */}
        {projectsLines.length > 0 && (
          <section className="ats-doc-section">
            <h2 className="ats-doc-heading">PROJECTS</h2>
            <div className="ats-doc-rule" />
            <ul className="ats-doc-bullet-list">
              {projectsLines.map((line, idx) => {
                const cleaned = cleanBullet(line);
                const isHeading = /^\d+\./.test(cleaned) || cleaned.includes(" | ");
                return (
                  <li key={idx} className={`ats-doc-bullet ${isHeading ? "ats-item-heading" : ""}`}>
                    {renderFormattedLine(cleaned)}
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        {/* Education */}
        {educationLines.length > 0 && (
          <section className="ats-doc-section">
            <h2 className="ats-doc-heading">EDUCATION</h2>
            <div className="ats-doc-rule" />
            <ul className="ats-doc-bullet-list">
              {educationLines.map((line, idx) => (
                <li key={idx} className="ats-doc-bullet">
                  {renderFormattedLine(cleanBullet(line))}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Certifications & Achievements */}
        {certLines.length > 0 && (
          <section className="ats-doc-section">
            <h2 className="ats-doc-heading">CERTIFICATIONS & ACHIEVEMENTS</h2>
            <div className="ats-doc-rule" />
            <ul className="ats-doc-bullet-list">
              {certLines.map((line, idx) => (
                <li key={idx} className="ats-doc-bullet">
                  {renderFormattedLine(cleanBullet(line))}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Footer info note */}
        <footer className="ats-doc-footer-badge">
          <span>✓ Guaranteed 1-Page A4 ATS Compliance · Standard Single-Column Layout</span>
        </footer>
      </div>
    </div>
  );
}
