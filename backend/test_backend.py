import unittest
import io
import os
import json
import sqlite3
from unittest.mock import patch, MagicMock

import skills
import analyzer
import db
import main

class TestSkillsAndAnalyzer(unittest.TestCase):
    def test_skills_matching(self):
        text = "Experienced in Python, C#, Docker, Kubernetes, and PostgreSQL databases."
        found = analyzer.find_skills(text)
        self.assertIn("Python", found)
        self.assertIn("C#", found)
        self.assertIn("Docker", found)
        self.assertIn("Kubernetes", found)
        self.assertIn("SQL", found)

    def test_no_false_positive_js_on_extensions_or_nodejs(self):
        # Having Node.js should match Node.js, but NOT match standalone JavaScript alias "js"
        text = "Built services with Node.js and deployed app.js on Linux."
        found = analyzer.find_skills(text)
        self.assertIn("Node.js", found)
        self.assertIn("Linux", found)
        self.assertNotIn("JavaScript", found)

    def test_standalone_js_matched(self):
        text = "Frontend developer skilled in HTML, CSS, and JS."
        found = analyzer.find_skills(text)
        self.assertIn("JavaScript", found)
        self.assertIn("HTML/CSS", found)

    def test_section_checks(self):
        sample_resume = """
        John Doe - john.doe@example.com - +1 (555) 123-4567
        Education: Bachelor of Science in Computer Science, University of Technology, 2022
        Experience: Software Engineer at Acme Corp. Reduced server latency by 45% and scaled to 50k users.
        Technical Skills: Python, FastAPI, Docker, SQL, Git
        Projects: Built an automated data pipeline saving 10 hrs/week.
        """
        checks = analyzer.section_checks(sample_resume)
        self.assertTrue(checks["Contact email"])
        self.assertTrue(checks["Education section"])
        self.assertTrue(checks["Projects or experience"])
        self.assertTrue(checks["Skills section"])
        self.assertTrue(checks["Measurable results (numbers/%)"])

    def test_graduation_year_not_counted_as_quantified_metric(self):
        resume_no_metrics = """
        Jane Doe - jane@example.com
        Education: B.Tech in CSE, Graduated in 2021
        Experience: Developed web features and fixed bugs.
        Skills: Python, React
        """
        ats_data = analyzer.calculate_ats_score(resume_no_metrics, analyzer.section_checks(resume_no_metrics))
        # Metrics count should be 0 because 2021 is a graduation year, resulting in low metric score
        self.assertEqual(ats_data["breakdown"]["Quantified Impact"], 15)

    def test_empty_jd_skills_scoring_does_not_collapse_to_zero(self):
        resume = """
        Alex Smith - alex@example.com - 555-0199
        Education: BS Computer Science 2020
        Experience: Managed projects and coordinated team communications.
        Skills: Communication, Teamwork
        """
        jd = "Looking for a proactive professional to lead team initiatives and manage communications."
        result = analyzer.analyze(resume, jd)
        self.assertGreater(result["score"], 0)
        self.assertEqual(result["breakdown"]["Skill coverage"], 100)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_file.close()
        self.patcher = patch("db.DB", self.temp_file.name)
        self.patcher.start()
        db.init()

    def tearDown(self):
        self.patcher.stop()
        try:
            os.remove(self.temp_file.name)
        except OSError:
            pass

    def test_save_get_list_delete(self):
        dummy_result = {"score": 85, "job_title": "Backend Dev", "matched_skills": ["Python"]}
        row_id = db.save("test_resume.pdf", "Backend Dev", dummy_result)
        self.assertIsInstance(row_id, int)

        # Get
        record = db.get(row_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["filename"], "test_resume.pdf")
        self.assertEqual(record["result"]["score"], 85)

        # List
        items = db.list_all()
        self.assertGreaterEqual(len(items), 1)

        # Delete
        deleted = db.delete(row_id)
        self.assertTrue(deleted)

        # Verify deletion
        self.assertIsNone(db.get(row_id))
        deleted_again = db.delete(row_id)
        self.assertFalse(deleted_again)

class TestPDFReportGeneration(unittest.TestCase):
    def test_pdf_report_with_complex_and_string_items(self):
        dummy_record = {
            "id": 99,
            "filename": "test.pdf",
            "job_title": "Senior Engineer",
            "result": {
                "score": 88,
                "ats_score": 82,
                "ats_grade": "A",
                "disclaimer": "Test disclaimer",
                "matched_skills": ["Python", "FastAPI"],
                "need_to_improve": [
                    {"skill": "Docker", "priority": "High", "suggestion": "Build containerized apps."},
                    "Kubernetes"  # String fallback test
                ],
                "resume_improvements": ["Add more quantifiable results."],
                "recommendations": ["Tailor bullets."],
                "bullet_rewrites": [
                    {"original": "Worked on API.", "improved": "Architected REST API reducing latency by 30%."},
                ],
                "questions": ["How do you scale FastAPI?"]
            }
        }
        with patch("db.get", return_value=dummy_record):
            response = main.pdf(99)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.media_type, "application/pdf")
            self.assertIn("Content-Disposition", response.headers)

    def test_ats_resume_pdf_generation(self):
        dummy_record = {
            "id": 99,
            "filename": "test.pdf",
            "job_title": "Python Developer",
            "result": {
                "score": 90,
                "ats_score": 85,
                "ats_grade": "A",
                "matched_skills": ["Python", "FastAPI", "SQL"],
                "extra_skills": ["Docker", "Git"],
                "_raw_text": "Jane Doe\njane@example.com\n+1 555-0100\nExperience: Built scalable APIs with Python.",
                "bullet_rewrites": [{"original": "Built APIs", "improved": "Architected high-throughput REST APIs reducing response time by 40%."}],
                "recommendations": ["Highlight Docker and Kubernetes orchestration."]
            }
        }
        with patch("db.get", return_value=dummy_record):
            response = main.ats_resume_pdf(99)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.media_type, "application/pdf")
            self.assertIn("Content-Disposition", response.headers)
            self.assertIn("ats-resume-99.pdf", response.headers["Content-Disposition"])

class TestJobRecommendationsAndEnhancedATS(unittest.TestCase):
    def test_job_recommendations(self):
        recs = analyzer.recommend_jobs({"Python", "FastAPI", "SQL", "Docker"}, target_role="Python Backend Engineer")
        self.assertGreaterEqual(len(recs), 1)
        top_role = recs[0]
        self.assertIn("title", top_role)
        self.assertIn("match_score", top_role)
        self.assertIn("match_level", top_role)
        self.assertIn("reason", top_role)
        self.assertIn("Python", top_role["matching_skills"])

    def test_enhanced_ats_score_with_jd_and_certifications(self):
        sample_resume = """
        Alex Smith - alex@example.com - 555-0199
        Certifications: AWS Certified Solutions Architect, Scrum Master
        Education: BS Computer Science 2020
        Experience: Developed microservices and optimized queries by 35%.
        Skills: Python, FastAPI, Docker, SQL
        """
        checks = analyzer.section_checks(sample_resume)
        jd = "Seeking a Python Developer with FastAPI and SQL experience."
        ats_data = analyzer.calculate_ats_score(sample_resume, checks, jd=jd, job_title="Python Developer")
        self.assertIn("Role Keyword Alignment", ats_data["breakdown"])
        self.assertIn("Certifications & Credentials", ats_data["breakdown"])
        self.assertEqual(ats_data["breakdown"]["Certifications & Credentials"], 100)

if __name__ == "__main__":
    unittest.main()
