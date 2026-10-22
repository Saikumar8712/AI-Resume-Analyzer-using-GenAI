export default function SkillBadge({ label, variant = "match" }) {
  const icon = variant === "match" ? "✓" : variant === "extra" ? "✦" : "!";
  return (
    <li className={`badge badge-${variant}`}>
      <span className="badge-icon" aria-hidden="true">{icon}</span>
      <span className="badge-text">{label}</span>
    </li>
  );
}
