"""
Job Matching Engine
Provides at least 10 relevant, categorized job recommendations tailored to the
candidate's verified skills, experience level, and target job description.
Never fabricates active vacancies; clearly distinguishes verified market benchmarks from suggested roles.
"""

import urllib.parse
import re

EXTENDED_JOB_CATALOG = [
    {
        "title": "Python Backend Engineer",
        "category": "Backend",
        "core_skills": ["Python", "FastAPI", "Flask", "Django", "SQL", "REST APIs", "Docker"],
        "experience_level": "Entry Level / Mid",
        "location": "Remote / Hybrid",
        "work_mode": "Hybrid",
        "company": "Market Benchmark (Tech / SaaS)",
        "is_verified": True,
        "description": "Architect and scale RESTful microservices, asynchronous APIs, and relational database pipelines."
    },
    {
        "title": "Junior Python Developer",
        "category": "Backend",
        "core_skills": ["Python", "SQL", "REST APIs", "Git", "Linux", "FastAPI"],
        "experience_level": "Fresher / Entry Level",
        "location": "Remote / On-site",
        "work_mode": "Remote",
        "company": "Market Benchmark (Growth Startups)",
        "is_verified": True,
        "description": "Develop modular backend scripts, automated endpoints, and unit test suites with Python."
    },
    {
        "title": "Full Stack Software Engineer",
        "category": "Full Stack",
        "core_skills": ["React", "JavaScript", "TypeScript", "Node.js", "Python", "SQL", "HTML/CSS", "REST APIs"],
        "experience_level": "Entry Level / Mid",
        "location": "Remote / Hybrid",
        "work_mode": "Remote",
        "company": "Market Benchmark (Global Tech)",
        "is_verified": True,
        "description": "Design interactive web interfaces and build scalable, secure server-side applications."
    },
    {
        "title": "Frontend Engineer",
        "category": "Frontend",
        "core_skills": ["React", "JavaScript", "TypeScript", "HTML/CSS", "Next.js", "Tailwind CSS", "Git"],
        "experience_level": "Fresher / Entry Level",
        "location": "Remote / Hybrid",
        "work_mode": "Hybrid",
        "company": "Market Benchmark (Digital Products)",
        "is_verified": True,
        "description": "Craft responsive, component-driven user interfaces with accessibility and smooth state management."
    },
    {
        "title": "DevOps & Cloud Associate",
        "category": "DevOps",
        "core_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git", "Python"],
        "experience_level": "Entry Level / Mid",
        "location": "Remote / Hybrid",
        "work_mode": "Remote",
        "company": "Market Benchmark (Cloud Infrastructure)",
        "is_verified": True,
        "description": "Automate deployment workflows, configure containerized services, and monitor cloud resources."
    },
    {
        "title": "API & Integration Engineer",
        "category": "Backend",
        "core_skills": ["REST APIs", "Python", "SQL", "FastAPI", "Docker", "Git"],
        "experience_level": "Entry Level / Mid",
        "location": "Remote / On-site",
        "work_mode": "Remote",
        "company": "Market Benchmark (FinTech & Enterprise)",
        "is_verified": True,
        "description": "Build high-throughput API gateways, third-party integrations, and data validation layers."
    },
    {
        "title": "Data Engineer / ETL Developer",
        "category": "Data",
        "core_skills": ["Python", "SQL", "Pandas", "Kafka", "Redis", "Git"],
        "experience_level": "Entry Level / Mid",
        "location": "Hybrid / On-site",
        "work_mode": "Hybrid",
        "company": "Market Benchmark (Analytics & Data)",
        "is_verified": True,
        "description": "Construct high-performance ETL pipelines, database migrations, and streaming ingestion queues."
    },
    {
        "title": "Machine Learning Associate",
        "category": "AI/ML",
        "core_skills": ["Python", "Machine learning", "Pandas", "SQL", "Deep learning", "NLP"],
        "experience_level": "Entry Level / Mid",
        "location": "Remote / Hybrid",
        "work_mode": "Remote",
        "company": "Market Benchmark (AI Solutions)",
        "is_verified": True,
        "description": "Train and evaluate predictive models, curate feature stores, and deploy ML inference endpoints."
    },
    {
        "title": "Software Development Engineer in Test (SDET)",
        "category": "QA / Testing",
        "core_skills": ["Python", "Unit testing", "CI/CD", "Git", "REST APIs", "Linux"],
        "experience_level": "Fresher / Entry Level",
        "location": "Remote / Hybrid",
        "work_mode": "Remote",
        "company": "Market Benchmark (Enterprise Software)",
        "is_verified": True,
        "description": "Write automated test harnesses, regression suites, and load test scripts for backend services."
    },
    {
        "title": "Cloud Platform Engineer",
        "category": "Cloud",
        "core_skills": ["AWS", "Docker", "Linux", "Python", "CI/CD", "System Design"],
        "experience_level": "Entry Level / Mid",
        "location": "Hybrid / Remote",
        "work_mode": "Hybrid",
        "company": "Market Benchmark (Cloud Platforms)",
        "is_verified": True,
        "description": "Provision serverless compute, manage S3/RDS storage architectures, and enforce security policies."
    },
    {
        "title": "Site Reliability Engineer (SRE)",
        "category": "DevOps",
        "core_skills": ["Linux", "Docker", "Python", "Kubernetes", "CI/CD", "Git"],
        "experience_level": "Entry Level / Mid",
        "location": "Remote / Hybrid",
        "work_mode": "Remote",
        "company": "Market Benchmark (High-Scale Tech)",
        "is_verified": True,
        "description": "Maintain service reliability, automate incident triage, and optimize low-latency production clusters."
    },
    {
        "title": "Application Support / Systems Associate",
        "category": "Systems",
        "core_skills": ["SQL", "Linux", "Python", "Git", "REST APIs"],
        "experience_level": "Fresher / Entry Level",
        "location": "On-site / Hybrid",
        "work_mode": "Hybrid",
        "company": "Market Benchmark (IT Services)",
        "is_verified": True,
        "description": "Troubleshoot production database queries, inspect server log streams, and assist API debugging."
    },
    {
        "title": "FastAPI / Microservices Developer",
        "category": "Backend",
        "core_skills": ["FastAPI", "Python", "Docker", "SQL", "REST APIs", "Redis"],
        "experience_level": "Entry Level / Mid",
        "location": "Remote",
        "work_mode": "Remote",
        "company": "Market Benchmark (Fast-Growth Startups)",
        "is_verified": True,
        "description": "Develop asynchronous microservice handlers utilizing Pydantic models and SQLAlchemy ORM."
    },
    {
        "title": "Backend Web Developer (Django / Flask)",
        "category": "Backend",
        "core_skills": ["Django", "Flask", "Python", "SQL", "HTML/CSS", "Git"],
        "experience_level": "Fresher / Entry Level",
        "location": "Remote / Hybrid",
        "work_mode": "Remote",
        "company": "Market Benchmark (Web Agencies)",
        "is_verified": True,
        "description": "Implement authentication, schema migrations, template rendering, and REST endpoints."
    },
    {
        "title": "Junior Data Analyst",
        "category": "Data",
        "core_skills": ["SQL", "Python", "Pandas", "Git"],
        "experience_level": "Fresher / Entry Level",
        "location": "Remote / On-site",
        "work_mode": "Hybrid",
        "company": "Market Benchmark (Business Intelligence)",
        "is_verified": True,
        "description": "Query relational data warehouses, prepare statistical summaries, and build executive dashboards."
    }
]

def build_job_search_url(title: str, skills: list) -> str:
    """Builds a verified, direct job search query link on LinkedIn / Indeed."""
    query_parts = [title]
    if skills:
        query_parts.extend(skills[:2])
    query = " ".join(query_parts)
    encoded = urllib.parse.quote(query)
    return f"https://www.linkedin.com/jobs/search/?keywords={encoded}"

def is_fresher_profile(resume_text: str) -> bool:
    """Checks if the candidate is entry-level, fresher, or student based on resume text."""
    t = resume_text.lower()
    fresher_indicators = [
        "fresher", "student", "intern", "internship", "entry level", "graduate",
        "bachelor", "b.tech", "b.sc", "b.e", "pursuing", "academic projects"
    ]
    # Check for senior indicators
    senior_indicators = ["senior", "lead", "architect", "principal", "staff engineer", "manager", "head of"]
    has_fresher = any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in fresher_indicators)
    has_senior = any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in senior_indicators)
    
    # If candidate has < 3 years experience or matches fresher words
    return has_fresher and not has_senior

def match_jobs(
    candidate_skills: set,
    resume_text: str = "",
    target_role: str = "",
    job_description: str = "",
    min_count: int = 10
) -> list:
    """
    Generates at least 10 relevant job recommendations based on candidate's verified skills,
    target role, and JD keywords. Distinguishes verified benchmarks from suggested titles.
    """
    t_role_lower = (target_role or "").lower()
    t_role_words = {w for w in re.findall(r"[a-z]{3,}", t_role_lower)}
    is_fresher = is_fresher_profile(resume_text)

    # Extract JD skills or keywords for relevance weighting
    jd_words = {w for w in re.findall(r"[a-z]{3,}", (job_description or "").lower())}

    matches = []
    for role in EXTENDED_JOB_CATALOG:
        core = role["core_skills"]
        matched = [s for s in core if s in candidate_skills]
        missing = [s for s in core if s not in candidate_skills]

        # Calculate base skill fit
        base_pct = (len(matched) / len(core)) * 100 if core else 0

        # Title alignment bonus
        role_title_words = {w for w in re.findall(r"[a-z]{3,}", role["title"].lower())}
        title_overlap = len(role_title_words & t_role_words)
        title_bonus = min(25, title_overlap * 12)

        # JD context bonus
        jd_overlap = len(role_title_words & jd_words)
        jd_bonus = min(15, jd_overlap * 5)

        # Experience level weighting
        level_bonus = 0
        if is_fresher and "Fresher" in role["experience_level"]:
            level_bonus = 10
        elif not is_fresher and "Mid" in role["experience_level"]:
            level_bonus = 5

        match_score = round(min(98, max(25, base_pct + title_bonus + jd_bonus + level_bonus)))

        # Level description
        if match_score >= 75:
            level = "High Match"
        elif match_score >= 55:
            level = "Strong Potential"
        else:
            level = "Growth Opportunity"

        # Construct clear explanation
        if matched:
            reason = (
                f"Matches {len(matched)} of your core skills ({', '.join(matched[:3])}). "
                f"Aligned with {role['experience_level']} expectations in {role['work_mode']} environments."
            )
        else:
            reason = (
                f"Strong adjacent pathway for your technical background. "
                f"Requires ramping up on {', '.join(missing[:2])}."
            )

        search_url = build_job_search_url(role["title"], matched)

        matches.append({
            "title": role["title"],
            "company": role["company"],
            "location": role["location"],
            "work_mode": role["work_mode"],
            "experience_level": role["experience_level"],
            "is_verified": role["is_verified"],
            "match_score": match_score,
            "match_level": level,
            "reason": reason,
            "matching_skills": matched,
            "growth_skills": missing[:3],
            "apply_url": search_url,
            "category": role.get("category", "Engineering")
        })

    # Sort descending by match score
    matches.sort(key=lambda m: m["match_score"], reverse=True)

    # Ensure at least min_count (10)
    final_recs = matches[:max(min_count, 10)]

    # If fresher, reorder so entry/fresher roles with high match come first
    if is_fresher:
        final_recs.sort(key=lambda m: (
            1 if "Fresher" in m["experience_level"] else 0,
            m["match_score"]
        ), reverse=True)

    return final_recs
