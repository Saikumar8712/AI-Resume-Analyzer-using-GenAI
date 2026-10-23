const API_BASE_URL = (
  import.meta.env.VITE_API_URL || ""
).replace(/\/+$/, "");

async function handle(res) {
  if (!res.ok) {
    let msg = "Something went wrong. Try again.";
    try {
      msg = (await res.json()).detail || msg;
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const analyze = (file, jd, title) => {
  const f = new FormData();
  f.append("resume", file);
  f.append("job_description", jd);
  f.append("job_title", title || "Target role");

  return fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: f,
  }).then(handle);
};

export const getHistory = () =>
  fetch(`${API_BASE_URL}/api/history`).then(handle);

export const getAnalysis = (id) =>
  fetch(`${API_BASE_URL}/api/history/${id}`).then(handle);

export const deleteAnalysis = (id) =>
  fetch(`${API_BASE_URL}/api/history/${id}`, {
    method: "DELETE",
  }).then(handle);

export const pdfUrl = (id) =>
  `${API_BASE_URL}/api/report/${id}/pdf`;
