async function handle(res) {
  if (!res.ok) {
    let msg = "Something went wrong. Try again.";
    try { msg = (await res.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}
export const analyze = (file, jd, title) => {
  const f = new FormData();
  f.append("resume", file); f.append("job_description", jd); f.append("job_title", title || "Target role");
  return fetch("/api/analyze", { method: "POST", body: f }).then(handle);
};
export const getHistory = () => fetch("/api/history").then(handle);
export const getAnalysis = (id) => fetch(`/api/history/${id}`).then(handle);
export const deleteAnalysis = (id) => fetch(`/api/history/${id}`, { method: "DELETE" }).then(handle);
export const pdfUrl = (id) => `/api/report/${id}/pdf`;
