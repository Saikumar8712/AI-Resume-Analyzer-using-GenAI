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
import db, analyzer, ai

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
    if len(data) > MAX_MB * 1024 * 1024: raise HTTPException(400, f"File is larger than {MAX_MB} MB.")
    jd_clean = job_description.strip()
    if len(jd_clean) < 2: raise HTTPException(400, "Job description must be at least 2 characters.")
    try:
        if is_docx:
            text = analyzer.extract_docx_text(data)
        else:
            text = analyzer.extract_pdf_text(data)
    except Exception:
        doc_type = "DOCX" if is_docx else "PDF"
        raise HTTPException(400, f"Could not read this {doc_type}. It may be corrupted or password-protected.")
    if len(text) < 100: raise HTTPException(400, "No readable text found. Scanned documents or image-only files are not supported; export a text-based PDF/DOCX.")
    result = analyzer.analyze(text, job_description)
    result["job_title"] = job_title
    fb = ai.gemini_feedback(text, job_description, result)
    result["mode"] = "ai" if fb else "basic"
    if fb:
        result["summary"] = fb.get("summary", "")
        if fb.get("need_to_improve"):
            result["need_to_improve"] = fb.get("need_to_improve")
        if fb.get("resume_improvements"):
            result["resume_improvements"] = fb.get("resume_improvements")
        result["recommendations"] = fb.get("recommendations") or result["recommendations"]
        result["questions"] = fb.get("questions") or []
        if fb.get("bullet_rewrites"):
            result["bullet_rewrites"] = fb.get("bullet_rewrites")
    if not result.get("questions"):
        result["questions"] = analyzer.basic_questions(result["missing_skills"], result["matched_skills"])
    result["id"] = db.save(resume.filename, job_title, result)
    return result

@app.get("/api/history")
def history(): return db.list_all()

@app.get("/api/history/{i}")
def one(i: int):
    r = db.get(i)
    if not r: raise HTTPException(404, "Analysis not found.")
    return {**r["result"], "id": i}

@app.delete("/api/history/{i}")
def remove(i: int):
    db.delete(i); return {"deleted": i}

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
            s_name = html.escape(str(item.get("skill", "")))
            s_sug = html.escape(str(item.get("suggestion", "")))
            flow.append(Paragraph(f"• <b>{s_name}</b>: {s_sug}", st["BodyText"]))
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

    doc.build(flow); buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=report-{i}.pdf"})

