from typing import TypedDict, Dict, Any, List, Annotated, Literal
from pydantic import BaseModel, Field, conint
from enum import Enum

class ATSDecision(Enum):
    PASS = "PASS"
    REJECT = "REJECT"
    REVIEW = "REVIEW"

class ATSFormatAnalysis(BaseModel):
    format_score: int = Field(description="Percentage of format score from 0 to 100")
    analysis: str = Field(description='Format issues or validation points, e.g. No skills section, Missing dates in experience')

class ATSKeywordAnalysis(BaseModel):
    job_keywords: List[str] = Field(..., description="Exact keywords from job description")
    resume_keywords: List[str] = Field(..., description="Exact keywords from resume")
    match_score: Annotated[int, Field(..., strict=True, ge=0, le=100, description="Match score (0–100)")]

class ATSSkillAnalysis(BaseModel):
    required_skills: List[str] = Field(..., description="Skills extracted as required from the job description")
    preferred_skills: List[str] = Field(..., description="Skills extracted as preferred from the job description")
    candidate_skills: List[str] = Field(..., description="Skills extracted from the candidate's resume")
    required_score: Annotated[int, Field(..., strict=True, ge=0, le=100, description="Percentage of required skills matched")]
    preferred_score: Annotated[int, Field(..., strict=True, ge=0, le=100, description="Percentage of preferred skills matched")]
    
class ATSExperienceAnalysis(BaseModel):
    experience_quality: Literal["high", "medium", "low"] = Field(..., description="Overall quality of the candidate's experience")
    experience_score: Annotated[int, Field(..., strict=True, ge=0, le=100, description="Percentage of experience score")]
    analysis: str = Field(..., description="Explanation of the experience quality assessment")

class ATSEducationAnalysis(BaseModel):
    candidate_level: Literal[1, 2, 3, 4, 5] = Field(..., description="Candidate's highest education level (1: high school, 5: PhD)")
    required_level: Literal[1, 2, 3, 4, 5] = Field(..., description="Minimum required education level for the job")
    education_score: int = Field(..., ge=0, le=100, description="Education match score (0–100)")
    meets_requirement: bool = Field(..., description="Whether candidate meets or exceeds required level")

class ATSScore(BaseModel):
    format_score: float = Field(description="Score for resume format")
    keyword_score: float = Field(description="Score for keyword match")
    skills_score: float = Field(description="Score for skills match")
    experience_score: float = Field(description="Score for experience match")
    education_score: float = Field(description="Score for education match")
    overall_score: float = Field(description="Overall score based on all analyses")
    decision: ATSDecision = Field(description="Final decision based on the overall score")
    feedback: List[str] = Field(description="Feedback for the candidate based on the analysis")

class ATSState(TypedDict):
    raw_resume: str
    job_description: str
    format_analysis: ATSFormatAnalysis
    keyword_analysis: ATSKeywordAnalysis
    skills_analysis: ATSSkillAnalysis
    experience_analysis: ATSExperienceAnalysis
    education_analysis: ATSEducationAnalysis
    final_score: ATSScore
    decision: str
