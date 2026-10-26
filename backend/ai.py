import os, json, re, requests

def gemini_feedback(resume: str, jd: str, result: dict):
    """Returns {'summary','recommendations','questions'} or None if unavailable."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"
    prompt = f"""You are an elite career coach and ATS optimization specialist. Use ONLY facts explicitly stated in the resume. Never invent qualifications, credentials, metrics, percentages, or achievements.
Matched skills: {result.get('matched_skills', [])}.
Missing skills that candidate needs to improve: {result.get('missing_skills', [])}.
Target role: {result.get('job_title', 'Target Role')}.

Return strictly valid JSON with this exact schema:
{{
  "summary": "2 sentences summarizing the candidate's alignment and main competitive advantage.",
  "need_to_improve": [
    {{
      "skill": "<skill_name>",
      "priority": "High",
      "suggestion": "1-2 sentences with concrete advice on how to learn, practice, or demonstrate this skill in projects/resume."
    }}
  ],
  "resume_improvements": [
    "4-6 actionable tips targeting the extracted resume structure, quantifiable impact metrics, and ATS keywords."
  ],
  "recommendations": [
    "5 specific resume improvements to boost recruiter selection."
  ],
  "questions": [
    "8 rigorous interview questions (both technical deep-dives on matched skills and exploratory questions on missing skills)."
  ],
  "bullet_rewrites": [
    {{
      "original": "1-2 weak or unquantified bullet points from the resume",
      "improved": "High-impact rewrite using strong action verbs based strictly on resume facts. NEVER fabricate fake numbers or unverified statistics; use brackets like [X]% or [metric] if quantification needs candidate input."
    }}
  ]
}}
JOB DESCRIPTION:
{jd[:4000]}

RESUME:
{resume[:6000]}"""
    default_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
    models_to_try = [
        default_model,
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    models_to_try = [m.replace("models/", "") for m in dict.fromkeys(models_to_try)]

    for model in models_to_try:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"x-goog-api-key": key}, timeout=15,
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"responseMimeType": "application/json"}})
            if r.status_code != 200:
                print(f"Gemini {model} returned {r.status_code}: {r.text[:120]}")
                # If key is invalid or unauthorized, avoid slow retries
                if r.status_code in (400, 401, 403) and ("API_KEY_INVALID" in r.text or "key not valid" in r.text.lower()):
                    return None
                continue
            candidates = r.json().get("candidates", [])
            if not candidates:
                continue
            text = candidates[0]["content"]["parts"][0]["text"].strip()
            # Robust JSON extraction from response text
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                text = match.group(0)
            elif text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            parsed = json.loads(text.strip())
            if isinstance(parsed, dict):
                return parsed
        except Exception as e:
            print(f"Gemini error with {model}:", e)
            continue
    return None

