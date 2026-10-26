import re, io
try:
    import pymupdf as fitz
except ImportError:
    import fitz
from skills import SKILLS

STOP = set("the a an and or of to in for with on at by is are be as this that from will you your we our have has can must should".split())

def extract_pdf_text(data: bytes) -> str:
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
        "Projects or experience": bool(re.search(r"\b(project|projects|experience|employment|work history)\b", t)),
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

def recommend_jobs(all_skills: set, target_role: str = "") -> list:
    recommendations = []
    t_role_lower = (target_role or "").lower()

    for role in JOB_ROLE_CATALOG:
        core = role["core_skills"]
        matched = [s for s in core if s in all_skills]
        missing = [s for s in core if s not in all_skills]
        match_pct = round((len(matched) / len(core)) * 100) if core else 0

        # Alignment bonus if title words match target role
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
    return recommendations[:4]

def calculate_ats_score(text: str, checks: dict, jd: str = "", job_title: str = "") -> dict:
    t = text.lower()
    words = len(text.split())

    # 1. Contact check (email + phone/location)
    has_email = checks.get("Contact email", False)
    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    contact_score = 100 if (has_email and has_phone) else 65 if (has_email or has_phone) else 10

    # 2. Section Headings check
    standard_sections = [
        ("education", bool(re.search(r"\b(education|academic|qualification|university|degree)\b", t))),
        ("experience", bool(re.search(r"\b(experience|employment|work history)\b", t))),
        ("skills", bool(re.search(r"\b(skills|technical proficiencies|competencies|technologies)\b", t))),
        ("project", bool(re.search(r"\b(project|projects)\b", t)))
    ]
    sections_found = sum(1 for _, ok in standard_sections if ok)
    section_score = round((sections_found / len(standard_sections)) * 100)

    # 3. Measurable Results (Numbers / % / Metrics) - Filter out 4-digit graduation years
    raw_metrics = re.findall(r"\b\d+\s*[%kKmMbB]\b|\$\d+|\b\d+\s*(?:hrs?|hours?|x)\b|\b\d{2,}\b", text)
    filtered_metrics = [m for m in raw_metrics if not re.fullmatch(r"(?:19|20)\d{2}", m.strip())]
    metrics_count = len(filtered_metrics)
    metrics_score = 100 if metrics_count >= 4 else 75 if metrics_count >= 2 else 45 if metrics_count >= 1 else 15

    # 4. Resume Length & Formatting Depth
    if 350 <= words <= 950:
        length_score = 100
    elif 200 <= words < 350 or 950 < words <= 1300:
        length_score = 80
    elif words < 200:
        length_score = 40
    else:
        length_score = 65

    # 5. Bullet & Action Verb screening
    action_verbs = ["built", "developed", "designed", "implemented", "optimized", "engineered",
                    "led", "created", "reduced", "increased", "delivered", "managed", "deployed", "spearheaded"]
    action_count = sum(1 for v in action_verbs if re.search(r"\b" + v + r"\b", t))
    verb_score = min(100, round((action_count / 5) * 100))

    # 6. Certifications & Credentials
    has_cert = bool(re.search(r"\b(certif|certified|certification|certifications|license|licence|credential|accreditation|pmp|scrum master|aws certified)\b", t))
    cert_score = 100 if has_cert else 40

    # 7. Role & Keyword Alignment (if JD provided)
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

def generate_resume_improvements(text: str, checks: dict, ats_data: dict) -> list:
    improvements = []
    t = text.lower()
    words = len(text.split())

    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    if not has_phone:
        improvements.append("Add a direct phone number and location (City, State) to your header so recruiters can quickly reach out.")
    if not checks.get("Contact email", False):
        improvements.append("Ensure your professional email address is visible at the very top of the resume in plain text.")

    raw_metrics = re.findall(r"\b\d+\s*[%kKmMbB]\b|\$\d+|\b\d+\s*(?:hrs?|hours?|x)\b|\b\d{2,}\b", text)
    filtered_metrics = [m for m in raw_metrics if not re.fullmatch(r"(?:19|20)\d{2}", m.strip())]
    metrics_count = len(filtered_metrics)
    if metrics_count < 3:
        improvements.append("Quantify your project achievements with clear metrics (e.g. 'Reduced latency by 35%', 'Scaled to 25k daily users', 'Saved 10 hrs/week').")

    if words < 250:
        improvements.append(f"Resume text is brief ({words} words). Add depth to your experience bullets detailing technical challenges, tools used, and results.")
    elif words > 950:
        improvements.append("Resume length exceeds standard screening brevity. Condense descriptions into punchy, high-impact bullet points.")

    action_verbs = ["built", "developed", "designed", "implemented", "optimized", "engineered", "led", "created"]
    if sum(1 for v in action_verbs if v in t) < 3:
        improvements.append("Begin every experience bullet with a strong action verb (e.g., 'Architected', 'Engineered', 'Optimized', 'Deployed').")

    if not checks.get("Education section", False):
        improvements.append("Include a distinct 'Education' section specifying degree title, institution, and graduation year.")
    if not checks.get("Skills section", False):
        improvements.append("Add a clearly labeled 'Technical Skills' section categorized by Languages, Frameworks, Cloud, and Developer Tools.")

    if not improvements:
        improvements.append("Resume formatting has strong ATS readiness. Tailor bullet keywords specifically for each target job application.")

    return improvements[:6]

def build_need_to_improve(missing_skills: list) -> list:
    results = []
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

def analyze(resume: str, jd: str, job_title: str = "Target role") -> dict:
    r_sk, j_sk = find_skills(resume), find_skills(jd)
    matched, missing = sorted(j_sk & r_sk), sorted(j_sk - r_sk)
    skill_cov = len(matched) / len(j_sk) if j_sk else 0
    jk, rk = keywords(jd), keywords(resume)
    kw_cov = len(jk & rk) / len(jk) if jk else 0
    checks = section_checks(resume)
    struct = sum(checks.values()) / len(checks)
    if j_sk:
        skill_cov = len(matched) / len(j_sk)
        match_score = round(100 * (0.6 * skill_cov + 0.25 * kw_cov + 0.15 * struct))
        skill_breakdown = round(skill_cov * 100)
    else:
        skill_cov = 1.0
        match_score = round(100 * (0.8 * kw_cov + 0.2 * struct))
        skill_breakdown = 100

    ats_data = calculate_ats_score(resume, checks, jd=jd, job_title=job_title)
    resume_improvements = generate_resume_improvements(resume, checks, ats_data)
    need_to_improve = build_need_to_improve(missing)
    job_recs = recommend_jobs(r_sk | j_sk, target_role=job_title)

    recs = []
    if missing:
        recs.append(f"Add evidence for {', '.join(missing[:3])} only if you genuinely have it (projects, coursework, certifications).")
    for name, ok in checks.items():
        if not ok:
            recs.append(f"Missing or unclear: {name}.")
    if len(resume.split()) < 150:
        recs.append("Resume looks short. Add project details and responsibilities.")
    if not recs:
        recs.append("Strong alignment. Tailor your summary to the job title and quantify achievements.")

    return {
        "score": match_score,
        "ats_score": ats_data["score"],
        "ats_grade": ats_data["grade"],
        "ats_breakdown": ats_data["breakdown"],
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": sorted(r_sk - j_sk)[:10],
        "need_to_improve": need_to_improve,
        "resume_improvements": resume_improvements,
        "job_recommendations": job_recs,
        "_raw_text": resume,
        "recommendations": recs[:6],
        "breakdown": {
            "Skill coverage": skill_breakdown,
            "Keyword overlap": round(kw_cov * 100),
            "Resume structure": round(struct * 100)
        },
        "checks": checks,
        "disclaimer": "Estimate based on keyword, skill, and ATS structure analysis. Use as a preparation guide.",
    }

def basic_questions(missing, matched):
    qs = [f"Describe a project where you used {s}. What was your role?" for s in matched[:4]]
    qs += [f"How would you approach learning {s} quickly for this role?" for s in missing[:3]]
    qs += ["Tell me about yourself and why you fit this role.", "Describe a challenging bug you solved and how you found the root cause."]
    return qs

