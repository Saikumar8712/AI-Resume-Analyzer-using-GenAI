export default function History({ items = [], onOpen, onDelete, activeId }) {
  if (!items.length) {
    return (
      <div className="empty-history">
        <span className="empty-icon">🗂️</span>
        <p className="muted">No previous analyses saved yet.</p>
        <small className="muted-sub">Uploaded analyses will be stored here automatically.</small>
      </div>
    );
  }

  return (
    <ul className="history-list">
      {items.map((h) => {
        const tone = h.score >= 75 ? "high" : h.score >= 50 ? "mid" : "low";
        const dateStr = h.created_at ? h.created_at.slice(0, 10) : "";
        const isActive = activeId === h.id;

        return (
          <li key={h.id} className={`history-item ${isActive ? "active-item" : ""}`}>
            <button
              type="button"
              className="history-main-btn"
              onClick={() => onOpen(h.id)}
            >
              <div className={`history-score score-${tone}`}>{h.score}%</div>
              <div className="history-details">
                <span className="history-title">{h.job_title || "Target Role"}</span>
                <span className="history-meta">{h.filename} · {dateStr}</span>
              </div>
            </button>
            <button
              type="button"
              className="history-delete-btn"
              aria-label={`Delete analysis for ${h.job_title}`}
              onClick={(e) => {
                e.stopPropagation();
                onDelete(h.id);
              }}
              title="Delete record"
            >
              🗑️
            </button>
          </li>
        );
      })}
    </ul>
  );
}
