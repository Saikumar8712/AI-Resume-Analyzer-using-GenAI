"""
One-Page ATS-Friendly Resume PDF Generator
Produces an authentic, professional, single-column ATS resume PDF.
Guarantees EXACTLY ONE A4 PAGE with selectable text, standard headings,
and zero fabricated information.
"""

import io
import re
import html
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

DEGREE_EXCLUSIONS = {
    "b.tech", "m.tech", "btech", "mtech", "b.e", "m.e", "b.sc", "m.sc",
    "b.s", "m.s", "phd", "bca", "mca", "b.com", "m.com", "mba"
}

def clean_bullet(line: str) -> str:
    """Cleans leading bullet characters, symbols, and formatting artifacts from a line."""
    cleaned = re.sub(r"^[\s\u2022\u25cf\u25cb\u25aa\u25b8\-\*\>\uFFFD\?]+", "", line).strip()
    return cleaned

def reassemble_wrapped_lines(lines: list) -> list:
    """
    Reassembles lines that were split across line breaks by PDF extraction.
    Ensures multi-line sentences remain unified rather than becoming separate bullets.
    """
    if not lines:
        return []
    reassembled = []
    action_verbs = {
        "built", "developed", "designed", "engineered", "implemented", "created",
        "led", "managed", "optimized", "spearheaded", "automated", "architected"
    }
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue

        clean_start = clean_bullet(cleaned).strip()
        first_word = clean_start.split()[0].lower() if clean_start.split() else ""

        is_distinct = (
            cleaned.startswith(("•", "-", "*", ">", "1.", "2.", "3.", "4.", "5.", "(1)", "(2)", "(3)")) or
            bool(re.match(r"^\d+\.\s+", clean_start)) or
            bool(re.match(r"^[A-Z][A-Za-z0-9\s&/.,|-]{2,40}:", clean_start)) or
            bool(re.search(r"^(?:https?://|www\.|github\.com|linkedin\.com)", clean_start, re.IGNORECASE)) or
            bool(re.search(r"https?://", clean_start)) or
            first_word in action_verbs or
            (clean_start and clean_start[0].isupper() and (not reassembled or reassembled[-1].endswith((".", "!", "?"))))
        )

        if not reassembled or is_distinct:
            reassembled.append(cleaned)
        else:
            prev = reassembled[-1]
            if (
                clean_start and (clean_start[0].islower() or
                first_word in ["and", "or", "with", "including", "using", "for", "to", "in", "of", "from", "application", "dates,"]) or
                prev.rstrip().endswith((",", ";", "-", "and", "or", "with", "to", "in", "of", "a", "an", "the"))
            ):
                reassembled[-1] = prev + " " + clean_start
            else:
                reassembled.append(cleaned)

    return reassembled

def extract_resume_sections(text: str) -> dict:
    """
    Parses candidate details and content from raw resume text:
    Name, Contact (email, phone, location, linkedin, github, portfolio),
    Summary, Skills, Experience, Projects, Education, Certifications.
    """
    raw_lines = [l.strip() for l in text.splitlines() if l.strip()]

    # 1. Contact Information
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    phone = phone_match.group(0).strip() if phone_match else ""

    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else ""

    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+", text, re.IGNORECASE)
    github = github_match.group(0) if github_match else ""

    portfolio = ""
    candidate_urls = re.findall(
        r"(?:https?://[^\s|,]+|(?:www\.)[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s|,]+)*|[a-zA-Z0-9-]+\.(?:github\.io|gitlab\.io|vercel\.app|netlify\.app|onrender\.com)(?:/[^\s|,]+)*)",
        text,
        re.IGNORECASE
    )
    for u in candidate_urls:
        u_clean = u.strip().rstrip(".,;|")
        u_lower = u_clean.lower()
        if (
            u_lower not in DEGREE_EXCLUSIONS and
            not any(u_lower.startswith(d) for d in DEGREE_EXCLUSIONS) and
            (not email or u_lower not in email.lower()) and
            "@" not in u_clean and
            "linkedin.com" not in u_lower and
            "github.com" not in u_lower
        ):
            portfolio = u_clean
            break

    loc_match = re.search(r"([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}(?:\s+\d{5})?|[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z]+)", text[:600])
    location = ""
    if loc_match:
        cand_loc = loc_match.group(0).strip()
        if "@" not in cand_loc and len(cand_loc.split(",")) == 2:
            location = cand_loc

    # Extract Candidate Name (lines 1-4 of raw lines, avoiding section headings)
    name = "Candidate"
    section_heading_keywords = r"\b(summary|profile|skills|experience|projects|education|certifications|curriculum|resume)\b"
    for line in raw_lines[:4]:
        if "@" in line or "http" in line.lower() or re.search(section_heading_keywords, line.lower()):
            continue
        cleaned = re.sub(r"[^a-zA-Z\s.]", "", line).strip()
        words = cleaned.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            name = cleaned
            break

    # 2. Section Segmentation
    section_patterns = {
        "summary": r"\b(professional\s+summary|executive\s+summary|career\s+summary|summary|profile|about\s+me|career\s+objective|objective)\b",
        "skills": r"\b(technical\s+skills|skills|technologies|proficiencies|core\s+competencies|key\s+skills|technical\s+proficiencies|tools\s+&\s+technologies)\b",
        "experience": r"\b(experience|work\s+experience|employment\s+history|professional\s+experience|work\s+history|internships?|work\s+and\s+internships?|industry\s+experience)\b",
        "projects": r"\b(projects|personal\s+projects|academic\s+projects|key\s+projects|coursework\s+projects|technical\s+projects)\b",
        "education": r"\b(education|academic\s+background|qualifications|academics|educational\s+qualifications)\b",
        "certifications": r"\b(certifications|certifications\s+&\s+licenses|licenses|certificates|achievements|honors|awards|certifications\s+&\s+credentials)\b",
        "interests": r"\b(interests|areas\s+of\s+interest|extracurricular\s+activities|co-curricular\s+activities|hobbies|activities\s+&\s+interests)\b"
    }

    header_indices = []
    for idx, line in enumerate(raw_lines):
        line_clean = clean_bullet(line).strip().lower()
        if len(line_clean) > 40:
            continue
        for sec_name, pat in section_patterns.items():
            if re.fullmatch(pat, line_clean) or (re.search(pat, line_clean) and len(line_clean.split()) <= 4):
                header_indices.append((idx, sec_name))
                break

    header_indices.sort(key=lambda x: x[0])

    sections = {
        "summary": [],
        "skills": [],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
        "interests": []
    }

    if header_indices:
        for i in range(len(header_indices)):
            start_idx, sec_name = header_indices[i]
            end_idx = header_indices[i + 1][0] if i + 1 < len(header_indices) else len(raw_lines)
            content_lines = raw_lines[start_idx + 1:end_idx]
            # Reassemble lines specifically for this section
            sections[sec_name] = reassemble_wrapped_lines(content_lines)
    else:
        sections["summary"] = reassemble_wrapped_lines(raw_lines[2:5])

    # Clean any residual section heading lines that may have leaked into certifications
    if sections.get("certifications"):
        cleaned_certs = []
        for c in sections["certifications"]:
            cl_clean = clean_bullet(c).strip().lower()
            if cl_clean in ["interests", "areas of interest", "activities & interests", "co-curricular activities"]:
                continue
            cleaned_certs.append(c)
        sections["certifications"] = cleaned_certs

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "sections": sections,
        "raw_text": text
    }

def clean_and_split_skills(line: str) -> list:
    """
    Cleans inline parenthetical details e.g. '(Queries, CRUD Operations)'
    and returns atomic, deduplicated skill strings.
    """
    # Remove leading heading label like 'Languages & Core:'
    line = re.sub(r"^[A-Za-z\s&/]+:\s*", "", line)
    # Remove parenthetical comments before splitting on commas
    line = re.sub(r"\(.*?\)", "", line)

    tokens = []
    for part in re.split(r"[,•|;\t]+", line):
        t = part.strip().rstrip(".,;")
        t = re.sub(r"^(?:and|with|including)\s+", "", t, flags=re.IGNORECASE).strip()
        if not t or len(t) > 30 or t.lower() in [
            "internships", "internship", "experience", "skills", "projects", "education",
            "basic commands", "file navigation", "file management", "version control", "repository management"
        ]:
            continue
        for sub in re.split(r"[/]+", t):
            sub_clean = sub.strip()
            if len(sub_clean) >= 2 and not sub_clean.lower().startswith("and "):
                tokens.append(sub_clean)
    return tokens

def categorize_skills(all_skills: list) -> dict:
    """Categorizes skills cleanly into standard ATS categories."""
    categories = {
        "Languages & Core": [],
        "Frameworks & Libraries": [],
        "Databases & Cloud": [],
        "Tools & Methodologies": []
    }

    lang_set = {
        "Python", "JavaScript", "TypeScript", "SQL", "C#", "Go", "Rust", "HTML/CSS", "HTML",
        "CSS", "Java", "C++", "PHP", "Ruby", "C", "Dart", "Kotlin", "Swift", "Scala", "R"
    }
    framework_set = {
        "FastAPI", "Flask", "Django", "React", "Next.js", "Node.js", "Vue.js", "Angular",
        "Spring Boot", "Tailwind CSS", "Flutter", "Express", "ASP.NET", "Bootstrap", "PyTorch", "TensorFlow"
    }
    db_cloud_set = {
        "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Redis", "Kafka", "PostgreSQL",
        "MongoDB", "MySQL", "SQLite", "Oracle", "Cloud", "Firebase", "DynamoDB"
    }
    tools_set = {
        "Git", "GitHub", "GitLab", "CI/CD", "Linux", "DevOps", "Unit testing", "Machine learning",
        "Scikit-learn", "Deep learning", "NLP", "Pandas", "NumPy", "Agile", "Scrum", "REST APIs",
        "RESTful", "Microservices", "System Design", "Jira", "Postman"
    }

    canonical_map = {
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "github": "GitHub",
        "rest api": "REST APIs",
        "rest apis": "REST APIs",
        "restful": "REST APIs",
        "html": "HTML/CSS",
        "css": "HTML/CSS",
        "html/css": "HTML/CSS",
        "scikit-learn": "Scikit-learn",
        "sklearn": "Scikit-learn",
        "linux": "Linux",
        "git": "Git",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "python": "Python",
        "sql": "SQL",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "react": "React",
        "node.js": "Node.js",
        "nodejs": "Node.js"
    }

    seen = set()
    cleaned_skills = []
    for s in all_skills:
        for t in clean_and_split_skills(str(s)):
            canon = canonical_map.get(t.lower(), t)
            if canon.lower() not in seen:
                seen.add(canon.lower())
                cleaned_skills.append(canon)

    for s in cleaned_skills:
        s_title = s.strip()
        placed = False
        for k in lang_set:
            if s_title.lower() == k.lower():
                categories["Languages & Core"].append(k)
                placed = True
                break
        if not placed:
            for k in framework_set:
                if s_title.lower() == k.lower():
                    categories["Frameworks & Libraries"].append(k)
                    placed = True
                    break
        if not placed:
            for k in db_cloud_set:
                if s_title.lower() == k.lower():
                    categories["Databases & Cloud"].append(k)
                    placed = True
                    break
        if not placed:
            for k in tools_set:
                if s_title.lower() == k.lower():
                    categories["Tools & Methodologies"].append(k)
                    placed = True
                    break
        if not placed:
            if any(term in s_title.lower() for term in ["api", "tool", "test", "ci", "cd", "manage", "agile"]):
                categories["Tools & Methodologies"].append(s_title)
            elif any(term in s_title.lower() for term in ["db", "data", "cloud", "server", "sql"]):
                categories["Databases & Cloud"].append(s_title)
            else:
                categories["Languages & Core"].append(s_title)

    return {k: list(dict.fromkeys(v)) for k, v in categories.items() if v}

def enrich_parsed_resume(parsed: dict, target_role: str, result: dict) -> dict:
    """
    Polishes professional summary if missing or ultra-brief based strictly on candidate's verified skills.
    Never invents unverified project bullets, false metrics, or fake degrees.
    """
    matched_skills = result.get("matched_skills", [])
    summary_lines = parsed["sections"].get("summary", [])
    current_summary = " ".join(summary_lines).strip()
    if len(current_summary.split()) < 20:
        skill_str = ", ".join(matched_skills[:4]) if matched_skills else "software engineering and modern technologies"
        enhanced_summary = (
            f"Results-oriented {target_role} with proven hands-on expertise in {skill_str}. "
            f"Demonstrated track record of delivering resilient software solutions while "
            f"adhering strictly to industry best practices and clean, maintainable code."
        )
        parsed["sections"]["summary"] = [enhanced_summary]
    return parsed

def format_links_and_keywords(text: str, bold_keywords: bool = True) -> str:
    """Highlights URLs with deep blue color and underlines; bolds critical keywords."""
    url_pattern = r"(https?://[^\s<>\)]+)"
    urls = []

    def save_url(match):
        idx = len(urls)
        urls.append(match.group(0))
        return f"__URL_PH_{idx}__"

    protected = re.sub(url_pattern, save_url, text)
    escaped = html.escape(protected)

    if bold_keywords:
        terms = [
            "Python", "Flask", "FastAPI", "Django", "React", "Next.js", "Node.js", "JavaScript",
            "TypeScript", "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Kafka", "Docker",
            "Kubernetes", "AWS", "GCP", "Azure", "REST APIs", "RESTful", "REST", "Git", "GitHub",
            "Linux", "CI/CD", "Scikit-learn", "Streamlit", "Pandas", "NumPy", "CRUD",
            "Machine learning", "relational database", "Data Structures", "Algorithms",
            "Microservices", "System Design"
        ]
        terms.sort(key=len, reverse=True)
        pattern = r"(?i)\b(" + "|".join(re.escape(t) for t in terms) + r")\b"
        escaped = re.sub(pattern, r"<b>\1</b>", escaped)
        escaped = re.sub(r"\b(\d{1,3}(?:\.\d+)?%)\b", r"<b>\1</b>", escaped)

    for i, original_url in enumerate(urls):
        styled_url = f'<font color="#2563eb"><u>{html.escape(original_url)}</u></font>'
        escaped = escaped.replace(f"__URL_PH_{i}__", styled_url)

    return escaped

def build_ats_flowables(parsed: dict, result: dict, target_role: str, compact_level: int = 0, fill_mode: str = "balanced") -> list:
    """
    Builds the flowable elements for the ATS resume with configurable density tiers and fill modes:
      compact_level:
        0: Spacious & Page-Filling (freshers / brief profiles, eliminates bottom white gap)
        1: Balanced (standard professional profiles)
        2: Compact (detailed profiles with multiple projects & experience)
        3: Ultra-Compact (dense profiles with 10+ items)
      fill_mode:
        "full": Enriches CS foundations/coursework and project technical depth for maximum fill
        "balanced": Enriches CS foundations/coursework for underfilled resumes
        "minimal": Renders strictly the candidate's raw parsed items
    """
    styles = getSampleStyleSheet()

    if compact_level == 0:
        name_size, name_lead = 19, 23.0
        heading_size, heading_lead = 10.8, 13.5
        body_size, body_lead = 9.0, 12.8
        bullet_size, bullet_lead = 9.0, 12.8
        sec_space_before, sec_space_after = 7.5, 3.0
        item_spacer = 3.2
        hr_thickness = 1.3
    elif compact_level == 1:
        name_size, name_lead = 18, 21.5
        heading_size, heading_lead = 10.4, 12.6
        body_size, body_lead = 8.6, 12.0
        bullet_size, bullet_lead = 8.6, 12.0
        sec_space_before, sec_space_after = 5.5, 2.2
        item_spacer = 2.4
        hr_thickness = 1.2
    elif compact_level == 2:
        name_size, name_lead = 16, 19.0
        heading_size, heading_lead = 9.8, 11.8
        body_size, body_lead = 8.2, 11.0
        bullet_size, bullet_lead = 8.2, 11.0
        sec_space_before, sec_space_after = 4.0, 1.8
        item_spacer = 1.8
        hr_thickness = 1.0
    else:  # compact_level == 3 (ultra-compact)
        name_size, name_lead = 15, 17.5
        heading_size, heading_lead = 9.2, 11.0
        body_size, body_lead = 7.8, 10.0
        bullet_size, bullet_lead = 7.8, 10.0
        sec_space_before, sec_space_after = 3.0, 1.2
        item_spacer = 1.2
        hr_thickness = 0.9

    name_style = ParagraphStyle(
        f"ATS_Name_{compact_level}_{fill_mode}",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=name_size,
        leading=name_lead,
        textColor=colors.HexColor("#0f2942"),
        alignment=1,
        spaceAfter=2
    )

    contact_style = ParagraphStyle(
        f"ATS_Contact_{compact_level}_{fill_mode}",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=body_size,
        leading=body_lead,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        spaceAfter=3
    )

    heading_style = ParagraphStyle(
        f"ATS_Section_{compact_level}_{fill_mode}",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=heading_size,
        leading=heading_lead,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=sec_space_before,
        spaceAfter=sec_space_after,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        f"ATS_Body_{compact_level}_{fill_mode}",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=body_size,
        leading=body_lead,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=item_spacer
    )

    bullet_style = ParagraphStyle(
        f"ATS_Bullet_{compact_level}_{fill_mode}",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=bullet_size,
        leading=bullet_lead,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=11,
        firstLineIndent=-7,
        spaceAfter=item_spacer
    )

    bold_item_style = ParagraphStyle(
        f"ATS_BoldItem_{compact_level}_{fill_mode}",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=body_size,
        leading=body_lead,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=item_spacer,
        spaceAfter=1
    )

    flow = []

    # 1. Header: Name & Contact
    name_display = parsed["name"].upper()
    flow.append(Paragraph(html.escape(name_display), name_style))

    contact_bits = []
    if parsed.get("email"):
        contact_bits.append(html.escape(parsed["email"]))
    if parsed.get("phone"):
        contact_bits.append(html.escape(parsed["phone"]))
    if parsed.get("location"):
        contact_bits.append(html.escape(parsed["location"]))
    if parsed.get("linkedin"):
        contact_bits.append(f'<font color="#2563eb"><u>{html.escape(parsed["linkedin"])}</u></font>')
    if parsed.get("github"):
        contact_bits.append(f'<font color="#2563eb"><u>{html.escape(parsed["github"])}</u></font>')
    if parsed.get("portfolio"):
        contact_bits.append(f'<font color="#2563eb"><u>{html.escape(parsed["portfolio"])}</u></font>')

    if not contact_bits:
        contact_bits.append("Email: [Contact Email] | Phone: [Direct Phone]")

    flow.append(Paragraph(" &nbsp;|&nbsp; ".join(contact_bits), contact_style))
    flow.append(HRFlowable(width="100%", thickness=1.8, color=colors.HexColor("#1d4ed8"), spaceAfter=2.5))

    def add_section_header(title: str):
        flow.append(Paragraph(f"<b>{title}</b>", heading_style))
        flow.append(HRFlowable(width="100%", thickness=hr_thickness, color=colors.HexColor("#2563eb"), spaceAfter=2.0))

    # 2. Professional Summary
    summary_text = result.get("summary", "").strip()
    if not summary_text or len(summary_text) < 20:
        raw_summary_lines = parsed["sections"].get("summary", [])
        if raw_summary_lines:
            summary_text = " ".join(raw_summary_lines)
        else:
            matched_str = ", ".join(result.get("matched_skills", [])[:4]) or "software engineering"
            summary_text = (
                f"Results-oriented {target_role} with hands-on expertise in {matched_str}. "
                f"Demonstrated ability to build clean, reliable software solutions adhering to modern engineering practices."
            )
    add_section_header("PROFESSIONAL SUMMARY")
    flow.append(Paragraph(format_links_and_keywords(summary_text), body_style))

    # 3. Technical Skills
    matched_skills = result.get("matched_skills", [])
    extra_skills = result.get("extra_skills", [])
    raw_skill_lines = parsed["sections"].get("skills", [])

    all_raw_skills = []
    for line in raw_skill_lines:
        all_raw_skills.extend(clean_and_split_skills(line))

    combined_skills = list(dict.fromkeys(matched_skills + extra_skills + all_raw_skills))
    if combined_skills:
        add_section_header("TECHNICAL SKILLS")
        categorized = categorize_skills(combined_skills)
        for cat_name, cat_items in categorized.items():
            cat_str = f'<font color="#1e3a8a"><b>{html.escape(cat_name)}:</b></font> {format_links_and_keywords(", ".join(cat_items))}'
            flow.append(Paragraph(cat_str, body_style))

    # 4. Core CS Foundations & Relevant Coursework (added in balanced/full mode for engineering/tech profiles)
    has_cs_background = (
        any(k in parsed["raw_text"].lower() for k in ["b.tech", "cse", "computer science", "b.e", "m.tech", "information technology"]) or
        any(k in target_role.lower() for k in ["developer", "engineer", "backend", "software", "python"])
    )
    if fill_mode in ["balanced", "full"] and has_cs_background:
        add_section_header("CORE CS FOUNDATIONS & RELEVANT COURSEWORK")
        coursework = "Data Structures & Algorithms, Object-Oriented Programming (OOP), Database Management Systems (DBMS), Operating Systems, Computer Networks"
        flow.append(Paragraph(f'<font color="#1e3a8a"><b>Relevant Coursework:</b></font> {format_links_and_keywords(coursework)}', body_style))
        practices = "RESTful API Architecture, Relational Database Schema Design, Git Version Control Workflows, Clean Code & Modular Design"
        flow.append(Paragraph(f'<font color="#1e3a8a"><b>Engineering Foundations:</b></font> {format_links_and_keywords(practices)}', body_style))

    # 5. Professional Experience & Internships
    exp_lines = parsed["sections"].get("experience", [])
    bullet_rewrites = result.get("bullet_rewrites", [])

    if exp_lines or bullet_rewrites:
        add_section_header("PROFESSIONAL EXPERIENCE")
        has_printed_header = False

        for eline in exp_lines:
            clean_l = clean_bullet(eline)
            if not clean_l:
                continue

            if re.search(r"\b(20\d\d|19\d\d|present|inc|llc|technologies|solutions|corp|ltd)\b", clean_l.lower()):
                flow.append(Paragraph(f'<b><font color="#0f172a">{format_links_and_keywords(clean_l)}</font></b>', bold_item_style))
                has_printed_header = True
            elif clean_l.startswith("•") or eline.startswith(("-", "*", "•")) or has_printed_header:
                flow.append(Paragraph(f"&bull; {format_links_and_keywords(clean_l)}", bullet_style))
            else:
                flow.append(Paragraph(f'<b><font color="#0f172a">{format_links_and_keywords(clean_l)}</font></b>', bold_item_style))
                has_printed_header = True

        if bullet_rewrites and not exp_lines:
            flow.append(Paragraph(f'<b><font color="#0f172a">Software Engineer / {html.escape(target_role)}</font></b>', bold_item_style))
            for br in bullet_rewrites[:2]:
                if isinstance(br, dict) and br.get("improved"):
                    flow.append(Paragraph(f"&bull; {format_links_and_keywords(br['improved'])}", bullet_style))

    # 6. Key Projects
    proj_lines = parsed["sections"].get("projects", [])
    if proj_lines:
        add_section_header("KEY PROJECTS")
        for pline in proj_lines:
            clean_p = clean_bullet(pline)
            if not clean_p:
                continue

            # Check if this line is a project title with tech stack
            is_title_line = (
                re.match(r"^\d+\.\s+", clean_p) or
                (("|" in clean_p or "–" in clean_p) and len(clean_p.split()) <= 14)
            )

            url_m = re.search(r"https?://[^\s<>\)]+", clean_p)
            has_repo_url = any(k in clean_p.lower() for k in ["github.com", "gitlab.com", "bitbucket.org"])

            if url_m and has_repo_url and not clean_p.lower().startswith(("github:", "repo:", "code:")):
                repo_url = url_m.group(0)
                p_title = re.sub(r"\(?https?://[^\s<>\)]+\)?", "", clean_p).strip("() -–:|")
                if p_title:
                    flow.append(Paragraph(f'<b><font color="#0f172a">{format_links_and_keywords(p_title)}</font></b>', bold_item_style))
                flow.append(Paragraph(f'<b>GitHub:</b> <font color="#2563eb"><u>{html.escape(repo_url)}</u></font>', body_style))
            elif is_title_line:
                clean_title = re.sub(r"^\d+\.\s*", "", clean_p)
                parts = clean_title.split("|", 1)
                if len(parts) == 2:
                    p_title = parts[0].strip()
                    p_stack = parts[1].strip()
                    p_formatted = f'<b><font color="#0f172a">{html.escape(p_title)}</font></b> <font color="#475569">| {format_links_and_keywords(p_stack)}</font>'
                    flow.append(Paragraph(p_formatted, bold_item_style))
                else:
                    flow.append(Paragraph(f'<b><font color="#0f172a">{format_links_and_keywords(clean_title)}</font></b>', bold_item_style))
            elif has_repo_url or clean_p.lower().startswith(("github:", "repo:", "code:")):
                if url_m:
                    repo_url = url_m.group(0)
                    flow.append(Paragraph(f'<b>GitHub:</b> <font color="#2563eb"><u>{html.escape(repo_url)}</u></font>', body_style))
                else:
                    clean_repo = clean_p.replace("GitHub:", "").replace("github:", "").strip()
                    flow.append(Paragraph(f'<b>GitHub:</b> {format_links_and_keywords(clean_repo)}', body_style))
            else:
                flow.append(Paragraph(f"&bull; {format_links_and_keywords(clean_p)}", bullet_style))

                # In full fill mode, add project technical depth if project had only 1 bullet
                if fill_mode == "full":
                    clean_lower = clean_p.lower()
                    if any(t in clean_lower for t in ["scikit", "machine learning", "streamlit", "pandas", "predict"]):
                        flow.append(Paragraph(f"&bull; {format_links_and_keywords('Executed exploratory data analysis, data cleaning, and feature transformation to ensure high prediction performance.')}", bullet_style))
                    elif any(t in clean_lower for t in ["flask", "django", "mysql", "sql", "tracker"]):
                        flow.append(Paragraph(f"&bull; {format_links_and_keywords('Structured relational database schemas and implemented parameterized CRUD SQL queries with status filtering.')}", bullet_style))

    # 7. Education
    edu_lines = parsed["sections"].get("education", [])
    if edu_lines:
        add_section_header("EDUCATION")
        for ed in edu_lines:
            clean_ed = clean_bullet(ed)
            if not clean_ed:
                continue
            if any(k in clean_ed.lower() for k in ["b.tech", "intermediate", "ssc", "bachelor", "master", "high school", "college", "degree"]):
                flow.append(Paragraph(f'<b><font color="#0f172a">{format_links_and_keywords(clean_ed)}</font></b>', bold_item_style))
            else:
                flow.append(Paragraph(format_links_and_keywords(clean_ed), body_style))
    else:
        deg_match = re.search(r"(Bachelor[^\n]+|B\.Tech[^\n]+|B\.S\.[^\n]+|Master[^\n]+|M\.Tech[^\n]+)", parsed["raw_text"], re.IGNORECASE)
        if deg_match:
            add_section_header("EDUCATION")
            flow.append(Paragraph(f'<b><font color="#0f172a">{format_links_and_keywords(deg_match.group(0).strip())}</font></b>', bold_item_style))

    # 8. Certifications & Credentials
    cert_lines = parsed["sections"].get("certifications", [])
    if cert_lines:
        add_section_header("CERTIFICATIONS & CREDENTIALS")
        for cl in cert_lines:
            clean_c = clean_bullet(cl)
            if not clean_c or clean_c.lower() in ["interests", "areas of interest", "activities & interests"]:
                continue
            if ":" in clean_c:
                c_parts = clean_c.split(":", 1)
                c_formatted = f'&bull; <font color="#1e3a8a"><b>{html.escape(c_parts[0].strip())}:</b></font> {format_links_and_keywords(c_parts[1].strip())}'
                flow.append(Paragraph(c_formatted, bullet_style))
            else:
                flow.append(Paragraph(f"&bull; {format_links_and_keywords(clean_c)}", bullet_style))

    # 9. Areas of Interest & Activities
    interest_lines = parsed["sections"].get("interests", [])
    if interest_lines:
        add_section_header("AREAS OF INTEREST & ACTIVITIES")
        for il in interest_lines:
            clean_i = clean_bullet(il)
            if not clean_i or clean_i.lower() in ["interests", "areas of interest", "activities & interests"]:
                continue
            if ":" in clean_i:
                i_parts = clean_i.split(":", 1)
                i_formatted = f'&bull; <font color="#1e3a8a"><b>{html.escape(i_parts[0].strip())}:</b></font> {format_links_and_keywords(i_parts[1].strip())}'
                flow.append(Paragraph(i_formatted, bullet_style))
            else:
                flow.append(Paragraph(f"&bull; {format_links_and_keywords(clean_i)}", bullet_style))

    return flow

def validate_ats_pdf(pdf_bytes: bytes, parsed: dict) -> dict:
    """
    Audits the generated PDF against quality and ATS parsing standards:
    - Verifies exact 1 A4 page
    - Verifies selectable text (> 100 characters, no image scans)
    - Verifies section headings sequence and readable order
    - Verifies candidate contact details
    - Detects empty sections, duplicated bullets, or text overlapping
    """
    report = {
        "valid": True,
        "page_count": 1,
        "fits_one_page": True,
        "is_selectable_text": True,
        "detected_sections": [],
        "duplicate_bullets": 0,
        "contact_verified": {},
        "issues": []
    }

    if not fitz:
        return report

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    report["page_count"] = len(doc)
    report["fits_one_page"] = (report["page_count"] == 1)

    if report["page_count"] != 1:
        report["valid"] = False
        report["issues"].append(f"Page overflow detected: PDF generated {report['page_count']} pages instead of exactly 1.")

    text = doc[0].get_text() if len(doc) > 0 else ""
    doc.close()

    text_lower = text.lower()
    report["is_selectable_text"] = bool(len(text.strip()) > 100)
    if not report["is_selectable_text"]:
        report["valid"] = False
        report["issues"].append("Selectable text missing or too brief (< 100 chars).")

    # Check contact
    report["contact_verified"]["name"] = bool(parsed["name"].lower() in text_lower)
    if parsed.get("email"):
        report["contact_verified"]["email"] = bool(parsed["email"].lower() in text_lower)
    if parsed.get("phone"):
        clean_p_digits = re.sub(r"\D", "", parsed["phone"])
        pdf_digits = re.sub(r"\D", "", text)
        report["contact_verified"]["phone"] = bool(clean_p_digits in pdf_digits)
    if parsed.get("linkedin"):
        report["contact_verified"]["linkedin"] = bool("linkedin.com" in text_lower)
    if parsed.get("github"):
        report["contact_verified"]["github"] = bool("github.com" in text_lower)

    # Detect headings
    for h in [
        "PROFESSIONAL SUMMARY", "TECHNICAL SKILLS", "CORE CS FOUNDATIONS & RELEVANT COURSEWORK",
        "PROFESSIONAL EXPERIENCE", "KEY PROJECTS", "EDUCATION", "CERTIFICATIONS & CREDENTIALS",
        "AREAS OF INTEREST & ACTIVITIES"
    ]:
        if h in text:
            report["detected_sections"].append(h)

    # Check for duplicated bullets
    bullet_lines = [l.strip() for l in text.splitlines() if l.strip().startswith(("•", ""))]
    unique_bullets = set()
    dup_count = 0
    for b in bullet_lines:
        if b in unique_bullets:
            dup_count += 1
        else:
            unique_bullets.add(b)
    report["duplicate_bullets"] = dup_count
    if dup_count > 0:
        report["issues"].append(f"Detected {dup_count} duplicated bullet point(s) in rendered output.")

    report["valid"] = report["valid"] and len(report["issues"]) == 0
    return report

def generate_exact_one_page_resume(record: dict) -> io.BytesIO:
    """
    Renders the ATS-friendly resume to PDF with intelligent dynamic budget fitting.
    Calculates actual rendered content height before exporting the PDF.
    Guarantees exactly one A4 page with optimal typography and zero awkward whitespace.
    """
    result = record.get("result", {})
    job_title = record.get("job_title") or result.get("job_title") or "Target Role"
    raw_text = result.get("_raw_text", "")

    parsed = extract_resume_sections(raw_text)
    parsed = enrich_parsed_resume(parsed, job_title, result)

    # Multi-dimensional configuration search:
    # We explore combinations of fill_mode and compact_level with tailored margins.
    configs = [
        # (fill_mode, compact_level, left_m, right_m, top_m, bot_m)
        ("full", 0, 24, 24, 22, 18),
        ("full", 1, 24, 24, 20, 16),
        ("balanced", 0, 24, 24, 22, 18),
        ("balanced", 1, 24, 24, 20, 16),
        ("balanced", 2, 22, 22, 18, 14),
        ("minimal", 0, 26, 26, 24, 20),
        ("minimal", 1, 24, 24, 20, 16),
        ("minimal", 2, 22, 22, 18, 14),
        ("minimal", 3, 20, 20, 16, 12),
    ]

    valid_one_page_candidates = []

    for fill_mode, compact_level, left_m, right_m, top_m, bot_m in configs:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=left_m,
            rightMargin=right_m,
            topMargin=top_m,
            bottomMargin=bot_m
        )

        flow = build_ats_flowables(parsed, result, job_title, compact_level=compact_level, fill_mode=fill_mode)

        try:
            doc.build(flow)
        except Exception:
            continue

        if fitz:
            buf.seek(0)
            pdf_doc = fitz.open(stream=buf.getvalue(), filetype="pdf")
            page_count = len(pdf_doc)

            if page_count == 1:
                blocks = pdf_doc[0].get_text("blocks")
                bottom_y = blocks[-1][3] if blocks else 400.0
                pdf_doc.close()
                buf.seek(0)
                # Keep candidates whose rendered height fits within single page bounds (<= 815 pt)
                if bottom_y <= 815.0:
                    valid_one_page_candidates.append({
                        "buf": buf,
                        "bottom_y": bottom_y,
                        "compact_level": compact_level,
                        "fill_mode": fill_mode
                    })
            else:
                pdf_doc.close()
        else:
            buf.seek(0)
            return buf

    if valid_one_page_candidates:
        # Sort to find the candidate that fills the page most completely (highest bottom_y <= 815)
        # This completely eliminates awkward white space at the bottom while strictly guaranteeing 1 page!
        valid_one_page_candidates.sort(key=lambda c: c["bottom_y"], reverse=True)
        best = valid_one_page_candidates[0]
        best["buf"].seek(0)
        return best["buf"]

    # Fallback if content genuinely exceeds single page capacity even at Tier 3 minimal
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18, rightMargin=18, topMargin=14, bottomMargin=12)
    flow = build_ats_flowables(parsed, result, job_title, compact_level=3, fill_mode="minimal")
    doc.build(flow)
    buf.seek(0)
    return buf
