"""Define a data enrichment agent.

Works with a chat model with tool calling support.
"""

import json
from typing import Any, Dict, List, Literal, Optional, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from resume_generator import prompts
from resume_generator.configuration import Configuration
from resume_generator.state import InputState, OutputState, State
from resume_generator.tools import scrape_website, search
from resume_generator.utils import init_model




# Create the graph
workflow = StateGraph(
    State, input_schema=InputState, output_schema=OutputState
)

workflow.add_node(profile_analyzer)
workflow.add_node(job_description_parser)
workflow.add_node(match_profile_to_jd)
workflow.add_node(resume_generator)
workflow.add_node(call_agent_model)
workflow.add_node(reflect)
workflow.add_node(evaluation_node)
workflow.add_edge("__start__", "call_agent_model")
workflow.add_conditional_edges("call_agent_model", route_after_agent)
workflow.add_edge("tools", "call_agent_model")
workflow.add_conditional_edges("reflect", route_after_checker)

graph = workflow.compile()
graph.name = "ResearchTopic"
