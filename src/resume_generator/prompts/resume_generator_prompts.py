"""Prompts for Resume Generator Module"""

PROFILE_ANALYSIS_PROMPT = """
Analyze the following candidate profile to identify key strengths, relevant experience, and unique value propositions.

Candidate Profile:
{candidate_profile}

Target Job Description:
{job_description}

Focus on:
1. Core competencies and strengths that align with the job
2. Relevant professional experience and achievements
3. Any skill gaps that need to be addressed or compensated
4. Unique value propositions that differentiate this candidate

Return a structured analysis highlighting what makes this candidate valuable for the role.
"""

JOB_ANALYSIS_PROMPT = """
Parse and analyze the following job description to extract key requirements and optimization opportunities.

Job Description:
{job_description}

Extract and categorize:
1. Required technical and soft skills
2. Preferred qualifications and nice-to-haves
3. Key responsibilities and expectations
4. Company culture hints and values
5. Critical keywords for ATS optimization

Provide a comprehensive breakdown to guide resume tailoring.
"""

MATCH_MATRIX_PROMPT = """
Create a detailed matching matrix between the candidate profile and job requirements.

Profile Analysis:
{profile_analysis}

Job Analysis:
{job_analysis}

Candidate Profile:
{candidate_profile}

Evaluate:
1. Skill-by-skill matching for required competencies
2. Experience relevance to job responsibilities
3. Education and certification alignment
4. Overall fit percentage
5. Specific recommendations for resume optimization

Provide actionable insights on how to best position this candidate.
"""

RESUME_GENERATION_PROMPT = """
Generate a tailored, ATS-friendly resume based on the following inputs.

Candidate Profile:
{candidate_profile}

Job Requirements:
{job_analysis}

Match Matrix & Recommendations:
{match_matrix}

Resume Requirements:
1. Use STAR methodology for achievements (Situation, Task, Action, Result)
2. Incorporate {keyword_percentage}% of identified keywords naturally
3. Quantify achievements with metrics where possible
4. Use strong action verbs (led, developed, implemented, achieved)
5. Optimize for ATS parsing (clean formatting, standard sections)
6. Tailor content to emphasize relevant experience

Generate a complete resume with the following sections:
- Professional Summary (2-3 lines highlighting key qualifications)
- Core Skills (relevant technical and soft skills)
- Professional Experience (reverse chronological, achievement-focused)
- Education & Certifications
- Additional sections if relevant (Projects, Publications, etc.)

Format in clean, scannable structure.
"""

RESUME_EVALUATION_PROMPT = """
Evaluate the generated resume against best practices and job requirements.

Generated Resume:
{resume}

Job Description:
{job_description}

Required Keywords:
{keywords}

Assess the following criteria:
1. Keyword Coverage: What percentage of critical keywords are included?
2. ATS Friendliness: Is the format clean and parseable?
3. Clarity & Readability: Is the content clear and well-structured?
4. Achievement Focus: Are accomplishments quantified and impactful?
5. Overall Quality: Does this resume effectively position the candidate?

Provide specific scores (0-100) and detailed improvement suggestions.
"""

FEEDBACK_GENERATION_PROMPT = """
Generate actionable feedback for resume revision based on the evaluation.

Resume Evaluation:
{evaluation}

Current Resume:
{resume}

Job Requirements:
{job_analysis}

Iteration: {iteration_count} of {max_iterations}

Provide:
1. Strengths: What's working well in the current version
2. Weaknesses: Critical gaps or issues to address
3. Specific Revisions: Line-by-line suggestions for improvement
4. Priority Changes: Top 3-5 changes that will have the most impact

Focus on actionable, specific feedback that can be implemented immediately.
"""

RESUME_REVISION_PROMPT = """
Revise the resume based on the provided feedback.

Current Resume:
{resume}

Feedback:
{feedback}

Job Requirements:
{job_analysis}

Human Feedback (if any):
{human_feedback}

Apply the following revisions:
1. Address all priority changes identified in feedback
2. Strengthen weak areas while maintaining strengths
3. Improve keyword integration without keyword stuffing
4. Enhance achievement descriptions with better metrics
5. Ensure consistent formatting and professional tone

Generate an improved version that addresses all feedback points.
"""

FINAL_FORMAT_PROMPT = """
Format the final resume for export in the requested format.

Final Resume Content:
{resume}

Export Format: {format}

Requirements:
1. Ensure consistent formatting throughout
2. Optimize line spacing and margins for readability
3. Use appropriate bullet points and separators
4. Maintain ATS compatibility
5. Professional appearance suitable for the industry

Return the formatted resume ready for export.
"""