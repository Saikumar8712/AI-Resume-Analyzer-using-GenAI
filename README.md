<<<<<<< HEAD
# AI Resume Analyzer & Interview Prep

Upload a PDF resume + paste a job description. Get an explainable match estimate, matched/missing skills, recommendations, interview questions, saved history and a PDF report.

**Stack:** React + Vite · FastAPI · PyMuPDF · SQLite · Gemini API (optional)

## Run locally
```bash
# Backend
cd backend && python -m venv venv &&  source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add GEMINI_API_KEY (optional)
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev      # http://localhost:5173
```
No API key? The app runs in **basic mode** (rule-based skills + questions). With a key it adds Gemini feedback and tailored questions.

## How scoring works
`score = 60% required-skill coverage + 25% job keyword overlap + 15% resume structure`. It is an estimate, not an ATS score or hiring prediction.

## API
| Method | Path | Purpose |
|---|---|---|
| POST | /api/analyze | resume (PDF) + job_description + job_title |
| GET | /api/history, /api/history/{id} | past analyses |
| DELETE | /api/history/{id} | remove one |
| GET | /api/report/{id}/pdf | download report |

## Privacy
Keep `.env` out of Git. In AI mode, resume text is sent to Google; review Gemini data-use terms before using real personal data.

## Ideas to extend
Docker compose, pytest tests, deployment (Render + Vercel), DOCX upload, auth.
=======
# AI-Resume-Analyzer-using-GenAI
>>>>>>> 594253c7c6af709acb87216a4daf1bd98b1922c5
