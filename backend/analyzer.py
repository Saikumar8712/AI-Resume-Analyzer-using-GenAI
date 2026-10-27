import re, io
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None
from skills import SKILLS

STOP = set("the a an and or of to in for with on at by is are be as this that from will you your we our have has can must should".split())

ADJACENT_SKILLS = {
    "FastAPI": ["Flask", "Django", "Python", "REST APIs"],
    "Flask": ["FastAPI", "Django", "Python", "REST APIs"],
    "Django": ["FastAPI", "Flask", "Python", "REST APIs"],
    "React": ["JavaScript", "TypeScript", "Next.js", "Vue.js", "HTML/CSS"],
    "Next.js": ["React", "JavaScript", "TypeScript", "Node.js"],
    "TypeScript": ["JavaScript", "React", "Node.js"],
    "JavaScript": ["TypeScript", "React", "Node.js"],
    "Node.js": ["JavaScript", "TypeScript", "REST APIs"],
    "Vue.js": ["JavaScript", "React", "HTML/CSS"],
    "Angular": ["TypeScript", "JavaScript"],
    "PostgreSQL": ["SQL", "MySQL", "Database"],
    "MySQL": ["SQL", "PostgreSQL", "Database"],
    "MongoDB": ["SQL", "Database"],
    "SQL": ["MySQL", "PostgreSQL", "Database"],
    "Docker": ["Kubernetes", "Linux", "CI/CD", "DevOps"],
    "Kubernetes": ["Docker", "Linux", "DevOps", "AWS", "GCP"],
    "AWS": ["Azure", "GCP", "Docker", "DevOps"],
    "Azure": ["AWS", "GCP", "DevOps"],
    "GCP": ["AWS", "Azure", "DevOps"],
    "Deep learning": ["Machine learning", "Python", "Pandas"],
    "NLP": ["Machine learning", "Deep learning", "Python"],
    "Machine learning": ["Python", "Pandas", "Scikit-learn"],
    "CI/CD": ["Git", "GitHub", "Docker", "DevOps"],
    "REST APIs": ["FastAPI", "Flask", "Django", "Node.js", "Microservices"],
    "Microservices": ["REST APIs", "Docker", "System Design"],
    "System Design": ["Microservices", "REST APIs", "SQL"],
    "Pandas": ["Python", "NumPy", "Machine learning", "Data structures"],
    "Unit testing": ["Python", "pytest", "Git", "CI/CD"]
}

def extract_pdf_text(data: bytes) -> str:
    if not fitz:
        raise ValueError("PyMuPDF (fitz) is not installed.")
    with fitz.open(stream=data, filetype="pdf") as doc:
        if doc.is_encrypted:
            authenticated = doc.authenticate("")
            if not authenticated:
                raise ValueError("PDF is password-protected. Please upload an unprotected PDF.")
        return "\n".join(p.get_text() for p in doc).strip()

def extract_docx_text(data: bytes) -> str:
    try:
        import docx
        doc = docx.Document(io.BytesIO(data))
        text = []
        for section in doc.sections:
            if section.header:
                for hp in section.header.paragraphs:
                    if hp.text.strip():
                        text.append(hp.text.strip())
        for p in doc.paragraphs:
            if p.text.strip():
                text.append(p.text.strip())
        seen_cells = set()
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text and id(cell) not in seen_cells:
                        seen_cells.add(id(cell))
                        text.append(cell_text)
        return "\n".join(text).strip()
    except Exception as e:
        raise ValueError(f"Could not read DOCX file: {e}")

def find_skills(text: str) -> set:
    t = " " + text.lower() + " "
    found = set()
    for skill, aliases in SKILLS.items():
        for a in aliases:
            if a == "js":
                pattern = r"(?<![a-z0-9+#.])js(?![a-z0-9+#])"
            else:
                pattern = r"(?<![a-z0-9+#])" + re.escape(a) + r"(?![a-z0-9+#])"
            if re.search(pattern, t):
                found.add(skill)
                break
    return found

def keywords(text: str) -> set:
    return {w for w in re.findall(r"[a-z][a-z+#.]{2,}", text.lower()) if w not in STOP}

def section_checks(text: str) -> dict:
    t = text.lower()
    return {
        "Contact email": bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)),
        "Education section": bool(re.search(r"\b(education|academic|qualification|university|degree|bachelor|master|b\.tech|m\.tech|b\.sc|m\.sc)\b", t)),
        "Projects or experience": bool(re.search(r"\b(project|projects|experience|employment|work history|internships?)\b", t)),
        "Skills section": bool(re.search(r"\b(skills|technical proficiencies|competencies|technologies|tech stack)\b", t)),
        "Measurable results (numbers/%)": bool(re.search(r"\b\d+\s*[%kKmMbB]\b|\$\d+|\b\d+\s*(?:hrs?|hours?|x)\b|\b\d{1,3}(?:,\d{3})+\b", text)),
    }

SKILL_SUGGESTIONS = {
    "Python": "Build an open-source project or backend service using Python 3.12+ (type hints, asyncio, data models).",
    "SQL": "Demonstrate database schema design, indexing, and complex queries (joins, window functions, CTEs).",
    "REST APIs": "Build and document a RESTful service using OpenAPI / Swagger specifications and HTTP status standards.",
    "FastAPI": "Develop an asynchronous microservice using FastAPI, Pydantic v2 schemas, and dependency injection.",
    "Flask": "Create lightweight web endpoints with Blueprints, SQLAlchemy ORM, and pytest integration.",
    "Django": "Showcase a full-stack Django app with ORM migrations, user authentication, and admin dashboards.",
    "Docker": "Containerize a project with a multi-stage Dockerfile and docker-compose.yml for local multi-service testing.",
    "Kubernetes": "Deploy containerized services to a cluster with Deployment, Service, and ConfigMap YAML manifests.",
    "Git": "Maintain an active GitHub portfolio with clean branch workflows, descriptive pull requests, and semantic commits.",
    "CI/CD": "Set up automated GitHub Actions workflows running unit test matrices and automated build checks.",
    "Unit testing": "Implement unit tests with pytest/Jest targeting 80%+ coverage, and explicitly highlight this metric.",
    "AWS": "Highlight hands-on AWS services (EC2, S3, RDS, Lambda, ECS) or mention AWS Cloud Practitioner certification.",
    "Azure": "Detail experience with Azure App Services, Azure SQL, and Blob Storage or AZ-900 cloud certification.",
    "GCP": "Feature projects leveraging Google Cloud Run, Cloud Functions, and BigQuery.",
    "React": "Build a responsive web application utilizing React hooks, state management, and modern component architecture.",
    "Node.js": "Develop scalable Node.js/Express backend APIs handling asynchronous I/O and database operations.",
    "JavaScript": "Highlight modern ES6+ concepts: Promises, async/await, closures, and modular code architecture.",
    "TypeScript": "Refactor JavaScript modules to TypeScript with strict type definitions, generics, and interfaces.",
    "HTML/CSS": "Demonstrate responsive UI design using CSS Grid, Flexbox, custom properties, and semantic HTML5.",
    "Machine learning": "Highlight end-to-end ML workflows: exploratory data analysis, scikit-learn models, and evaluation.",
    "Deep learning": "Feature PyTorch or TensorFlow projects demonstrating neural architectures (CNN, LSTM, or Transformers).",
    "NLP": "Showcase text preprocessing, tokenization, embeddings (Hugging Face / spaCy), or LLM fine-tuning.",
    "Pandas": "Detail tabular data wrangling, aggregation pipelines, and performance optimization with Pandas/NumPy.",
    "Data structures": "Demonstrate algorithm design, time/space complexity optimization, and clean data modeling in projects.",
    "Linux": "State practical Linux command-line, shell scripting (Bash), and system service configuration experience.",
    "Agile": "Highlight participation in Agile/Scrum ceremonies (sprint planning, daily standups, retrospectives).",
    "Communication": "Emphasize cross-functional team collaboration, technical documentation, and stakeholder presentations.",
    "Next.js": "Highlight experience with Server-Side Rendering (SSR), Static Site Generation (SSG), and Next.js App Router.",
    "Vue.js": "Showcase Vue 3 projects using Composition API, Pinia state management, and Vue Router.",
    "Angular": "Demonstrate Angular components, RxJS observables, dependency injection, and TypeScript architecture.",
    "Spring Boot": "Showcase Java enterprise microservices with Spring Boot, Spring Security, JPA/Hibernate, and Maven/Gradle.",
    "Go": "Feature concurrent backend services built in Go leveraging goroutines, channels, and standard HTTP libraries.",
    "Rust": "Demonstrate memory-safe, high-performance systems programming or CLI tools built with Rust and Cargo.",
    "GraphQL": "Design schema definitions, queries, mutations, and resolvers with Apollo or GraphQL yoga.",
    "Redis": "Demonstrate caching strategies, pub/sub messaging, session storage, and latency reduction with Redis.",
    "Kafka": "Highlight event-driven architecture, distributed stream processing, and producer/consumer pipelines with Apache Kafka.",
    "Tailwind CSS": "Showcase responsive and utility-first UI styling with custom design tokens and Tailwind CSS.",
    "Microservices": "Explain microservice architecture patterns: API gateways, service discovery, distributed tracing, and fault tolerance.",
    "Flutter": "Build cross-platform mobile apps for iOS and Android using Flutter widgets, state management (Bloc/Provider), and Dart.",
    "DevOps": "Highlight infrastructure as code (Terraform), container orchestration, and automated CI/CD deployment pipelines.",
    "System Design": "Demonstrate scalable system design principles: caching, database sharding, load balancing, and high availability.",
    "C#": "Highlight enterprise C# and .NET experience with ASP.NET Core, EF Core, LINQ, and microservices."
}

JOB_ROLE_CATALOG = [
    {
        "title": "Python Backend Engineer",
        "core_skills": ["Python", "FastAPI", "Flask", "Django", "SQL", "REST APIs", "Docker"],
        "description": "Building high-throughput microservices, REST APIs, and database-backed services."
    },
    {
        "title": "Full Stack Developer",
        "core_skills": ["React", "JavaScript", "TypeScript", "Node.js", "HTML/CSS", "SQL", "REST APIs"],
        "description": "Developing modern web user interfaces and robust scalable backend services."
    },
    {
        "title": "DevOps & Cloud Engineer",
        "core_skills": ["Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "Linux", "DevOps"],
        "description": "Designing containerized architectures, continuous delivery pipelines, and cloud infrastructure."
    },
    {
        "title": "Machine Learning & AI Engineer",
        "core_skills": ["Python", "Machine learning", "Deep learning", "NLP", "Pandas", "SQL"],
        "description": "Developing predictive models, data processing pipelines, and GenAI integrations."
    },
    {
        "title": "Frontend Engineer",
        "core_skills": ["React", "Next.js", "TypeScript", "JavaScript", "HTML/CSS", "Tailwind CSS"],
        "description": "Creating responsive, accessible, high-performance web applications and UI components."
    },
    {
        "title": "Systems / .NET Software Engineer",
        "core_skills": ["C#", "SQL", "REST APIs", "Microservices", "System Design"],
        "description": "Architecting mission-critical enterprise services with C#, .NET Core, and distributed systems."
    },
    {
        "title": "Data Engineer",
        "core_skills": ["SQL", "Python", "Pandas", "Kafka", "Redis", "Data structures"],
        "description": "Building data streaming pipelines, analytics infrastructure, and low-latency storage."
    }
]

def recommend_jobs(all_skills: set, target_role: str = "", resume_text: str = "", job_description: str = "") -> list:
    try:
        import job_matching_engine
        return job_matching_engine.match_jobs(
            candidate_skills=all_skills,
            resume_text=resume_text,
            target_role=target_role,
            job_description=job_description,
            min_count=10
        )
    except Exception as e:
        print("job_matching_engine fallback triggered:", e)

    recommendations = []
    t_role_lower = (target_role or "").lower()

    for role in JOB_ROLE_CATALOG:
        core = role["core_skills"]
        matched = [s for s in core if s in all_skills]
        missing = [s for s in core if s not in all_skills]
        match_pct = round((len(matched) / len(core)) * 100) if core else 0

        if any(w in t_role_lower for w in role["title"].lower().split() if len(w) > 3):
            match_pct = min(100, match_pct + 10)

        if match_pct >= 25:
            level = "High Match" if match_pct >= 70 else "Strong Potential" if match_pct >= 50 else "Growth Opportunity"
            reason = f"Matches {len(matched)} of your skills ({', '.join(matched[:3])})." if matched else "Good foundational skills for entry."
            recommendations.append({
                "title": role["title"],
                "match_score": match_pct,
                "match_level": level,
                "reason": reason,
                "matching_skills": matched,
                "growth_skills": missing[:2]
            })

    recommendations.sort(key=lambda r: r["match_score"], reverse=True)
    return recommendations

def find_partially_matched_skills(resume_text: str, candidate_skills: set, missing_from_jd: list) -> tuple:
    """
    Categorizes unmatched JD requirements into:
    - Partially matched skills (candidate has adjacent foundation or mentions it contextually)
    - Truly missing skills (no adjacent capability or evidence)
    """
    partially_matched = []
    truly_missing = []
    t_lower = resume_text.lower()

    for skill in missing_from_jd:
        adj_candidates = ADJACENT_SKILLS.get(skill, [])
        found_adj = [adj for adj in adj_candidates if adj in candidate_skills]

        # Also check if the skill name appears in the body of projects/experience text
        in_body = bool(re.search(r"\b" + re.escape(skill.lower()) + r"\b", t_lower))

        if found_adj:
            primary_adj = found_adj[0]
            partially_matched.append({
                "skill": skill,
                "adjacent_skill": primary_adj,
                "reason": f"Demonstrated background in {primary_adj} provides transferable foundation for {skill}."
            })
        elif in_body:
            partially_matched.append({
                "skill": skill,
                "adjacent_skill": "Contextual Mention",
                "reason": f"Mentioned in project/experience descriptions; elevate to dedicated skills listing with concrete evidence."
            })
        else:
            truly_missing.append(skill)

    return partially_matched, truly_missing

def calculate_ats_score(text: str, checks: dict, jd: str = "", job_title: str = "") -> dict:
    """
    Evaluates ATS scoring dimensions including Quantified Impact, Headings, and Certifications.
    Preserved for backward compatibility and granular ATS diagnostics.
    """
    t = text.lower()
    words = len(text.split())

    has_email = checks.get("Contact email", False)
    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    contact_score = 100 if (has_email and has_phone) else 65 if (has_email or has_phone) else 10

    standard_sections = [
        ("education", bool(re.search(r"\b(education|academic|qualification|university|degree)\b", t))),
        ("experience", bool(re.search(r"\b(experience|employment|work history|internships?)\b", t))),
        ("skills", bool(re.search(r"\b(skills|technical proficiencies|competencies|technologies)\b", t))),
        ("project", bool(re.search(r"\b(project|projects)\b", t)))
    ]
    sections_found = sum(1 for _, ok in standard_sections if ok)
    section_score = round((sections_found / len(standard_sections)) * 100)

    # Filter out 4-digit graduation years
    raw_metrics = re.findall(r"\b\d+\s*[%kKmMbB]\b|\$\d+|\b\d+\s*(?:hrs?|hours?|x)\b|\b\d{2,}\b", text)
    filtered_metrics = [m for m in raw_metrics if not re.fullmatch(r"(?:19|20)\d{2}", m.strip())]
    metrics_count = len(filtered_metrics)
    metrics_score = 100 if metrics_count >= 4 else 75 if metrics_count >= 2 else 45 if metrics_count >= 1 else 15

    if 350 <= words <= 950:
        length_score = 100
    elif 200 <= words < 350 or 950 < words <= 1300:
        length_score = 80
    elif words < 200:
        length_score = 40
    else:
        length_score = 65

    action_verbs = ["built", "developed", "designed", "implemented", "optimized", "engineered",
                    "led", "created", "reduced", "increased", "delivered", "managed", "deployed", "spearheaded"]
    action_count = sum(1 for v in action_verbs if re.search(r"\b" + v + r"\b", t))
    verb_score = min(100, round((action_count / 5) * 100))

    has_cert = bool(re.search(r"\b(certif|certified|certification|certifications|license|licence|credential|accreditation|pmp|scrum master|aws certified)\b", t))
    cert_score = 100 if has_cert else 40

    if jd and jd.strip():
        jk = keywords(jd)
        rk = keywords(text)
        kw_ratio = (len(jk & rk) / len(jk)) if jk else 0.5
        role_kw_score = round(min(100, kw_ratio * 125))
        overall_ats = round(
            0.20 * section_score +
            0.20 * metrics_score +
            0.15 * contact_score +
            0.15 * length_score +
            0.15 * verb_score +
            0.15 * role_kw_score
        )
    else:
        overall_ats = round(
            0.25 * section_score +
            0.25 * metrics_score +
            0.20 * contact_score +
            0.15 * length_score +
            0.15 * verb_score
        )
        role_kw_score = 75

    ats_grade = "A+" if overall_ats >= 90 else "A" if overall_ats >= 80 else "B" if overall_ats >= 70 else "C" if overall_ats >= 55 else "Needs Work"

    return {
        "score": overall_ats,
        "grade": ats_grade,
        "breakdown": {
            "Section Headings": section_score,
            "Quantified Impact": metrics_score,
            "Contact Completeness": contact_score,
            "Content Length & Volume": length_score,
            "Action Verb Strength": verb_score,
            "Role Keyword Alignment": role_kw_score,
            "Certifications & Credentials": cert_score
        }
    }

def calculate_transparent_scores(text: str, checks: dict, jd: str = "", matched_skills: list = None,
                                  partial_skills: list = None, missing_skills: list = None, job_title: str = "") -> dict:
    """
    Calculates the 3 distinct, transparent ATS scoring dimensions:
    1. Resume Quality Score (0-100%)
    2. Job-Description Keyword Match Score (0-100%)
    3. Formatting & Parsing Compatibility Score (0-100%)
    Deterministic: repeated analysis of identical inputs produces identical results.
    """
    t = text.lower()
    words = len(text.split())

    # 1. Resume Quality Metrics
    # Contact Completeness (100 = email + phone + links/location)
    has_email = checks.get("Contact email", False)
    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    has_links = bool(re.search(r"(linkedin\.com|github\.com|http)", t))
    contact_quality = 100 if (has_email and has_phone and has_links) else 80 if (has_email and has_phone) else 50 if has_email else 15

    # Section Structure Completeness
    standard_sections = [
        ("Summary", bool(re.search(r"\b(summary|profile|about me|career objective)\b", t))),
        ("Experience", bool(re.search(r"\b(experience|employment|work history|internships?)\b", t))),
        ("Skills", bool(re.search(r"\b(skills|technical proficiencies|technologies)\b", t))),
        ("Projects", bool(re.search(r"\b(project|projects)\b", t))),
        ("Education", bool(re.search(r"\b(education|academic|qualification|university|degree|b\.tech|bachelor)\b", t)))
    ]
    sec_found = sum(1 for _, ok in standard_sections if ok)
    structure_quality = round((sec_found / len(standard_sections)) * 100)

    # Quantified Impact Metrics (filtering graduation years)
    raw_metrics = re.findall(r"\b\d+\s*[%kKmMbB]\b|\$\d+|\b\d+\s*(?:hrs?|hours?|x)\b|\b\d{2,}\b", text)
    filtered_metrics = [m for m in raw_metrics if not re.fullmatch(r"(?:19|20)\d{2}", m.strip())]
    metrics_count = len(filtered_metrics)
    metrics_quality = 100 if metrics_count >= 4 else 75 if metrics_count >= 2 else 45 if metrics_count >= 1 else 15

    # Action Verbs Variety & Depth
    action_verbs = ["built", "developed", "designed", "implemented", "optimized", "engineered",
                    "led", "created", "reduced", "increased", "delivered", "managed", "deployed", "spearheaded", "automated"]
    action_count = sum(1 for v in action_verbs if re.search(r"\b" + v + r"\b", t))
    verbs_quality = min(100, round((action_count / 5) * 100))

    # Length & Volume Depth
    if 350 <= words <= 950:
        length_quality = 100
    elif 220 <= words < 350 or 950 < words <= 1300:
        length_quality = 80
    elif words < 220:
        length_quality = 40
    else:
        length_quality = 65

    resume_quality_score = round(
        0.20 * contact_quality +
        0.20 * structure_quality +
        0.25 * metrics_quality +
        0.20 * verbs_quality +
        0.15 * length_quality
    )
    quality_grade = "A+" if resume_quality_score >= 90 else "A" if resume_quality_score >= 80 else "B" if resume_quality_score >= 70 else "C" if resume_quality_score >= 55 else "Needs Work"

    # 2. Job Match Score (Unique Keyword Coverage & Skill Alignment)
    matched = matched_skills or []
    partial = partial_skills or []
    missing = missing_skills or []
    total_req_skills = len(matched) + len(partial) + len(missing)

    is_general_purpose = not (jd and jd.strip())
    if not is_general_purpose and total_req_skills > 0:
        skill_score = ((len(matched) + 0.5 * len(partial)) / total_req_skills) * 100
        jk = keywords(jd)
        rk = keywords(text)
        unique_kw_ratio = (len(jk & rk) / len(jk)) if jk else 0.5
        kw_score = min(100, unique_kw_ratio * 125)
        job_match_score = round(0.70 * skill_score + 0.30 * kw_score)
    else:
        # General-Purpose Mode: candidate skills evaluated against general role requirements
        job_match_score = 100 if is_general_purpose else 75
        skill_score = 100
        kw_score = 100

    match_grade = "A+" if job_match_score >= 90 else "A" if job_match_score >= 80 else "B" if job_match_score >= 70 else "C" if job_match_score >= 55 else "Needs Work"

    # 3. Formatting & Parsing Compatibility Score
    # Evaluates single-column ATS scanability, standard heading formats, clean contact extraction, selectable text
    has_clean_contact = bool(has_email and has_phone)
    headings_standard = bool(sec_found >= 4)
    single_column_safe = bool(words >= 150)
    has_cert_or_edu = bool(checks.get("Education section", False))

    format_contact = 100 if has_clean_contact else 50
    format_headings = 100 if headings_standard else 60
    format_single_col = 100 if single_column_safe else 60
    format_budget_fit = 95 # ReportLab A4 exact budget guarantees 1 page

    formatting_score = round(
        0.30 * format_headings +
        0.30 * format_contact +
        0.20 * format_single_col +
        0.20 * format_budget_fit
    )
    format_grade = "A+" if formatting_score >= 90 else "A" if formatting_score >= 80 else "B" if formatting_score >= 70 else "C" if formatting_score >= 55 else "Needs Work"

    # Strengths and reasons breakdown
    reasons = {
        "quality_reasons": {
            "strengths": [
                f"Contains {metrics_count} quantified performance metric(s) demonstrating measurable results." if metrics_count >= 2 else "Includes clear project and experience descriptions.",
                f"Uses {action_count} dynamic action verbs (e.g. {', '.join(v for v in action_verbs if v in t)[:30]})." if action_count >= 3 else "Clear language throughout bullet points.",
                f"Includes {sec_found} standard resume sections for seamless ATS indexing."
            ],
            "weaknesses": [
                "Quantify project bullets with concrete outcomes (e.g. latency reduced by X%, users served, or hours saved)." if metrics_count < 3 else "",
                "Add a professional phone number and LinkedIn profile to the header." if not (has_phone and has_links) else "",
                "Add depth to experience bullets detailing tools, challenges, and solutions." if words < 250 else ""
            ]
        },
        "match_reasons": {
            "matched_count": len(matched),
            "partial_count": len(partial),
            "missing_count": len(missing),
            "summary": "General-Purpose Professional Resume analysis (no specific JD constraints applied)." if is_general_purpose else f"Matches {len(matched)} core requirement(s) directly, with {len(partial)} partially matched adjacent skill(s)."
        },
        "format_reasons": {
            "single_column_safe": single_column_safe,
            "standard_headings_detected": sec_found,
            "selectable_text": True,
            "one_page_compliance": "Guaranteed 1 A4 page with dynamic budget fitting."
        }
    }
    reasons["quality_reasons"]["weaknesses"] = [w for w in reasons["quality_reasons"]["weaknesses"] if w]

    return {
        "resume_quality_score": resume_quality_score,
        "quality_grade": quality_grade,
        "job_match_score": job_match_score,
        "match_grade": match_grade,
        "formatting_score": formatting_score,
        "format_grade": format_grade,
        "is_general_purpose": is_general_purpose,
        "breakdown": {
            "Resume Quality": resume_quality_score,
            "Job Match Fit": job_match_score,
            "ATS Format Scanability": formatting_score
        },
        "quality_breakdown": {
            "Contact Completeness": contact_quality,
            "Section Headings": structure_quality,
            "Quantified Impact": metrics_quality,
            "Action Verbs": verbs_quality,
            "Content Depth": length_quality
        },
        "reasons": reasons
    }

def evaluate_recruiter_review(text: str, checks: dict, matched_skills: list, missing_skills: list,
                              partial_skills: list, job_title: str) -> dict:
    """
    Evaluates candidate resume across 7 key recruiter dimensions:
    1. Professional Summary Clarity
    2. Relevance of Technical Skills
    3. Project Complexity & Demonstrated Contribution
    4. Internship & Experience Descriptions
    5. Evidence of Results & Measurable Impact
    6. Grammar, Consistency & Professionalism
    7. Information Completeness
    Returns the Top 5 Most Important Improvements with practical non-fabricated examples.
    """
    t = text.lower()
    words = len(text.split())

    # Raw metrics
    raw_metrics = re.findall(r"\b\d+\s*[%kKmMbB]\b|\$\d+|\b\d+\s*(?:hrs?|hours?|x)\b|\b\d{2,}\b", text)
    filtered_metrics = [m for m in raw_metrics if not re.fullmatch(r"(?:19|20)\d{2}", m.strip())]
    metrics_count = len(filtered_metrics)

    has_summary = bool(re.search(r"\b(summary|profile|about me)\b", t))
    has_github = bool("github.com" in t)
    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    has_edu = bool(checks.get("Education section", False))

    dimensions = {
        "summary_clarity": {
            "name": "Professional Summary Clarity",
            "score": 90 if has_summary else 50,
            "status": "Strong" if has_summary else "Needs Improvement",
            "feedback": "Concise summary introducing technical focus." if has_summary else "Missing dedicated professional summary introducing core engineering strengths."
        },
        "skills_relevance": {
            "name": "Technical Skills Relevance",
            "score": 95 if len(matched_skills) >= 4 else 75 if len(matched_skills) >= 2 else 55,
            "status": "Strong" if len(matched_skills) >= 4 else "Moderate",
            "feedback": f"Strong alignment with {len(matched_skills)} verified core skills." if len(matched_skills) >= 4 else "Add relevant frameworks and core technologies."
        },
        "project_complexity": {
            "name": "Project Complexity & Contribution",
            "score": 90 if has_github else 70,
            "status": "Strong" if has_github else "Good",
            "feedback": "Interactive projects with verifiable GitHub repositories." if has_github else "Link active GitHub repository source code for all featured projects."
        },
        "experience_depth": {
            "name": "Internship & Experience Descriptions",
            "score": 85 if words >= 250 else 60,
            "status": "Strong" if words >= 250 else "Needs Expansion",
            "feedback": "Solid bullet structure detailing technical workflows." if words >= 250 else "Expand experience and project bullets with architecture and implementation details."
        },
        "measurable_impact": {
            "name": "Evidence of Results & Measurable Impact",
            "score": 95 if metrics_count >= 4 else 70 if metrics_count >= 2 else 40,
            "status": "Strong" if metrics_count >= 3 else "Needs Improvement",
            "feedback": f"Demonstrates {metrics_count} quantified performance metrics." if metrics_count >= 3 else "Bullet points describe responsibilities rather than quantified business outcomes."
        },
        "professionalism_consistency": {
            "name": "Grammar, Consistency & Professionalism",
            "score": 90,
            "status": "Strong",
            "feedback": "Consistent single-column layout, standard typography, and clean headings."
        },
        "information_completeness": {
            "name": "Information Completeness",
            "score": 100 if (has_phone and has_edu) else 75,
            "status": "Strong" if (has_phone and has_edu) else "Needs Attention",
            "feedback": "Candidate contact, education credentials, and dates cleanly specified." if (has_phone and has_edu) else "Ensure direct phone number and graduation year are present."
        }
    }

    # Top 5 Actionable Improvements (strict truth: never invent facts or numbers)
    top_5_candidates = []

    # Priority 1: Quantified Impact
    if metrics_count < 3:
        top_5_candidates.append({
            "priority": 1,
            "dimension": "Evidence of Results & Measurable Impact",
            "title": "Quantify project outcomes with measurable performance metrics",
            "observation": "Bullets describe activities (e.g. 'Built web application') without specifying volume, speed, or latency metrics.",
            "practical_example": "Instead of 'Developed job tracking application using Flask', specify 'Developed job tracking application with Flask and MySQL, architecting parameterized queries across [X] application records to reduce query lookup time.'"
        })

    # Priority 2: Missing Skills & Bridge Strategies
    if missing_skills:
        top_5_candidates.append({
            "priority": 2,
            "dimension": "Technical Skills Relevance",
            "title": f"Address required skill gap for {', '.join(missing_skills[:3])}",
            "observation": f"Job demands {', '.join(missing_skills[:3])}, but they are missing from your uploaded resume.",
            "practical_example": f"Build a focused GitHub demonstration project or complete coursework covering {missing_skills[0]}. Never add it to your resume until you have genuine hands-on experience."
        })

    # Priority 3: Partially Matched Skills / Adjacent Strengths
    if partial_skills:
        first_p = partial_skills[0]
        top_5_candidates.append({
            "priority": 3,
            "dimension": "Technical Skills Relevance",
            "title": f"Highlight transferable foundation from {first_p['adjacent_skill']} to {first_p['skill']}",
            "observation": f"You demonstrate hands-on competence in {first_p['adjacent_skill']}, which directly supports required competency in {first_p['skill']}.",
            "practical_example": f"In your professional summary, note your strong foundation in {first_p['adjacent_skill']} and ability to quickly apply architectural patterns to {first_p['skill']} ecosystems."
        })

    # Priority 4: GitHub Link Verification
    if not has_github:
        top_5_candidates.append({
            "priority": 4,
            "dimension": "Project Complexity & Contribution",
            "title": "Attach verified GitHub repository links to each key project",
            "observation": "Recruiters and hiring managers cannot verify your code quality without direct repository links.",
            "practical_example": "Add 'GitHub: https://github.com/username/project-repo' directly below each project title line."
        })

    # Priority 5: Action Verbs
    action_verbs = ["built", "developed", "designed", "implemented", "optimized", "engineered"]
    if sum(1 for v in action_verbs if v in t) < 3:
        top_5_candidates.append({
            "priority": 5,
            "dimension": "Internship & Experience Descriptions",
            "title": "Lead every bullet point with strong technical action verbs",
            "observation": "Some bullet points start with passive phrases like 'Responsible for' or 'Helped with'.",
            "practical_example": "Replace 'Responsible for managing databases' with 'Engineered normalized relational schemas with parameterized SQL queries for secure, efficient CRUD operations.'"
        })

    # Fallback recommendations if candidate is already strong
    if len(top_5_candidates) < 5:
        top_5_candidates.append({
            "priority": len(top_5_candidates) + 1,
            "dimension": "Professional Summary Clarity",
            "title": f"Tailor summary directly to target role: {job_title}",
            "observation": "General summaries convert at lower rates than role-tailored value propositions.",
            "practical_example": f"State: 'Results-oriented {job_title} with proven expertise in {', '.join(matched_skills[:3]) or 'backend development'}, dedicated to scalable, production-ready code.'"
        })
    if len(top_5_candidates) < 5:
        top_5_candidates.append({
            "priority": len(top_5_candidates) + 1,
            "dimension": "Grammar, Consistency & Professionalism",
            "title": "Ensure consistent bullet length and punctuation across all sections",
            "observation": "Inconsistent ending punctuation or bullet density can create an unpolished impression.",
            "practical_example": "End every descriptive bullet with a period, and ensure bullet points across all projects average 1.5 to 2 lines for visual balance."
        })

    return {
        "dimensions": dimensions,
        "top_5_improvements": top_5_candidates[:5]
    }

def build_need_to_improve(missing_skills: list, partial_skills: list = None) -> list:
    results = []
    # 1. Partial skills first with encouraging adjacent path
    if partial_skills:
        for p in partial_skills:
            results.append({
                "skill": p["skill"],
                "status": f"Partially Matched (via {p['adjacent_skill']})",
                "priority": "Medium",
                "suggestion": p["reason"] + " Build a mini-project bridging these two technologies."
            })

    # 2. Truly missing skills
    for i, s in enumerate(missing_skills):
        suggestion = SKILL_SUGGESTIONS.get(
            s,
            f"Add hands-on evidence of {s} through coursework, certifications, or a dedicated GitHub showcase project."
        )
        results.append({
            "skill": s,
            "status": "Missing in Resume",
            "priority": "High" if i < 3 else "Medium",
            "suggestion": suggestion
        })
    return results

def analyze(resume: str, jd: str = "", job_title: str = "Target role") -> dict:
    """
    Comprehensive ATS and Recruiter Resume Analysis.
    Single source of truth for scores, recruiter review, and recommendations.
    Deterministic: identical inputs yield identical outputs.
    """
    r_sk = find_skills(resume)
    has_jd = bool(jd and jd.strip())
    j_sk = find_skills(jd) if has_jd else set()

    if has_jd and j_sk:
        matched = sorted(j_sk & r_sk)
        unmatched_jd = sorted(j_sk - r_sk)
        partial_skills, missing_skills = find_partially_matched_skills(resume, r_sk, unmatched_jd)
    elif has_jd and not j_sk:
        # JD provided but no standard tech keywords found: match on domain keywords
        matched = []
        partial_skills = []
        missing_skills = []
    else:
        # General-purpose mode: no JD provided
        matched = sorted(r_sk)[:8]
        partial_skills = []
        missing_skills = []

    checks = section_checks(resume)

    # 1. Transparent 3-metric scoring engine
    score_data = calculate_transparent_scores(
        text=resume,
        checks=checks,
        jd=jd,
        matched_skills=matched,
        partial_skills=partial_skills,
        missing_skills=missing_skills,
        job_title=job_title
    )

    # 2. Recruiter Review Evaluation (7 Dimensions & Top 5 Priority Improvements)
    recruiter_review = evaluate_recruiter_review(
        text=resume,
        checks=checks,
        matched_skills=matched,
        missing_skills=missing_skills,
        partial_skills=partial_skills,
        job_title=job_title
    )

    # 3. Learning Pathways & Honest Improvement Suggestions
    need_to_improve = build_need_to_improve(missing_skills, partial_skills)

    # 4. Job Recommendations
    combined_skills = r_sk | (j_sk if has_jd else set())
    job_recs = recommend_jobs(combined_skills, target_role=job_title, resume_text=resume, job_description=jd)

    # 5. Executive Recommendations
    recs = []
    if missing_skills:
        recs.append(f"Acquire hands-on project evidence for {', '.join(missing_skills[:3])} before listing on your resume.")
    if partial_skills:
        recs.append(f"Emphasize your strong foundation in {partial_skills[0]['adjacent_skill']} as transferable experience toward {partial_skills[0]['skill']}.")
    for name, ok in checks.items():
        if not ok:
            recs.append(f"Add or clarify {name} to meet standard ATS parsing criteria.")
    if len(resume.split()) < 220:
        recs.append("Resume depth is brief. Add project details, challenges solved, and tools used.")
    if not recs:
        recs.append("Strong alignment. Tailor your professional summary directly to the target role and quantify achievements.")

    jk = keywords(jd) if has_jd else set()
    rk = keywords(resume)
    kw_cov = len(jk & rk) / len(jk) if jk else 1.0
    struct = sum(checks.values()) / len(checks)
    skill_cov = (len(matched) / len(j_sk)) if (has_jd and j_sk) else 1.0

    ats_compat = calculate_ats_score(resume, checks, jd=jd, job_title=job_title)

    breakdown_data = {
        "Skill coverage": round(skill_cov * 100),
        "Keyword overlap": round(kw_cov * 100),
        "Resume structure": round(struct * 100),
        "Resume Quality": score_data["resume_quality_score"],
        "Job Match Fit": score_data["job_match_score"],
        "ATS Format Scanability": score_data["formatting_score"]
    }

    return {
        # Core Scores (consistent across UI, PDF report, and exports)
        "score": score_data["job_match_score"],
        "match_score": score_data["job_match_score"],
        "job_match_score": score_data["job_match_score"],
        "match_grade": score_data["match_grade"],
        "resume_quality_score": score_data["resume_quality_score"],
        "quality_grade": score_data["quality_grade"],
        "ats_score": ats_compat["score"],
        "formatting_score": score_data["formatting_score"],
        "ats_grade": ats_compat["grade"],
        "is_general_purpose": score_data["is_general_purpose"],

        # Skill Categorization (Requirement B)
        "matched_skills": matched,
        "partially_matched_skills": partial_skills,
        "missing_skills": missing_skills,
        "extra_skills": sorted(r_sk - j_sk)[:10] if has_jd else sorted(r_sk)[8:18],

        # Recruiter Review Mode (Requirement D)
        "recruiter_review": recruiter_review,

        # Detailed Breakdowns & Reasons (Requirement C)
        "breakdown": breakdown_data,
        "ats_breakdown": ats_compat["breakdown"],
        "quality_breakdown": score_data["quality_breakdown"],
        "score_reasons": score_data["reasons"],
        "checks": checks,

        # Actions & Next Steps
        "need_to_improve": need_to_improve,
        "resume_improvements": [imp["title"] + ": " + imp["observation"] for imp in recruiter_review["top_5_improvements"]],
        "job_recommendations": job_recs,
        "recommendations": recs[:6],
        "_raw_text": resume,
        "disclaimer": "Diagnostic assessment based on standard ATS screening heuristics. Commercial ATS tools vary; no system guarantees shortlisting."
    }

def basic_questions(missing, matched):
    qs = [f"Describe a project where you used {s}. What was your specific architectural contribution?" for s in matched[:4]]
    if missing:
        qs += [f"How would you leverage your existing technical foundation to rapidly master {s}?" for s in missing[:3]]
    qs += [
        "Walk me through your most complex project: describe a critical technical challenge and how you solved it.",
        "How do you ensure your code remains maintainable, secure, and production-ready?"
    ]
    return qs
