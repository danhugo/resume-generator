keyword_analysis_prompt = """
You are an AI assistant evaluating how well a resume matches a job description.

Your task:
1. Extract relevant keywords *exactly as they appear* in the **job description**.
2. Extract relevant keywords *exactly as they appear* in the **resume**.
3. Compare both sets of keywords and compute a match score:
   - The score is the percentage of job keywords that are also found in the resume (case-insensitive match, exact phrase).
   - Do not infer, reword, or generalize. Use only the literal words/phrases present in the text.

Output format:
{
  "job_keywords": [...],       // list of keywords from job description (exact phrases)
  "resume_keywords": [...],    // list of keywords from resume (exact phrases)
  "match_score": float         // % of job_keywords found in resume_keywords
}

Job Description:
{job_description}

Resume:
{raw_resume}
"""

skills_analysis_prompt = """
You are an AI assistant in an Applicant Tracking System (ATS).

Given only the full text of a candidate's resume and a job description:

1. Extract the list of **required skills** and **preferred skills** from the job description.
2. Extract the list of **skills** from the resume.
3. Compare the extracted candidate skills to the required and preferred skills.
4. A skill is matched if it appears clearly in both documents (case-insensitive, partial matches allowed).
5. Calculate the percentage of required and preferred skills matched.

Input:

Job Description:
{job_description}

Resume:
{raw_resume}

Output format:

{
  "required_skills": [list of extracted required skills],
  "preferred_skills": [list of extracted preferred skills],
  "candidate_skills": [list of skills extracted from the resume],
  "matched_required": [list of required skills found in candidate skills],
  "matched_preferred": [list of preferred skills found in candidate skills],
  "required_score": int (percentage of required skills matched),
  "preferred_score": int (percentage of preferred skills matched)
}
"""

experience_quality_prompt = """
You are an ATS assistant.

Evaluate the quality of the candidate's work experience in relation to the job description.

Based on the resume and job description, assess how strong and relevant the candidate’s past roles and responsibilities are for this position.

Output format:
{
  "experience_quality": "high" | "medium" | "low",
  "analysis": string
}

Resume:
{raw_resume}

Job Description:
{job_description}
"""

education_score_prompt = """
You are an ATS system.

Based on the resume and job description, determine the candidate's highest education level and compare it to the required education level.

Return only a JSON object:
{
  "candidate_level": int,  // 1: high school, 2: associate, 3: bachelor, 4: master, 5: phd
  "required_level": int,
  "education_score": int,  // 0–100
  "meets_requirement": boolean
}

Resume:
{raw_resume}

Job Description:
{job_description}
"""

resume_format_prompt = """
You are an ATS (Applicant Tracking System). Evaluate the resume formatting and compatibility based on the following criteria. The resume text is below.

Resume:
{raw_resume}

Check for:
- Length issues (too short < 100 chars or too long > 10,000 chars)
- Presence of contact information (e.g., email address)
- Sections: "experience" or "work", "education", and "skills"
- Number of standard sections present: summary, objective, experience, education, skills
- Whether dates are included in experience (formats like YYYY, MM/YYYY, MM-YYYY)

Return JSON with:
{
  "decision": boolean,  // true if the resume is ATS-friendly (passes minimum format requirements), false otherwise
  "assessment": [string]  // List of specific format issues or validation points, e.g. ["No skills section", "Missing dates in experience"]
}
"""




