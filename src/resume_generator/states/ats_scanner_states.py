from typing import TypedDict, Dict, Any, List, Annotated, Literal
from pydantic import BaseModel, Field, conint

class ATSFormatAnalysis(BaseModel):
    format_score: int = Field(description="Percentage of format score from 0 to 100")
    analysis: str = Field(description='Format issues or validation points, e.g. No skills section, Missing dates in experience')

class ATSKeywordAnalysis(BaseModel):
    job_keywords: List[str] = Field(..., description="Exact keywords from job description")
    resume_keywords: List[str] = Field(..., description="Exact keywords from resume")
    match_score: int = Field(..., ge=0, le=100, description="Match score (0–100)")

class ATSSkillAnalysis(BaseModel):
    required_skills: List[str] = Field(..., description="Skills extracted as required from the job description")
    preferred_skills: List[str] = Field(..., description="Skills extracted as preferred from the job description")
    candidate_skills: List[str] = Field(..., description="Skills extracted from the candidate's resume")
    required_score: int = Field(..., ge=0, le=100, description="Percentage of required skills matched")
    preferred_score:int = Field(..., ge=0, le=100, description="Percentage of preferred skills matched")

class ATSExperienceAnalysis(BaseModel):
    experience_quality: str = Field(..., description="Overall quality of the candidate's experience: 'high', 'medium', 'low'")
    experience_score: int = Field(..., ge=0, le=100, description="Percentage of experience score")
    analysis: str = Field(..., description="Explanation of the experience quality assessment")

class ATSEducationAnalysis(BaseModel):
    candidate_level: int = Field(..., ge=0, le=5, description="Candidate's highest education level")
    required_level: int = Field(..., ge=0, le=5, description="Minimum required education level for the job")
    education_score: int = Field(..., ge=0, le=100, description="Education match score (0–100)")
    meets_requirement: bool = Field(..., description="Whether candidate meets or exceeds required level")

class ATSScore(BaseModel):
    format_score: int = Field(description="Score for resume format")
    keyword_score: int = Field(description="Score for keyword match")
    skills_score: int = Field(description="Score for skills match")
    experience_score: int = Field(description="Score for experience match")
    education_score: int = Field(description="Score for education match")
    overall_score: int = Field(description="Overall score based on all analyses")
    # decision: str = Field(description="Final decision based on the overall score: pass, review, or reject")
    # feedback: List[str] = Field(description="Feedback for the candidate based on the analysis")

class ATSState(TypedDict):
    resume: str
    job_description: str
    format_analysis: ATSFormatAnalysis
    keyword_analysis: ATSKeywordAnalysis
    skills_analysis: ATSSkillAnalysis
    experience_analysis: ATSExperienceAnalysis
    education_analysis: ATSEducationAnalysis
    final_score: ATSScore
    decision: str
    feedback: str
