from typing import TypedDict, Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ProfileAnalysis(BaseModel):
    """Analysis of candidate's profile"""
    strengths: List[str] = Field(..., description="Key strengths identified from the profile")
    relevant_experience: List[str] = Field(..., description="Experience relevant to the target job")
    skill_gaps: List[str] = Field(..., description="Skills that may need to be highlighted or acquired")
    unique_value_props: List[str] = Field(..., description="Unique value propositions of the candidate")


class JobAnalysis(BaseModel):
    """Analysis of job description"""
    required_skills: List[str] = Field(..., description="Required skills from job description")
    preferred_skills: List[str] = Field(..., description="Preferred skills from job description")
    key_responsibilities: List[str] = Field(..., description="Key responsibilities of the role")
    company_culture_hints: List[str] = Field(..., description="Hints about company culture and values")
    keywords: List[str] = Field(..., description="Important keywords for ATS optimization")


class MatchMatrix(BaseModel):
    """Matching matrix between profile and job"""
    skill_matches: Dict[str, bool] = Field(..., description="Mapping of required skills to candidate match")
    experience_relevance_score: int = Field(..., ge=0, le=100, description="How relevant is candidate's experience")
    education_match_score: int = Field(..., ge=0, le=100, description="How well education matches requirements")
    overall_fit_score: int = Field(..., ge=0, le=100, description="Overall fit percentage")
    recommendations: List[str] = Field(..., description="Recommendations for resume optimization")


class ResumeSection(BaseModel):
    """Individual resume section"""
    section_name: str = Field(..., description="Name of the section (e.g., Experience, Skills)")
    content: str = Field(..., description="Content of the section")
    keywords_used: List[str] = Field(..., description="Keywords incorporated in this section")


class ResumeEvaluation(BaseModel):
    """Evaluation of generated resume"""
    keyword_coverage: int = Field(..., ge=0, le=100, description="Percentage of keywords covered")
    ats_friendliness: int = Field(..., ge=0, le=100, description="ATS compatibility score")
    clarity_score: int = Field(..., ge=0, le=100, description="Clarity and readability score")
    achievement_focus: int = Field(..., ge=0, le=100, description="Focus on measurable achievements")
    overall_quality: int = Field(..., ge=0, le=100, description="Overall resume quality score")
    improvement_suggestions: List[str] = Field(..., description="Specific suggestions for improvement")


class ResumeFeedback(BaseModel):
    """Feedback for resume revision"""
    strengths: List[str] = Field(..., description="Strong points of the current resume")
    weaknesses: List[str] = Field(..., description="Areas needing improvement")
    specific_revisions: List[str] = Field(..., description="Specific revision recommendations")
    priority_changes: List[str] = Field(..., description="High-priority changes to make")


class ResumeGeneratorState(TypedDict):
    """Main state for resume generator graph"""
    # Inputs
    candidate_profile: Dict[str, Any]
    job_description: str
    
    # Analysis results
    profile_analysis: Optional[ProfileAnalysis]
    job_analysis: Optional[JobAnalysis]
    match_matrix: Optional[MatchMatrix]
    
    # Resume generation
    resume_sections: Optional[List[ResumeSection]]
    full_resume: Optional[str]
    
    # Evaluation and feedback
    resume_evaluation: Optional[ResumeEvaluation]
    feedback: Optional[ResumeFeedback]
    
    # Control flow
    iteration_count: int
    max_iterations: int
    quality_threshold: int
    should_continue: bool
    human_feedback: Optional[str]