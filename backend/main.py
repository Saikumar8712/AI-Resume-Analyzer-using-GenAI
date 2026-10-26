import os, io, sys, html
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import db, analyzer, ai, ats_resume

MAX_MB = 5
app = FastAPI(title="AI Resume Analyzer")

cors_origins = [
    os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").rstrip("/"),
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
app.add_middleware(CORSMiddleware, allow_origins=list(set(cors_origins)),
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
db.init()

@app.get("/api/health")
def health():
    return {"status": "ok", "ai_enabled": bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/api/analyze")
async def analyze(resume: UploadFile = File(...), job_description: str = Form(...), job_title: str = Form("Target role")):
    filename_lower = (resume.filename or "").lower()
    is_pdf = resume.content_type == "application/pdf" or filename_lower.endswith(".pdf")
    is_docx = (
        resume.content_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]
        or filename_lower.endswith(".docx")
    )
    if not (is_pdf or is_docx):
        raise HTTPException(400, "Upload a PDF or DOCX file.")
    data = await resume.read()
    if len(data) == 0:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(400, f"File is larger than {MAX_MB} MB.")
    jd_clean = job_description.strip()
    if len(jd_clean) < 2:
        raise HTTPException(400, "Job description must be at least 2 characters.")
    try:
        if is_docx:
            text = analyzer.extract_docx_text(data)
        else:
            text = analyzer.extract_pdf_text(data)
    except ValueError as ve:
        raise HTTPException(400, str(ve))
    except Exception:
        doc_type = "DOCX" if is_docx else "PDF"
        raise HTTPException(400, f"Could not read this {doc_type}. It may be corrupted or password-protected.")
    if len(text.strip()) < 50:
        raise HTTPException(400, "No readable text found. Scanned documents or image-only files are not supported; export a text-based PDF/DOCX.")
    result = analyzer.analyze(text, job_description, job_title=job_title)
    result["job_title"] = job_title
    fb = ai.gemini_feedback(text, job_description, result)
    result["mode"] = "ai" if fb else "basic"
    if fb:
        result["summary"] = str(fb.get("summary", "")).strip()
        if fb.get("need_to_improve") and isinstance(fb["need_to_improve"], list):
            sanitized_improve = []
            for item in fb["need_to_improve"]:
                if isinstance(item, dict):
                    sanitized_improve.append({
                        "skill": str(item.get("skill", "")).strip(),
                        "priority": str(item.get("priority", "High")).strip(),
                        "suggestion": str(item.get("suggestion", "")).strip()
                    })
                elif isinstance(item, str) and item.strip():
                    sanitized_improve.append({
                        "skill": item.strip(),
                        "priority": "High",
                        "suggestion": f"Build hands-on experience and portfolio evidence for {item.strip()}."
                    })
            if sanitized_improve:
                result["need_to_improve"] = sanitized_improve
        if fb.get("resume_improvements") and isinstance(fb["resume_improvements"], list):
            result["resume_improvements"] = [str(x).strip() for x in fb["resume_improvements"] if str(x).strip()]
        if fb.get("recommendations") and isinstance(fb["recommendations"], list):
            result["recommendations"] = [str(x).strip() for x in fb["recommendations"] if str(x).strip()]
        if fb.get("questions") and isinstance(fb["questions"], list):
            result["questions"] = [str(x).strip() for x in fb["questions"] if str(x).strip()]
        if fb.get("bullet_rewrites") and isinstance(fb["bullet_rewrites"], list):
            sanitized_rewrites = []
            for rw in fb["bullet_rewrites"]:
                if isinstance(rw, dict):
                    orig = str(rw.get("original", "")).strip()
                    imp = str(rw.get("improved", "")).strip()
                    if orig and imp:
                        sanitized_rewrites.append({"original": orig, "improved": imp})
            if sanitized_rewrites:
                result["bullet_rewrites"] = sanitized_rewrites
    if not result.get("questions"):
        result["questions"] = analyzer.basic_questions(result["missing_skills"], result["matched_skills"])
    saved_id = db.save(resume.filename, job_title, result)
    result["id"] = saved_id
    result["ats_resume_url"] = f"/api/report/{saved_id}/ats-resume"
    return result

@app.get("/api/history")
def history(): return db.list_all()

@app.get("/api/history/{i}")
def one(i: int):
    r = db.get(i)
    if not r: raise HTTPException(404, "Analysis not found.")
    return {**r["result"], "id": i, "ats_resume_url": f"/api/report/{i}/ats-resume"}

@app.delete("/api/history/{i}")
def remove(i: int):
    if not db.delete(i):
        raise HTTPException(404, "Analysis not found.")
    return {"deleted": i}

@app.get("/api/report/{i}/ats-resume")
def ats_resume_pdf(i: int):
    r = db.get(i)
    if not r: raise HTTPException(404, "Analysis not found.")
    buf = ats_resume.generate_ats_resume(r)
    return StreamingResponse(buf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=ats-resume-{i}.pdf"})

@app.get("/api/report/{i}/pdf")
def pdf(i: int):
    r = db.get(i)
    if not r: raise HTTPException(404, "Analysis not found.")
    x, st = r["result"], getSampleStyleSheet()
    buf = io.BytesIO(); doc = SimpleDocTemplate(buf, pagesize=A4)
    escaped_title = html.escape(str(r.get('job_title', 'Resume Analysis')))
    escaped_disclaimer = html.escape(str(x.get('disclaimer', '')))
    ats_score = x.get('ats_score', x.get('score', 0))
    ats_grade = x.get('ats_grade', 'A')

    flow = [
        Paragraph(f"AI Resume Analysis Report: {escaped_title}", st["Title"]),
        Paragraph(f"Job Match Score: {x.get('score', 0)}%  |  ATS Compatibility Score: {ats_score}% (Grade: {ats_grade})", st["Heading2"]),
        Paragraph(escaped_disclaimer, st["Italic"]),
        Spacer(1, 10)
    ]

    # 1. Matched Skills
    flow.append(Paragraph("Matched Core Skills", st["Heading3"]))
    matched = x.get("matched_skills", [])
    if matched:
        flow += [Paragraph("• " + html.escape(str(s)), st["BodyText"]) for s in matched]
    else:
        flow.append(Paragraph("No required core skills detected in resume.", st["BodyText"]))
    flow.append(Spacer(1, 8))

    # 2. Need to Improve (Skills Gaps & Learning Pathways)
    flow.append(Paragraph("Need to Improve: Skills Gaps & Advice", st["Heading3"]))
    need_to_improve = x.get("need_to_improve", [])
    if need_to_improve:
        for item in need_to_improve:
            if isinstance(item, dict):
                s_name = html.escape(str(item.get("skill", "")))
                s_sug = html.escape(str(item.get("suggestion", "")))
                flow.append(Paragraph(f"• <b>{s_name}</b>: {s_sug}", st["BodyText"]))
            elif isinstance(item, str):
                flow.append(Paragraph(f"• {html.escape(item)}", st["BodyText"]))
    else:
        flow.append(Paragraph("None - Candidate demonstrates all listed required skills!", st["BodyText"]))
    flow.append(Spacer(1, 8))

    # 3. Resume Improvements (Extracted PDF)
    flow.append(Paragraph("Resume Structure & Content Improvements", st["Heading3"]))
    improvements = x.get("resume_improvements", [])
    if improvements:
        flow += [Paragraph("• " + html.escape(str(imp)), st["BodyText"]) for imp in improvements]
    else:
        flow.append(Paragraph("Resume structure is strong and meets standard screening benchmarks.", st["BodyText"]))
    flow.append(Spacer(1, 8))

    # 4. Tailoring Recommendations
    flow.append(Paragraph("Top Tailoring Recommendations", st["Heading3"]))
    recs = x.get("recommendations", [])
    if recs:
        flow += [Paragraph("• " + html.escape(str(r_item)), st["BodyText"]) for r_item in recs]
    flow.append(Spacer(1, 8))

    # 5. High-Impact Bullet Point Rewrites
    rewrites = x.get("bullet_rewrites", [])
    if rewrites:
        flow.append(Paragraph("AI High-Impact Bullet Rewrites", st["Heading3"]))
        for rw in rewrites:
            if isinstance(rw, dict):
                orig = html.escape(str(rw.get("original", "")))
                imp = html.escape(str(rw.get("improved", "")))
                flow.append(Paragraph(f"• <b>Original:</b> <i>{orig}</i><br/>&nbsp;&nbsp;<b>Rewrite:</b> {imp}", st["BodyText"]))
                flow.append(Spacer(1, 4))
        flow.append(Spacer(1, 4))

    # 6. Tailored Interview Practice Questions
    flow.append(Paragraph("Targeted Practice Interview Questions", st["Heading3"]))
    questions = x.get("questions", [])
    if questions:
        flow += [Paragraph(f"{idx+1}. " + html.escape(str(q)), st["BodyText"]) for idx, q in enumerate(questions)]

    try:
        doc.build(flow)
    except Exception as e:
        raise HTTPException(500, f"Failed to generate PDF report: {e}")
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=report-{i}.pdf"})

