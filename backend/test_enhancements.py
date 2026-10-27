"""
Test script for Job Matching Engine and One-Page ATS Resume PDF Generator
"""

import unittest
import io
import pymupdf as fitz
import job_matching_engine
import one_page_ats_resume

SAMPLE_RESUME = """Alex Johnson
alex.johnson@example.com | (555) 123-4567 | San Francisco, CA
Professional Summary
Software Engineer with 4 years of experience specializing in Python, FastAPI, SQL, and Docker.
Proven track record building high-performance REST APIs and scalable backend architectures.
Skills
Languages & Frameworks: Python, FastAPI, Flask, SQL, PostgreSQL, JavaScript, React, HTML/CSS
DevOps & Tools: Git, Docker, CI/CD, Linux, pytest
Experience
Senior Backend Engineer - Tech Solutions Inc. (2022 - Present)
• Developed and maintained 15+ microservices in Python and FastAPI with 99.9% uptime.
• Optimized SQL queries reducing database response latency by 42%.
• Implemented Docker containerization and CI/CD pipelines with GitHub Actions.
Education
B.S. in Computer Science - State University, 2020
"""

class TestEnhancements(unittest.TestCase):
    def test_job_matching_returns_at_least_10_recommendations(self):
        candidate_skills = {"Python", "FastAPI", "SQL", "Docker", "Git", "Linux", "REST APIs"}
        recs = job_matching_engine.match_jobs(
            candidate_skills=candidate_skills,
            resume_text=SAMPLE_RESUME,
            target_role="Senior Python Backend Developer",
            job_description="Seeking Python backend developer with FastAPI, SQL, Docker, and REST APIs experience.",
            min_count=10
        )
        self.assertGreaterEqual(len(recs), 10, "Must return at least 10 job matches")
        
        # Verify required fields on each recommendation
        for r in recs:
            self.assertIn("title", r)
            self.assertIn("company", r)
            self.assertIn("location", r)
            self.assertIn("work_mode", r)
            self.assertIn("experience_level", r)
            self.assertIn("match_score", r)
            self.assertIn("match_level", r)
            self.assertIn("reason", r)
            self.assertIn("matching_skills", r)
            self.assertIn("growth_skills", r)
            self.assertIn("apply_url", r)
            self.assertTrue(r["is_verified"])
            self.assertTrue(r["apply_url"].startswith("https://www.linkedin.com/jobs/search/"))

    def test_one_page_ats_resume_pdf_exact_one_page(self):
        record = {
            "job_title": "Senior Python Backend Engineer",
            "result": {
                "job_title": "Senior Python Backend Engineer",
                "summary": "Software Engineer with 4 years of experience specializing in Python, FastAPI, SQL, and Docker.",
                "matched_skills": ["Python", "FastAPI", "SQL", "Docker", "REST APIs"],
                "extra_skills": ["Git", "Linux", "pytest"],
                "bullet_rewrites": [
                    {"original": "Worked on APIs", "improved": "Architected 15+ resilient microservices in Python and FastAPI with 99.9% uptime."}
                ],
                "_raw_text": SAMPLE_RESUME
            }
        }

        buf = one_page_ats_resume.generate_exact_one_page_resume(record)
        self.assertIsInstance(buf, io.BytesIO)
        pdf_bytes = buf.getvalue()
        self.assertGreater(len(pdf_bytes), 1000)

        # Inspect generated PDF with PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertEqual(len(doc), 1, f"Resume MUST be exactly 1 page, but has {len(doc)} pages!")
        
        # Check text content extraction and preservation
        page_text = doc[0].get_text()
        self.assertIn("ALEX JOHNSON", page_text.upper())
        self.assertIn("alex.johnson@example.com", page_text)
        self.assertIn("(555) 123-4567", page_text)
        self.assertIn("San Francisco, CA", page_text)
        self.assertIn("PROFESSIONAL SUMMARY", page_text)
        self.assertIn("TECHNICAL SKILLS", page_text)
        self.assertIn("PROFESSIONAL EXPERIENCE", page_text)
        self.assertIn("EDUCATION", page_text)
        self.assertIn("B.S. in Computer Science", page_text)
        self.assertIn("Tech Solutions Inc.", page_text)
        doc.close()

if __name__ == "__main__":
    unittest.main()
