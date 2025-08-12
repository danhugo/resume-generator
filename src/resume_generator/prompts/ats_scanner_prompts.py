KEYWORD_ANALYSIS_PROMPT = """
You are an ATS keyword analyzer. Extract and match keywords between resume and job description.

TASK: Find exact keyword matches for ATS screening.

INSTRUCTIONS:
- Extract technical terms, job titles, certifications, tools from both texts
- Use exact phrases as written (case-insensitive matching)
- Calculate match percentage: (job keywords found in resume / total job keywords) × 100
- Focus on ATS-relevant terms: skills, technologies, certifications, job functions

FORMAT:
- "job_keywords": keywords from job description,
- "resume_keywords": keywords from resume,
- "match_score": match score (0–100) is calculated as follows:
  - "match_score": (len(set(job_keywords) & set(resume_keywords)) / len(set(job_keywords))) * 100
- If no keywords found, set:
  - "match_score": 0

Call ATSKeywordAnalysis Tool.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}
"""

SKILLS_ANALYSIS_PROMPT = """
You are an ATS skills matcher. Extract and compare skills between job requirements and candidate resume.

TASK: Identify required/preferred skills and calculate match rates.

INSTRUCTIONS:
- Extract required skills (must-have, required, essential)
- Extract preferred skills (nice-to-have, preferred, bonus)
- Extract all candidate skills from resume
- Match skills using case-insensitive partial matching
- Calculate: required_score = (matched required / total required) × 100
- Calculate: preferred_score = (matched preferred / total preferred) × 100

FORMAT:
- "required_skills": required skills from job description,
- "preferred_skills": preferred skills from job description,
- "candidate_skills": skills extracted from the candidate's resume,
- "required_score": required skills match score (0–100), which is calculated as follows:
  - "required_score": (len(set(required_skills) & set(candidate_skills)) / len(set(required_skills))) * 100
- "preferred_score": preferred skills match score (0–100), which is calculated as follows
  - "preferred_score": (len(set(preferred_skills) & set(candidate_skills)) / len(set(preferred_skills))) * 100
- If no required or preferred skills are found, set:
  - "required_score": 0
  - "preferred_score": 0

Call ATSSkillAnalysis Tool.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}
"""

EXPERIENCE_ANALYSIS_PROMPT = """
You are an ATS experience evaluator. Assess candidate experience quality and relevance.

TASK: Rate experience quality for ATS scoring.

EVALUATION CRITERIA:
- Role relevance to target position
- Industry alignment
- Years of experience vs requirements
- Seniority level progression
- Achievement impact

QUALITY RATINGS:
- HIGH (80-100): Strong relevant experience exceeding requirements
- MEDIUM (60-79): Adequate experience meeting requirements
- LOW (0-59): Limited or misaligned experience

FORMAT:
- "experience_quality": "high", "medium", or "low", which is determined based on the evaluation criteria.
- "experience_score": int score (0–100) based on the quality rating.
- "analysis": concise explanation of the experience quality assessment.

Call ATSExperienceAnalysis Tool.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}
"""

EDUCATION_ANALYSIS_PROMPT = """
You are an ATS education analyzer. Compare education levels for screening.

TASK: Match candidate education against job requirements.

EDUCATION LEVELS:
1 = High school/GED
2 = Associate/Certificate
3 = Bachelor's degree
4 = Master's degree
5 = PhD/Doctorate

SCORING RULES:
- Meets/exceeds requirement: 100 points
- One level below: 75 points
- Two levels below: 50 points
- Three+ levels below: 25 points

FORMAT:
- "candidate_level": int (1-5) representing candidate's highest education level.
- "required_level": int (1-5) representing minimum required education level for the job.
- "education_score": int (0–100) based on the scoring rules.
- "meets_requirement": bool indicating if candidate meets or exceeds required level.
- If candidate education is not provided, set:
- "candidate_level": 0,
- "required_level": 0,
- "education_score": 0,
- "meets_requirement": false

Call ATSEducationAnalysis Tool.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}
"""

FORMAT_ANALYSIS_PROMPT = """
You are an ATS format checker. Evaluate resume ATS compatibility.

TASK: Check format requirements for ATS processing.

INPUT: Plaintext resume content only (no file structure or visual formatting available).

ATS FORMAT CHECKLIST (Content-Level Only):
- Length: Between 100 and 5,000 characters
- Contact Info:
  - Must include a valid email address
  - Preferably includes phone number and/or location
- Required Sections (detectable by header keywords):
  - Work Experience or Professional Experience
  - Education
  - Skills
- Date Formats:
  - Employment/education dates use consistent YYYY or MM/YYYY formats
- Section Headers:
  - Clearly labeled with standard keywords (e.g., “Experience”, “Education”, “Skills”)
- Bullet Points (optional):
  - Experience descriptions use basic bullet-style formatting (-, *, •) or newline lists

SCORING:
- All requirements met: 90–100
- Minor issues (1–2 checklist items missed): 70–89
- Major issues (3–4 items missed): 50–69
- ATS incompatible (5+ items missed): 0–49

RETURN FORMAT:
-  format_score: format score from 0 to 100,
-  analysis: concise summary of format issues or validation points.

Call ATSFormatAnalysis Tool.

RESUME:
{resume}
"""

FEEDBACK_GENERATION_PROMPT = """
You are an ATS feedback evaluator. Generate actionable and constructive feedback based on the analysis of a resume.

TASK: Create a list of professional feedback points to guide candidates in improving their resume for better ATS compatibility and alignment with the job description.

FEEDBACK CRITERIA:
- Keyword and skill match relevance
- Missing or weak qualifications (experience, education)
- ATS format compliance
- Areas of strength or optimization
- Critical issues affecting ATS ranking

FEEDBACK STYLE:
- Bullet point list
- Concise and professional tone
- Highlight both strengths and weaknesses
- Prioritize critical improvements

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}
"""




