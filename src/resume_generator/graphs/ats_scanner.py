"""ATS Scanner Module
This module implements an ATS (Applicant Tracking System) scanner that processes resumes and LinkedIn profiles.
"""

import json
from typing import Any, Dict, List, Literal, Optional, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from resume_generator import prompts
from resume_generator.configuration import Configuration
from resume_generator.tools import scrape_website, search
from resume_generator.utils import init_model
import re
from resume_generator.states.ats_scanner import ATSState, ScanType, ATSDecision, ATSScore, ATSKeywordAnalysis
from resume_generator.prompts.ats_scanner import (
    keyword_analysis_prompt,
    skills_analysis_prompt,
    experience_quality_prompt,
    education_score_prompt,
    resume_format_prompt
)

from resume_generator.logger import init_logger
from resume_generator.llms import get_llm_by_type, AGENT_LLM_MAP

logger = init_logger(__name__)

class ATSScanner:
    def build_graph(self) -> StateGraph:
        workflow = StateGraph(ATSState)

        # Add nodes
        workflow.add_node("extract_data", self._extract_data)
        workflow.add_node("analyze_keywords", self._analyze_keywords)
        workflow.add_node("analyze_skills", self._analyze_skills)
        workflow.add_node("analyze_experience", self._analyze_experience)
        workflow.add_node("analyze_education", self._analyze_education)
        workflow.add_node("analyze_format", self._analyze_format)
        workflow.add_node("calculate_score", self._calculate_score)
        workflow.add_node("make_decision", self._make_decision)

        # Define the flow
        workflow.set_entry_point("extract_data")
        workflow.add_edge("extract_data", "analyze_keywords")
        workflow.add_edge("extract_data", "analyze_skills")
        workflow.add_edge("extract_data", "analyze_experience")
        workflow.add_edge("extract_data", "analyze_education")
        workflow.add_edge("extract_data", "analyze_format")

        workflow.add_edge("analyze_keywords", "calculate_score")
        workflow.add_edge("analyze_skills", "calculate_score")
        workflow.add_edge("analyze_experience", "calculate_score")
        workflow.add_edge("analyze_education", "calculate_score")
        workflow.add_edge("analyze_format", "calculate_score")
        
        workflow.add_edge("calculate_score", "make_decision")
        workflow.add_edge("make_decision", END)
        
        return workflow.compile()
    
    async def _analyze_keywords(self, state: ATSState):
        """Analyze keyword matching"""
        raw_resume = state["raw_resume"]
        job_description = state["job_description"]
        
        llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"]).with_structured_output(ATSKeywordAnalysis)
        messages = [
            SystemMessage(content=keyword_analysis_prompt.format(job_description=job_description, raw_resume=raw_resume)),
            HumanMessage(content="Extract the structured resume information from the provided resume.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "keyword_analysis": response
        }
    
    async def _analyze_skills(self, state: ATSState) -> ATSState:
        """Analyze skills matching"""
        raw_resume = state["raw_resume"]
        job_description = state["job_description"]
        
        llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"]).with_structured_output(ATSKeywordAnalysis)
        messages = [
            SystemMessage(content=skills_analysis_prompt.format(job_description=job_description, raw_resume=raw_resume)),
            HumanMessage(content="Extract the structured resume information from the provided resume.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "skills_analysis": response
        }
    
    async def _analyze_experience(self, state: ATSState):
        """Analyze experience requirements"""
        raw_resume = state["raw_resume"]
        job_description = state["job_description"]
        
        llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"]).with_structured_output(ATSKeywordAnalysis)
        messages = [
            SystemMessage(content=experience_quality_prompt.format(job_description=job_description, raw_resume=raw_resume)),
            HumanMessage(content="Extract the structured resume information from the provided resume.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "skills_analysis": response
        }
    
    async def _analyze_education(self, state: ATSState) -> ATSState:
        """Analyze education requirements"""
        raw_resume = state["raw_resume"]
        job_description = state["job_description"]
        
        llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"]).with_structured_output(ATSKeywordAnalysis)
        messages = [
            SystemMessage(content=experience_quality_prompt.format(job_description=job_description, raw_resume=raw_resume)),
            HumanMessage(content="Extract the structured resume information from the provided resume.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "skills_analysis": response
        }
    
    async def _analyze_format(self, state: ATSState) -> ATSState:
        """Analyze resume format and ATS compatibility"""
        raw_resume = state["raw_resume"]
        job_description = state["job_description"]
        
        llm = get_llm_by_type(AGENT_LLM_MAP["ats_analyst"]).with_structured_output(ATSKeywordAnalysis)
        messages = [
            SystemMessage(content=experience_quality_prompt.format(job_description=job_description, raw_resume=raw_resume)),
            HumanMessage(content="Extract the structured resume information from the provided resume.")
        ]
        response = await llm.ainvoke(messages)
        return {
            "skills_analysis": response
        }
    
    async def _calculate_score(self, state: ATSState) -> ATSState:
        """Calculate final ATS score"""
        keyword_analysis = state["keyword_analysis"]
        skills_analysis = state["skills_analysis"]
        experience_analysis = state["experience_analysis"]
        education_analysis = state["education_analysis"]
        format_analysis = state["format_analysis"]
        
        # Weighted scoring (real ATS systems use similar weights)
        weights = {
            "keywords": 0.25,    # 25% - Keyword matching is crucial
            "skills": 0.30,      # 30% - Skills matching is most important
            "experience": 0.25,  # 25% - Experience is critical
            "education": 0.10,   # 10% - Education is less weighted
            "format": 0.10       # 10% - Format/ATS compatibility
        }
        
        keyword_score = keyword_analysis["match_score"]
        skills_score = (skills_analysis["required_score"] * 0.8 + skills_analysis["preferred_score"] * 0.2)
        experience_score = experience_analysis["experience_score"]
        education_score = education_analysis["education_score"]
        format_score = format_analysis["format_score"]
        
        overall_score = (
            keyword_score * weights["keywords"] +
            skills_score * weights["skills"] +
            experience_score * weights["experience"] +
            education_score * weights["education"] +
            format_score * weights["format"]
        )
        
        state["final_score"] = {
            "keyword_score": keyword_score,
            "skills_score": skills_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "format_score": format_score,
            "overall_score": overall_score,
            "weights": weights
        }
        
        return state
    
    async def _make_decision(self, state: ATSState) -> ATSState:
        """Make final ATS decision"""
        final_score = state["final_score"]
        overall_score = final_score["overall_score"]
        
        # Decision thresholds (typical ATS thresholds)
        if overall_score >= 75:
            decision = ATSDecision.PASS.value
        elif overall_score >= 50:
            decision = ATSDecision.REVIEW.value
        else:
            decision = ATSDecision.REJECT.value
        
        # Generate feedback
        feedback = self._generate_feedback(state)
        
        state["decision"] = decision
        state["feedback"] = feedback
        
        return state

    def _generate_feedback(self, state: ATSState) -> List[str]:
        """Generate detailed feedback for the candidate"""
        feedback = []
        
        keyword_analysis = state["keyword_analysis"]
        skills_analysis = state["skills_analysis"]
        experience_analysis = state["experience_analysis"]
        education_analysis = state["education_analysis"]
        format_analysis = state["format_analysis"]
        
        # Keyword feedback
        if keyword_analysis["match_score"] < 70:
            missing = keyword_analysis["missed_keywords"][:3]  # Top 3 missing
            feedback.append(f"Missing important keywords: {', '.join(missing)}")
        
        # Skills feedback
        if skills_analysis["missing_required"]:
            missing_skills = skills_analysis["missing_required"][:3]
            feedback.append(f"Missing required skills: {', '.join(missing_skills)}")
        
        # Experience feedback
        if not experience_analysis["meets_requirement"]:
            feedback.append(f"Insufficient experience: {experience_analysis['estimated_years']} years vs {experience_analysis['required_years']} required")
        
        # Education feedback
        if not education_analysis["meets_requirement"]:
            feedback.append(f"Education requirement not met: {education_analysis['required_education']} required")
        
        # Format feedback
        if format_analysis["format_issues"]:
            feedback.extend([f"Format issue: {issue}" for issue in format_analysis["format_issues"][:2]])
        
        # Positive feedback
        if keyword_analysis["match_score"] >= 80:
            feedback.append("Strong keyword optimization")
        
        if skills_analysis["required_score"] >= 80:
            feedback.append("Excellent skills match")
        
        return feedback
    
ats_scanner = ATSScanner()
graph = ats_scanner.build_graph()