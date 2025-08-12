"""ATS Scanner Module
This module implements an ATS (Applicant Tracking System) scanner that processes resumes and LinkedIn profiles.
"""

import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, Interrupt

from resume_generator.configuration import Configuration

from resume_generator.states.ats_scanner_states import (
    ATSState,
    ATSScore,
    ATSKeywordAnalysis,
    ATSFormatAnalysis,
    ATSSkillAnalysis,
    ATSExperienceAnalysis,
    ATSEducationAnalysis
)
from resume_generator.prompts.ats_scanner_prompts import (
    FORMAT_ANALYSIS_PROMPT,
    SKILLS_ANALYSIS_PROMPT,
    KEYWORD_ANALYSIS_PROMPT,
    EDUCATION_ANALYSIS_PROMPT,
    EXPERIENCE_ANALYSIS_PROMPT,
    FEEDBACK_GENERATION_PROMPT,
)

from resume_generator.logger import init_logger
from resume_generator.llms import get_llm_by_type, AGENT_LLM_MAP

logger = init_logger(__name__)

class ATSScanner:
    def __init__(self):
        self.llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"])
    def build_graph(self) -> StateGraph:
        workflow = StateGraph(ATSState)

        # Add nodes
        workflow.add_node("analyze_format", self._analyze_format)
        workflow.add_node("analyze_keywords", self._analyze_keywords)
        workflow.add_node("analyze_skills", self._analyze_skills)
        workflow.add_node("analyze_experience", self._analyze_experience)
        workflow.add_node("analyze_education", self._analyze_education)
        workflow.add_node("calculate_score", self._calculate_score)
        workflow.add_node("make_decision", self._make_decision)

        # Define the flow
        workflow.add_edge(START, "analyze_format")
        workflow.add_edge(START, "analyze_keywords")
        workflow.add_edge(START, "analyze_skills")
        workflow.add_edge(START, "analyze_experience")
        workflow.add_edge(START, "analyze_education")

        workflow.add_edge("analyze_format", "calculate_score")
        workflow.add_edge("analyze_keywords", "calculate_score")
        workflow.add_edge("analyze_skills", "calculate_score")
        workflow.add_edge("analyze_experience", "calculate_score")
        workflow.add_edge("analyze_education", "calculate_score")
        
        workflow.add_edge("calculate_score", "make_decision")
        workflow.add_edge("make_decision", END)
        
        return workflow.compile()
    
    async def _analyze_format(self, state: ATSState):
        """Analyze resume format and ATS compatibility"""
        resume = state["resume"]
        llm = self.llm.with_structured_output(ATSFormatAnalysis)
        messages = [
            SystemMessage(content=FORMAT_ANALYSIS_PROMPT.format(resume=resume)),
            HumanMessage(content="Please evaluate the format of this resume for ATS compatibility.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "format_analysis": response
        }
    
    async def _analyze_keywords(self, state: ATSState):
        """Analyze keyword matching"""
        resume = state["resume"]
        job_description = state["job_description"]
        
        llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"]).with_structured_output(ATSKeywordAnalysis)
        messages = [
            SystemMessage(content=KEYWORD_ANALYSIS_PROMPT.format(job_description=job_description, resume=resume)),
            HumanMessage(content="Compare the resume against the job description and return keyword match scores and missed keywords.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "keyword_analysis": response
        }
    
    async def _analyze_skills(self, state: ATSState) -> ATSState:
        """Analyze skills matching"""
        resume = state["resume"]
        job_description = state["job_description"]
        
        llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"]).with_structured_output(ATSSkillAnalysis)
        messages = [
            SystemMessage(content=SKILLS_ANALYSIS_PROMPT.format(job_description=job_description, resume=resume)),
            HumanMessage(content="Assess required and preferred skill matches between the resume and job description.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "skills_analysis": response
        }
    
    async def _analyze_experience(self, state: ATSState):
        """Analyze experience requirements"""
        resume = state["resume"]
        job_description = state["job_description"]
        
        llm = self.llm.with_structured_output(ATSExperienceAnalysis)
        messages = [
            SystemMessage(content=EXPERIENCE_ANALYSIS_PROMPT.format(job_description=job_description, resume=resume)),
            HumanMessage(content="Check whether the candidate's experience matches the job's years of experience requirements.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "experience_analysis": response
        }
    
    async def _analyze_education(self, state: ATSState) -> ATSState:
        """Analyze education requirements"""
        resume = state["resume"]
        job_description = state["job_description"]
        
        llm = self.llm.with_structured_output(ATSEducationAnalysis)
        messages = [
            SystemMessage(content=EDUCATION_ANALYSIS_PROMPT.format(job_description=job_description, resume=resume)),
            HumanMessage(content="Evaluate if the candidate meets the job's education requirements.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "education_analysis": response
        }
    
    async def _calculate_score(self, state: ATSState) -> ATSState:
        """Calculate final ATS score"""
        format_analysis = state["format_analysis"]
        keyword_analysis = state["keyword_analysis"]
        skills_analysis = state["skills_analysis"]
        experience_analysis = state["experience_analysis"]
        education_analysis = state["education_analysis"]
        
        # Weighted scoring (real ATS systems use similar weights)
        weights = {
            "keywords": 0.25,    # 25% - Keyword matching is crucial
            "skills": 0.30,      # 30% - Skills matching is most important
            "experience": 0.25,  # 25% - Experience is critical
            "education": 0.10,   # 10% - Education is less weighted
            "format": 0.10       # 10% - Format/ATS compatibility
        }
        
        format_score = format_analysis.format_score
        keyword_score = keyword_analysis.match_score
        skills_score = int(skills_analysis.required_score * 0.8 + skills_analysis.preferred_score * 0.2)
        experience_score = experience_analysis.experience_score
        education_score = education_analysis.education_score
        
        overall_score = int(
            keyword_score * weights["keywords"] +
            skills_score * weights["skills"] +
            experience_score * weights["experience"] +
            education_score * weights["education"] +
            format_score * weights["format"]
        )


        attsscore = ATSScore(
            format_score=format_score,
            keyword_score=keyword_score,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score,
            overall_score=overall_score
        )
        
        return {
            "final_score": attsscore
        }  
    
    async def _make_decision(self, state: ATSState) -> ATSState:
        """Make final ATS decision"""
        final_score = state["final_score"]
        overall_score = final_score.overall_score
        
        # Decision thresholds (typical ATS thresholds)
        if overall_score >= 75:
            decision = 'pass'
        elif overall_score >= 50:
            decision = 'review'
        else:
            decision = 'reject'
        
        # Generate feedback
        keyword_analysis = state["keyword_analysis"]
        skills_analysis = state["skills_analysis"]
        experience_analysis = state["experience_analysis"]
        education_analysis = state["education_analysis"]
        format_analysis = state["format_analysis"]
        
        # Construct feedback input data
        feedback_input = {
            "keyword_analysis": keyword_analysis.model_dump_json(),
            "skills_analysis": skills_analysis.model_dump_json(),
            "experience_analysis": experience_analysis.model_dump_json(),
            "education_analysis": education_analysis.model_dump_json(),
            "format_analysis": format_analysis.model_dump_json(),
        }

        # Initialize LLM
        job_description = state["job_description"]
        resume = state["resume"]

        llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"])
        
        messages = [
            SystemMessage(content=FEEDBACK_GENERATION_PROMPT.format(job_description=job_description, resume=resume)),
            HumanMessage(content=f"With decision: {decision} and overall score {final_score}, please generate feedback based on the following analysis:\n{json.dumps(feedback_input, indent=2)}")
        ]
        
        response = await llm.ainvoke(messages)

        return {
            "decision": decision,
            "feedback": response,
        }  
    
ats_scanner = ATSScanner()
graph = ats_scanner.build_graph()
