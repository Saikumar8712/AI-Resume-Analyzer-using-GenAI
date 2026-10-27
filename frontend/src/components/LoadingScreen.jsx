import React from "react";

/**
 * LoadingScreen
 * Premium branded initial loading screen matching ResumeMatch AI visual identity,
 * color palette, typography ('Outfit' / 'Plus Jakarta Sans'), and glassmorphism.
 */
export default function LoadingScreen({ isFading = false }) {
  return (
    <div
      className={`app-loading-overlay ${isFading ? "fade-out" : ""}`}
      role="status"
      aria-live="polite"
      aria-label="Loading ResumeMatch AI application"
    >
      <div className="loading-ambient-glow" aria-hidden="true" />

      <div className="loading-card">
        {/* Animated Brand Logo with Ambient Pulsing Glow & Hover Interactivity */}
        <div className="loading-logo-wrapper" title="ResumeMatch AI Engine">
          <div className="loading-radar-wave" aria-hidden="true" />
          <div className="loading-ring-pulse" aria-hidden="true" />
          <div className="loading-brand-icon">
            <span className="loading-icon-target">🎯</span>
          </div>
        </div>

        {/* Brand Typography */}
        <div className="loading-text-group">
          <h1 className="loading-brand-title">ResumeMatch AI</h1>
          <p className="loading-brand-subtitle">
            ATS Keyword Matching &amp; Skill Diagnostics
          </p>
        </div>

        {/* Elegant Animated Progress Track */}
        <div className="loading-progress-container" aria-hidden="true">
          <div className="loading-progress-bar" />
        </div>

        {/* Dynamic Status Pill */}
        <div className="loading-status-pill">
          <span className="loading-status-dot" aria-hidden="true" />
          <span className="loading-status-text">
            Initializing ATS Engine &amp; Workspace...
          </span>
        </div>
      </div>
    </div>
  );
}
