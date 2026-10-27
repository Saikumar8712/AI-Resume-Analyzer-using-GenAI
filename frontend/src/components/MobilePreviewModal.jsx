import React, { useState, useEffect } from "react";
import MobileResumeDocView from "./MobileResumeDocView.jsx";
import { atsResumeUrl } from "../api.js";

/**
 * MobilePreviewModal
 * Fullscreen mobile-friendly modal for viewing, inspecting, zooming,
 * and downloading the 1-page ATS Resume on any phone or desktop screen.
 */
export default function MobilePreviewModal({ isOpen, onClose, resumeData, fallbackData, targetId }) {
  const [zoom, setZoom] = useState(100);
  const [modalMode, setModalMode] = useState("doc"); // 'doc' | 'pdf'

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
      const handleKeyDown = (e) => {
        if (e.key === "Escape") onClose();
      };
      window.addEventListener("keydown", handleKeyDown);
      return () => {
        document.body.style.overflow = "";
        window.removeEventListener("keydown", handleKeyDown);
      };
    } else {
      document.body.style.overflow = "";
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const zoomIn = () => setZoom((prev) => Math.min(prev + 15, 160));
  const zoomOut = () => setZoom((prev) => Math.max(prev - 15, 60));
  const resetZoom = () => setZoom(100);

  return (
    <div className="mobile-modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-label="1-Page Resume Fullscreen Preview">
      <div className="mobile-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Modal Top Bar */}
        <header className="mobile-modal-header">
          <div className="modal-title-wrap">
            <span className="modal-icon">👁️</span>
            <div>
              <h3 className="modal-title">1-Page ATS Resume Preview</h3>
              <span className="modal-subtitle">Screen-fitted · Verified 1-Page A4 ATS Layout</span>
            </div>
          </div>

          <div className="modal-actions-wrap">
            {/* View Mode Toggle */}
            <div className="modal-view-toggle">
              <button
                type="button"
                className={`modal-toggle-btn ${modalMode === "doc" ? "active" : ""}`}
                onClick={() => setModalMode("doc")}
                title="View formatted mobile document"
              >
                📱 Mobile View
              </button>
              <button
                type="button"
                className={`modal-toggle-btn ${modalMode === "pdf" ? "active" : ""}`}
                onClick={() => setModalMode("pdf")}
                title="View embedded PDF file"
              >
                📑 PDF View
              </button>
            </div>

            {/* Zoom Controls */}
            {modalMode === "doc" && (
              <div className="modal-zoom-bar">
                <button type="button" className="zoom-btn" onClick={zoomOut} title="Zoom Out">
                  -
                </button>
                <button type="button" className="zoom-display-btn" onClick={resetZoom} title="Reset Zoom">
                  {zoom}%
                </button>
                <button type="button" className="zoom-btn" onClick={zoomIn} title="Zoom In">
                  +
                </button>
              </div>
            )}

            {/* External Tab / Download */}
            <a
              className="modal-action-btn secondary-btn"
              href={atsResumeUrl(targetId)}
              target="_blank"
              rel="noopener noreferrer"
              title="Open PDF in a new tab"
            >
              ↗ Open in Tab
            </a>
            <a
              className="modal-action-btn download-btn"
              href={`${atsResumeUrl(targetId)}?download=true`}
              download={`ats-resume-${targetId}.pdf`}
              title="Download ATS PDF"
            >
              📄 Download PDF
            </a>

            {/* Close Button */}
            <button
              type="button"
              className="modal-close-btn"
              onClick={onClose}
              aria-label="Close modal preview"
            >
              ✕
            </button>
          </div>
        </header>

        {/* Modal Content Body */}
        <div className="mobile-modal-body">
          {modalMode === "doc" ? (
            <div className="modal-doc-wrapper">
              <MobileResumeDocView
                resumeData={resumeData}
                fallbackData={fallbackData}
                targetId={targetId}
                scale={zoom}
              />
            </div>
          ) : (
            <div className="modal-pdf-wrapper">
              <object
                data={`${atsResumeUrl(targetId)}#toolbar=0&navpanes=0&view=FitH`}
                type="application/pdf"
                className="modal-pdf-object"
                aria-label="PDF Preview"
              >
                <iframe
                  title="PDF Preview"
                  src={`${atsResumeUrl(targetId)}#toolbar=0&navpanes=0&view=FitH`}
                  className="modal-pdf-object"
                >
                  <div className="pdf-mobile-fallback">
                    <p>Inline PDF is not supported by your mobile browser.</p>
                    <div className="fallback-buttons">
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => setModalMode("doc")}
                      >
                        📱 Switch to Mobile Document View
                      </button>
                      <a
                        className="btn btn-download"
                        href={atsResumeUrl(targetId)}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        ↗ Open in Native PDF Viewer
                      </a>
                    </div>
                  </div>
                </iframe>
              </object>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
