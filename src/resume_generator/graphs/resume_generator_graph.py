"""Resume Generator Module
This module implements an intelligent resume generator that tailors resumes to specific job descriptions.
"""

import json
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, Interrupt

from resume_generator.configuration import Configuration
from resume_generator.states.resume_generator_states import (
    ResumeGeneratorState,
    ProfileAnalysis,
    JobAnalysis,
    MatchMatrix,
    ResumeSection,
    ResumeEvaluation,
    ResumeFeedback
)
from resume_generator.prompts.resume_generator_prompts import (
    PROFILE_ANALYSIS_PROMPT,
    JOB_ANALYSIS_PROMPT,
    MATCH_MATRIX_PROMPT,
    RESUME_GENERATION_PROMPT,
    RESUME_EVALUATION_PROMPT,
    FEEDBACK_GENERATION_PROMPT,
    RESUME_REVISION_PROMPT,
    FINAL_FORMAT_PROMPT
)
from resume_generator.logger import init_logger
from resume_generator.llms import get_llm_by_type, AGENT_LLM_MAP

logger = init_logger(__name__)


class ResumeGenerator:
    def __init__(self):
        self.llm = get_llm_by_type(AGENT_LLM_MAP.get("resume_generator"))
        
    def build_graph(self) -> StateGraph:
        workflow = StateGraph(ResumeGeneratorState)
        
        # Add nodes
        workflow.add_node("analyze_profile", self._analyze_profile)
        workflow.add_node("analyze_job", self._analyze_job)
        workflow.add_node("build_match_matrix", self._build_match_matrix)
        workflow.add_node("generate_resume", self._generate_resume)
        workflow.add_node("evaluate_resume", self._evaluate_resume)
        workflow.add_node("generate_feedback", self._generate_feedback)
        workflow.add_node("revise_resume", self._revise_resume)
        workflow.add_node("check_quality", self._check_quality)
        workflow.add_node("format_final", self._format_final)
        
        # Define the flow
        workflow.add_edge(START, "analyze_profile")
        workflow.add_edge(START, "analyze_job")
        
        workflow.add_edge("analyze_profile", "build_match_matrix")
        workflow.add_edge("analyze_job", "build_match_matrix")
        
        workflow.add_edge("build_match_matrix", "generate_resume")
        workflow.add_edge("generate_resume", "evaluate_resume")
        workflow.add_edge("evaluate_resume", "check_quality")
        
        # Conditional edge from check_quality
        workflow.add_conditional_edges(
            "check_quality",
            self._should_continue,
            {
                "continue": "generate_feedback",
                "finish": "format_final"
            }
        )
        
        workflow.add_edge("generate_feedback", "revise_resume")
        workflow.add_edge("revise_resume", "evaluate_resume")
        workflow.add_edge("format_final", END)
        
        return workflow.compile()
    
    async def _analyze_profile(self, state: ResumeGeneratorState):
        """Analyze candidate profile to identify strengths and relevant experience"""
        candidate_profile = state["candidate_profile"]
        job_description = state["job_description"]
        
        llm = self.llm.with_structured_output(ProfileAnalysis)
        messages = [
            SystemMessage(content=PROFILE_ANALYSIS_PROMPT.format(
                candidate_profile=json.dumps(candidate_profile, indent=2),
                job_description=job_description
            )),
            HumanMessage(content="Analyze this candidate's profile for the target job.")
        ]
        response = await llm.ainvoke(messages)
        
        return {
            "profile_analysis": response
        }
    
    async def _analyze_job(self, state: ResumeGeneratorState):
        """Parse and analyze job description for requirements and keywords"""
        job_description = state["job_description"]
        
        llm = self.llm.with_structured_output(JobAnalysis)
        messages = [
            SystemMessage(content=JOB_ANALYSIS_PROMPT.format(
                job_description=job_description
            )),
            HumanMessage(content="Extract key requirements and keywords from this job description.")
        ]
        response = await llm.ainvoke(messages)
        
        return {
            "job_analysis": response
        }
    
    async def _build_match_matrix(self, state: ResumeGeneratorState):
        """Build matching matrix between profile and job requirements"""
        profile_analysis = state["profile_analysis"]
        job_analysis = state["job_analysis"]
        candidate_profile = state["candidate_profile"]
        
        llm = self.llm.with_structured_output(MatchMatrix)
        messages = [
            SystemMessage(content=MATCH_MATRIX_PROMPT.format(
                profile_analysis=profile_analysis.model_dump_json() if profile_analysis else "{}",
                job_analysis=job_analysis.model_dump_json() if job_analysis else "{}",
                candidate_profile=json.dumps(candidate_profile, indent=2)
            )),
            HumanMessage(content="Create a detailed matching matrix for resume optimization.")
        ]
        response = await llm.ainvoke(messages)
        
        return {
            "match_matrix": response
        }
    
    async def _generate_resume(self, state: ResumeGeneratorState):
        """Generate tailored resume based on analysis and matching"""
        candidate_profile = state["candidate_profile"]
        job_analysis = state["job_analysis"]
        match_matrix = state["match_matrix"]
        
        # If this is a revision, use the previous resume as base
        is_revision = state.get("iteration_count", 0) > 0
        
        if is_revision:
            feedback = state.get("feedback")
            human_feedback = state.get("human_feedback", "")
            current_resume = state.get("full_resume", "")
            
            llm = get_llm_by_type(AGENT_LLM_MAP.get("resume_generator", "gemini-2.0-flash-exp"))
            messages = [
                SystemMessage(content=RESUME_REVISION_PROMPT.format(
                    resume=current_resume,
                    feedback=feedback.model_dump_json() if feedback else "{}",
                    job_analysis=job_analysis.model_dump_json() if job_analysis else "{}",
                    human_feedback=human_feedback
                )),
                HumanMessage(content="Revise the resume based on the feedback provided.")
            ]
        else:
            llm = get_llm_by_type(AGENT_LLM_MAP.get("resume_generator", "gemini-2.0-flash-exp"))
            messages = [
                SystemMessage(content=RESUME_GENERATION_PROMPT.format(
                    candidate_profile=json.dumps(candidate_profile, indent=2),
                    job_analysis=job_analysis.model_dump_json() if job_analysis else "{}",
                    match_matrix=match_matrix.model_dump_json() if match_matrix else "{}",
                    keyword_percentage=80
                )),
                HumanMessage(content="Generate a tailored, ATS-friendly resume.")
            ]
        
        response = await llm.ainvoke(messages)
        
        # Parse resume into sections
        resume_text = response.content if hasattr(response, 'content') else str(response)
        sections = self._parse_resume_sections(resume_text)
        
        return {
            "full_resume": resume_text,
            "resume_sections": sections,
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    async def _evaluate_resume(self, state: ResumeGeneratorState):
        """Evaluate generated resume for quality and alignment"""
        resume = state["full_resume"]
        job_description = state["job_description"]
        job_analysis = state["job_analysis"]
        
        keywords = job_analysis.keywords if job_analysis else []
        
        llm = self.llm.with_structured_output(ResumeEvaluation)
        messages = [
            SystemMessage(content=RESUME_EVALUATION_PROMPT.format(
                resume=resume,
                job_description=job_description,
                keywords=", ".join(keywords)
            )),
            HumanMessage(content="Evaluate this resume against job requirements and best practices.")
        ]
        response = await llm.ainvoke(messages)
        
        return {
            "resume_evaluation": response
        }
    
    async def _generate_feedback(self, state: ResumeGeneratorState):
        """Generate specific feedback for resume improvement"""
        evaluation = state["resume_evaluation"]
        resume = state["full_resume"]
        job_analysis = state["job_analysis"]
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 3)
        
        llm = self.llm.with_structured_output(ResumeFeedback)
        messages = [
            SystemMessage(content=FEEDBACK_GENERATION_PROMPT.format(
                evaluation=evaluation.model_dump_json() if evaluation else "{}",
                resume=resume,
                job_analysis=job_analysis.model_dump_json() if job_analysis else "{}",
                iteration_count=iteration_count,
                max_iterations=max_iterations
            )),
            HumanMessage(content="Generate actionable feedback for resume improvement.")
        ]
        response = await llm.ainvoke(messages)
        
        return {
            "feedback": response
        }
    
    async def _revise_resume(self, state: ResumeGeneratorState):
        """Revise resume based on feedback"""
        # This redirects to _generate_resume with revision flag
        return await self._generate_resume(state)
    
    async def _check_quality(self, state: ResumeGeneratorState):
        """Check if resume meets quality threshold"""
        evaluation = state.get("resume_evaluation")
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 3)
        quality_threshold = state.get("quality_threshold", 80)
        
        # Calculate whether to continue
        if evaluation:
            overall_quality = evaluation.overall_quality
            should_continue = (
                overall_quality < quality_threshold and 
                iteration_count < max_iterations
            )
        else:
            should_continue = iteration_count < max_iterations
        
        return {
            "should_continue": should_continue
        }
    
    def _should_continue(self, state: ResumeGeneratorState) -> str:
        """Conditional function to determine next step"""
        should_continue = state.get("should_continue", False)
        return "continue" if should_continue else "finish"
    
    async def _format_final(self, state: ResumeGeneratorState):
        """Format final resume for export"""
        resume = state["full_resume"]
        format_type = state.get("export_format", "markdown")
        
        llm = get_llm_by_type(AGENT_LLM_MAP.get("resume_generator", "gemini-2.0-flash-exp"))
        messages = [
            SystemMessage(content=FINAL_FORMAT_PROMPT.format(
                resume=resume,
                format=format_type
            )),
            HumanMessage(content=f"Format this resume for {format_type} export.")
        ]
        response = await llm.ainvoke(messages)
        
        final_resume = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "full_resume": final_resume
        }
    
    def _parse_resume_sections(self, resume_text: str) -> List[ResumeSection]:
        """Parse resume text into structured sections"""
        sections = []
        current_section = None
        current_content = []
        
        # Common section headers
        section_headers = [
            "PROFESSIONAL SUMMARY", "SUMMARY", "OBJECTIVE",
            "EXPERIENCE", "PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE",
            "EDUCATION", "SKILLS", "TECHNICAL SKILLS", "CORE SKILLS",
            "CERTIFICATIONS", "PROJECTS", "ACHIEVEMENTS", "PUBLICATIONS"
        ]
        
        lines = resume_text.split('\n')
        for line in lines:
            line_upper = line.strip().upper()
            
            # Check if this line is a section header
            is_header = any(header in line_upper for header in section_headers)
            
            if is_header and current_section:
                # Save previous section
                sections.append(ResumeSection(
                    section_name=current_section,
                    content='\n'.join(current_content),
                    keywords_used=[]  # Could extract keywords here
                ))
                current_section = line.strip()
                current_content = []
            elif is_header:
                current_section = line.strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections.append(ResumeSection(
                section_name=current_section,
                content='\n'.join(current_content),
                keywords_used=[]
            ))
        
        return sections


# Create the graph instance
resume_generator = ResumeGenerator()
graph = resume_generator.build_graph()