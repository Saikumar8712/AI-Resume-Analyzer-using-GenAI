import { useEffect, useState, useCallback } from "react";
import UploadForm from "./components/UploadForm.jsx";
import ResumeAnalysisReport from "./components/ResumeAnalysisReport.jsx";
import History from "./components/History.jsx";
import LoadingScreen from "./components/LoadingScreen.jsx";
import * as api from "./api.js";

export default function App() {
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [backendOnline, setBackendOnline] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("resume_theme") || "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("resume_theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const refreshHistory = useCallback(async () => {
    try {
      const data = await api.getHistory();
      setHistory(data);
      setBackendOnline(true);
    } catch {
      setBackendOnline(false);
    }
  }, []);

  useEffect(() => {
    let mounted = true;
    const startTime = Date.now();
    const MIN_LOAD_TIME = 1000; // Keep icon and loading screen visible for at least 1.0 sec
    const MAX_LOAD_TIME = 2500; // Stay up to 2.5 sec maximum

    // Safety timeout ensures user is never stuck for more than 2.5 sec
    const safetyTimer = setTimeout(() => {
      if (mounted) finish();
    }, MAX_LOAD_TIME);

    refreshHistory().finally(() => {
      const elapsed = Date.now() - startTime;
      const remainingTime = Math.max(0, MIN_LOAD_TIME - elapsed);
      // Ensure at least 1.0 sec icon display time, up to 2.5 sec
      setTimeout(() => {
        if (mounted) finish();
      }, remainingTime);
    });

    let finished = false;
    function finish() {
      if (finished) return;
      finished = true;
      setIsFadingOut(true);
      // Smooth 1.0s load-out fade transition
      setTimeout(() => {
        if (mounted) setInitialLoading(false);
      }, 1000);
    }

    return () => {
      mounted = false;
      clearTimeout(safetyTimer);
    };
  }, [refreshHistory]);

  const run = async (file, jd, title) => {
    setLoading(true);
    setError("");
    setReport(null);
    try {
      const res = await api.analyze(file, jd, title);
      setReport(res);
      setBackendOnline(true);
      refreshHistory();
    } catch (e) {
      setError(e.message || "Failed to analyze resume.");
    } finally {
      setLoading(false);
    }
  };

  const open = async (id) => {
    setError("");
    try {
      const item = await api.getAnalysis(id);
      setReport(item);
    } catch (e) {
      setError(e.message || "Could not load saved analysis.");
    }
  };

  const del = async (id) => {
    try {
      await api.deleteAnalysis(id);
      if (report?.id === id) setReport(null);
      refreshHistory();
    } catch (e) {
      setError(e.message || "Failed to delete item.");
    }
  };

  return (
    <>
      {initialLoading && <LoadingScreen isFading={isFadingOut} />}
      <div className="app-container">
      <header className="top-nav">
        <div className="nav-brand">
          <div className="brand-logo">🎯</div>
          <div>
            <h1 className="brand-title">ResumeMatch AI</h1>
            <p className="brand-subtitle">ATS Keyword Matching, Skill Diagnostics & Tailored Interview Coaching</p>
          </div>
        </div>

        <div className="nav-controls">
          {/* Dedicated Backend Server Indicator */}
          <div className="server-indicator-badge" title="FastAPI Backend Microservice Status">
            <span className="server-chip-icon">🖥️</span>
            <span className="server-label">Backend API:</span>
            <span className={`status-dot-pill ${backendOnline ? "online" : backendOnline === false ? "offline" : "checking"}`}>
              <span className="status-dot"></span>
              {backendOnline ? "8000 Live" : backendOnline === false ? "Offline" : "Checking..."}
            </span>
            {backendOnline === false && (
              <button type="button" className="retry-btn" onClick={refreshHistory} title="Retry connecting to port 8000">
                ↻ Reconnect
              </button>
            )}
          </div>

          {/* Separate Dark / Light Mode Toggle Button */}
          <button
            type="button"
            className="theme-switcher-btn"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "Senior Developer Light" : "Cyber Dark"} mode`}
            title={`Toggle Theme (Current: ${theme === "dark" ? "Dark" : "Light"})`}
          >
            <span className="theme-btn-icon">{theme === "dark" ? "☀️" : "🌙"}</span>
            <span className="theme-btn-text">{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>
          </button>
        </div>
      </header>

      <main className="layout">
        <aside className="sidebar-col">
          <UploadForm
            onSubmit={run}
            loading={loading}
            onReset={() => {
              setReport(null);
              setError("");
            }}
          />

          <section className="panel history-panel">
            <div className="panel-header">
              <h2 className="panel-title">Past Analyses</h2>
              <span className="count-pill">{history.length}</span>
            </div>
            <History
              items={history}
              onOpen={open}
              onDelete={del}
              activeId={report?.id}
            />
          </section>
        </aside>

        <section className="main-col">
          {error && (
            <div className="error-banner" role="alert">
              <span className="error-icon">⚠️</span>
              <div className="error-text">{error}</div>
              <button type="button" className="close-banner" onClick={() => setError("")}>✕</button>
            </div>
          )}

          {loading && (
            <div className="panel loading-panel" role="status">
              <div className="pulse-spinner"></div>
              <h3>Analyzing your resume against target requirements...</h3>
              <p className="loading-desc">Extracting text, comparing skills, measuring structure, and crafting practice questions.</p>
            </div>
          )}

          {report && !loading && <ResumeAnalysisReport data={report} />}

          {!report && !loading && (
            <div className="panel hero-empty-panel">
              <div className="hero-art">🚀</div>
              <h2>Ready to Optimize Your Resume?</h2>
              <p>Upload your PDF resume on the left and paste the job description to get:</p>
              <div className="features-preview">
                <div className="feat-chip">📊 Objective Match Score</div>
                <div className="feat-chip">🔍 Matched & Missing Skills</div>
                <div className="feat-chip">📝 Section Completeness Check</div>
                <div className="feat-chip">🎙️ Tailored Interview Questions</div>
                <div className="feat-chip">📄 Downloadable PDF Report</div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
    </>
  );
}
