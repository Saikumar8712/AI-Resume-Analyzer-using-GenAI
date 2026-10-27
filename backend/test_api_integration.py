from fastapi.testclient import TestClient
from main import app
import pymupdf as fitz

client = TestClient(app)

# 1. Health check
res = client.get('/api/health')
assert res.status_code == 200, res.text
print('Health check passed:', res.json())

# 2. General-Purpose analysis without JD
sample_resume_text = """MADHANKUMAR ONTEDDUBANDI
madhankumar.onteddubandi@gmail.com | +91 6303555193 | Kurnool, AP | https://www.linkedin.com/in/madhankumaronteddubandi | https://github.com/MadhanBlastz
PROFESSIONAL SUMMARY
Results-oriented Python Backend Developer with proven hands-on expertise in Flask, Git, Python, REST APIs.
TECHNICAL SKILLS
Languages & Core: Python, SQL, HTML/CSS, JavaScript
SQL / MySQL (Queries, CRUD Operations, Filtering)
HTML, CSS, Flask (Routing, Templates, CRUD)
GitHub (Version Control, Repository Management)
Linux (Basic Commands, File Navigation, File Management)
INTERNSHIPS
KEY PROJECTS
1. Water Quality Index Predictor | Python, Scikit-learn, Pandas, Streamlit
GitHub: https://github.com/MadhanBlastz/Water-Quality-Index-Predictor
Built an interactive machine learning web application using Scikit-learn and Streamlit to analyze and predict water potability from environmental parameters.
2. Job Application Tracker | HTML, CSS, Python, Flask, MySQL
GitHub: https://github.com/MadhanBlastz/Job-Application-Tracker
Developed a web-based job tracking application that allows users to add, update, and manage job roles,
application dates, and application status using Flask and MySQL.
EDUCATION
B.Tech in CSE, Vemu Institute of Technology, P. Kothakota, Chittoor Dist.
2022 - 2026 | 77%
CERTIFICATIONS & CREDENTIALS
Python for Data Science - Coursera
"""

# Create a genuine text PDF with PyMuPDF
pdf_doc = fitz.open()
page = pdf_doc.new_page()
page.insert_text((50, 50), sample_resume_text, fontsize=10)
pdf_bytes = pdf_doc.write()
pdf_doc.close()

files = {'resume': ('madhan_resume.pdf', pdf_bytes, 'application/pdf')}
data = {'job_description': '', 'job_title': 'Python Backend Developer'}
res = client.post('/api/analyze', files=files, data=data)
assert res.status_code == 200, res.text
out = res.json()
rep_id = out['id']
print('General-Purpose Analysis ID:', rep_id)
print('Is General Purpose:', out['is_general_purpose'])
print('Scores:', out['resume_quality_score'], out['job_match_score'], out['ats_score'])
print('Recruiter Review Top 5 count:', len(out['recruiter_review']['top_5_improvements']))

# 3. Test ATS Resume PDF generation
ats_res = client.get(f'/api/report/{rep_id}/ats-resume')
assert ats_res.status_code == 200
doc = fitz.open(stream=ats_res.content, filetype='pdf')
print('ATS Resume PDF Page Count:', len(doc))
assert len(doc) == 1, f'MUST BE EXACTLY 1 PAGE, got {len(doc)}'

# 4. Test PDF validation endpoint
val_res = client.get(f'/api/report/{rep_id}/validation')
assert val_res.status_code == 200
val = val_res.json()
print('Validation endpoint response:', val)
assert val['fits_one_page'] is True
assert val['valid'] is True

# 5. Test Analysis Report PDF generation
report_pdf_res = client.get(f'/api/report/{rep_id}/pdf')
assert report_pdf_res.status_code == 200
assert len(report_pdf_res.content) > 1000
print('Report PDF successfully generated, size:', len(report_pdf_res.content))
print('ALL INTEGRATION CHECKS PASSED!')
