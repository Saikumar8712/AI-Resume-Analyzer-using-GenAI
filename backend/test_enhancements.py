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
    def test_original_resume_preservation_with_projects_and_urls(self):
        complex_resume = """Jane Developer
jane.dev@example.com | +1 555-987-6543 | New York, NY
https://linkedin.com/in/janedev | https://github.com/janedev | https://janedev.dev
Professional Summary
Experienced Software Engineer specialized in full-stack cloud applications.
Technical Skills
Languages: Python, JavaScript, TypeScript, Go
Cloud & Tools: Docker, Kubernetes, AWS, PostgreSQL, Git
Professional Experience
Software Engineer - Cloud Innovations LLC (2021 - Present)
• Architected scalable microservices handling 25,000+ daily requests.
• Automated CI/CD pipelines reducing deployment friction by 50%.
Key Projects
Distributed Task Scheduler (https://github.com/janedev/task-scheduler)
• Built an event-driven scheduler using Python, Redis, and Docker.
• Implemented fault-tolerant worker nodes with automatic task retries.
Education
B.Tech in Computer Science - Tech University, 2021 | CGPA: 9.2/10
Certifications
• AWS Certified Solutions Architect Associate
"""
        record = {
            "job_title": "Full Stack Cloud Engineer",
            "result": {
                "job_title": "Full Stack Cloud Engineer",
                "summary": "Experienced Software Engineer specialized in full-stack cloud applications.",
                "matched_skills": ["Python", "Docker", "AWS", "PostgreSQL", "Git"],
                "extra_skills": ["JavaScript", "TypeScript", "Kubernetes", "Go"],
                "_raw_text": complex_resume
            }
        }

        buf = one_page_ats_resume.generate_exact_one_page_resume(record)
        doc = fitz.open(stream=buf.getvalue(), filetype="pdf")
        
        # 1. Exactly 1 A4 page
        self.assertEqual(len(doc), 1, "Resume must fit exactly on 1 page")
        page_text = doc[0].get_text()
        
        # 2. Contact and all URLs preserved
        self.assertIn("JANE DEVELOPER", page_text.upper())
        self.assertIn("jane.dev@example.com", page_text)
        self.assertIn("555-987-6543", page_text)
        self.assertIn("linkedin.com/in/janedev", page_text)
        self.assertIn("github.com/janedev", page_text)
        self.assertIn("janedev.dev", page_text)
        
        # 3. Technical Skills preserved
        self.assertIn("Python", page_text)
        self.assertIn("Docker", page_text)
        self.assertIn("Kubernetes", page_text)
        self.assertIn("Go", page_text)
        
        # 4. Experience & bullets preserved
        self.assertIn("Cloud Innovations LLC", page_text)
        self.assertIn("25,000+", page_text)
        
        # 5. Projects & repository links preserved
        self.assertIn("Distributed Task Scheduler", page_text)
        self.assertIn("github.com/janedev/task-scheduler", page_text)
        
        # 6. Education, CGPA, and Certifications preserved
        self.assertIn("Tech University", page_text)
        self.assertIn("9.2/10", page_text)
        self.assertIn("AWS Certified Solutions Architect", page_text)
        
        doc.close()

    def test_madhankumar_exact_one_page_and_no_degree_in_contact(self):
        madhan_resume = """MADHANKUMAR ONTEDDUBANDI
madhankumar.onteddubandi@gmail.com | +91 6303555193 | Kurnool, AP | https://www.linkedin.com/in/madhankumaronteddubandi | https://github.com/MadhanBlastz
PROFESSIONAL SUMMARY
Results-oriented Python Backend Developer with proven hands-on expertise in Flask, Git, Python, REST APIs. Demonstrated track record of delivering resilient, production-ready software solutions while adhering strictly to industry best practices and scalable design patterns.
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
2022 – 2026 | 77%
Intermediate (MPC), A.P Model college, Dhone Town, Kurnool Dist.
2020 – 2022 | 66%
SSC, ZP High School, Dhone Town, Kurnool Dist.
2020 | 93%
CERTIFICATIONS & CREDENTIALS
Python for Data Science - Coursera
"""
        record = {
            "job_title": "Python Backend Developer",
            "result": {
                "job_title": "Python Backend Developer",
                "matched_skills": ["Python", "SQL", "Flask", "REST APIs", "Git"],
                "extra_skills": ["HTML/CSS", "JavaScript", "Linux", "Machine learning", "Pandas"],
                "_raw_text": madhan_resume
            }
        }
        buf = one_page_ats_resume.generate_exact_one_page_resume(record)
        doc = fitz.open(stream=buf.getvalue(), filetype="pdf")
        
        # 1. Exactly 1 A4 page
        self.assertEqual(len(doc), 1, f"Resume must be exactly 1 page, found {len(doc)}")
        
        # 2. Extract and validate text
        text = doc[0].get_text()
        self.assertIn("MADHANKUMAR ONTEDDUBANDI", text.upper())
        self.assertIn("madhankumar.onteddubandi@gmail.com", text)
        self.assertIn("6303555193", text)
        self.assertIn("Kurnool, AP", text)
        
        # 3. B.Tech must NOT be in contact header
        header_text = text.split("PROFESSIONAL SUMMARY")[0]
        self.assertNotIn("B.Tech", header_text, "B.Tech degree must not be placed in contact links!")
        
        # 4. Technical skills must be cleaned and categorized
        skills_text = text.split("TECHNICAL SKILLS")[1].split("KEY PROJECTS")[0]
        self.assertNotIn("INTERNSHIPS", skills_text, "INTERNSHIPS header must not appear as a skill!")
        self.assertNotIn("(Queries, CRUD Operations, Filtering)", skills_text)
        
        # 5. Validation helper passes
        parsed = one_page_ats_resume.extract_resume_sections(madhan_resume)
        val = one_page_ats_resume.validate_ats_pdf(buf.getvalue(), parsed)
        self.assertTrue(val["valid"])
        self.assertTrue(val["fits_one_page"])
        self.assertTrue(val["is_selectable_text"])
        self.assertEqual(val["duplicate_bullets"], 0)
        doc.close()

    def test_transparent_scoring_and_partial_skills_matching(self):
        import analyzer
        resume = """Candidate Developer
cand@example.com | 555-1234
Summary: Python developer skilled in Flask, MySQL, and Docker.
Skills: Python, Flask, SQL, MySQL, Docker, Linux, Git
Experience:
Software Engineer at Acme Corp (2022 - Present)
• Developed backend services reducing response time by 40%.
• Built containerized workflows saving 12 hours weekly.
Education: BS in Computer Science, 2021
"""
        # JD asks for FastAPI (candidate has Flask), PostgreSQL (candidate has SQL/MySQL), and Kubernetes (missing)
        jd = "Seeking Backend Engineer proficient in Python, FastAPI, PostgreSQL, and Kubernetes."
        result = analyzer.analyze(resume, jd, job_title="Backend Engineer")
        
        # 1. Matched, Partial, and Missing categorization
        self.assertIn("Python", result["matched_skills"])
        partial_skill_names = [p["skill"] for p in result["partially_matched_skills"]]
        self.assertIn("FastAPI", partial_skill_names)
        self.assertIn("missing_skills", result)
        
        # 2. Transparent 3-score architecture
        self.assertIn("resume_quality_score", result)
        self.assertIn("job_match_score", result)
        self.assertIn("formatting_score", result)
        self.assertIn("score_reasons", result)
        
        # 3. Deterministic repeatability: repeated analysis yields identical scores
        repeat_result = analyzer.analyze(resume, jd, job_title="Backend Engineer")
        self.assertEqual(result["resume_quality_score"], repeat_result["resume_quality_score"])
        self.assertEqual(result["job_match_score"], repeat_result["job_match_score"])
        self.assertEqual(result["formatting_score"], repeat_result["formatting_score"])

    def test_general_purpose_resume_mode_when_no_jd_provided(self):
        import analyzer
        resume = """Jane Developer
jane@example.com | +1 555-0100
Summary: Full stack developer with expertise in React, Node.js, and PostgreSQL.
Skills: JavaScript, TypeScript, React, Node.js, SQL, Git
Experience:
Full Stack Engineer at WebCo (2021 - Present)
• Architected scalable web services handling 10,000+ daily active users.
• Increased frontend test coverage by 30%.
Education: B.S. in Computer Science, 2021
"""
        # Blank / omitted JD runs in general-purpose mode
        result = analyzer.analyze(resume, "", job_title="Senior Developer")
        self.assertTrue(result["is_general_purpose"])
        self.assertGreaterEqual(result["resume_quality_score"], 60)
        self.assertGreaterEqual(result["formatting_score"], 70)
        self.assertGreater(len(result["matched_skills"]), 0)

    def test_recruiter_review_dimensions_and_top_5_improvements(self):
        import analyzer
        resume = """Bob Smith - bob@example.com
Education: B.Tech 2022
Skills: Python, HTML/CSS
Experience:
Worked on web applications and updated databases.
"""
        result = analyzer.analyze(resume, "Python web developer with SQL and Docker.", job_title="Web Developer")
        recruiter_review = result.get("recruiter_review", {})
        
        # Verify 7 dimensions present
        dims = recruiter_review.get("dimensions", {})
        self.assertIn("summary_clarity", dims)
        self.assertIn("skills_relevance", dims)
        self.assertIn("project_complexity", dims)
        self.assertIn("experience_depth", dims)
        self.assertIn("measurable_impact", dims)
        self.assertIn("professionalism_consistency", dims)
        self.assertIn("information_completeness", dims)
        
        # Verify Top 5 improvements
        top_5 = recruiter_review.get("top_5_improvements", [])
        self.assertEqual(len(top_5), 5)
        for item in top_5:
            self.assertIn("priority", item)
            self.assertIn("title", item)
            self.assertIn("observation", item)
            self.assertIn("practical_example", item)

if __name__ == "__main__":
    unittest.main()

