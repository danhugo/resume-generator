from typing import Literal, Dict, Any, Union
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel, _ConfigurableModel
from langchain_google_genai import ChatGoogleGenerativeAI
from resume_generator.utils import load_yaml_config
from pathlib import Path

# Define available LLM types
LLMType = Literal[
    "gemini-2.5-flash", 
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro"
    ]

AGENT_LLM_MAP: dict[str, LLMType] = {
    # CLINICAL ANALYSIS & TRIAGE (High complexity - medical decision making)
    "clarifier": "gemini-2.5-flash",  # Clinical triage & PICO analysis requires sophisticated medical reasoning
    
    # RESEARCH PLANNING (High complexity - strategic thinking)
    "decomposer": "gemini-2.5-flash",  # Clinical question decomposition requires deep medical knowledge
    "critiquer": "gemini-2.5-flash",   # Research quality assessment needs rigorous analytical thinking
    
    # SEARCH & RETRIEVAL (Medium complexity - structured tasks)
    "query_parser": "gemini-2.5-flash",  # Search query generation is structured but needs clinical context
    
    # INFORMATION PROCESSING (Medium-High complexity - evidence synthesis)
    "question_info_aggregator": "gemini-2.5-flash",  # Evidence synthesis with clinical assessment
    "reasoner": "gemini-2.5-flash",  # Clinical reasoning from first principles requires advanced thinking
    
    # REPORT GENERATION & REVIEW (Highest complexity - clinical communication)
    "report_composer": "gemini-2.5-flash",  # Clinical report writing requires sophisticated medical communication
    "report_reviewer": "gemini-2.5-flash",  # Clinical review requires expert-level medical judgment
}

# Cache for LLM instances
_llm_cache: dict[LLMType, Union[BaseChatModel, _ConfigurableModel]] = {}

def _create_llm_use_conf(llm_type: LLMType, conf: Dict[str, Any]) -> Union[BaseChatModel, _ConfigurableModel]:
    llm_type_map = {
        "gemini-2.5-flash": conf.get("GEMINI-2.5-FLASH"),
        "gemini-2.5-flash-lite": conf.get("GEMINI-2.5-FLASH-LITE"),
        "gemini-2.5-pro": conf.get("GEMINI-2.5-PRO"),
    }
    llm_conf = llm_type_map.get(llm_type)
    if not llm_conf:
        raise ValueError(f"Unknown LLM type: {llm_type}")
    if not isinstance(llm_conf, dict):
        raise ValueError(f"Invalid LLM Conf: {llm_type}")
    return init_chat_model(**llm_conf)

def get_llm_by_type(llm_type: LLMType) -> Union[BaseChatModel, _ConfigurableModel]:
    """
    Get LLM instance by type. Returns cached instance if available.
    """
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]

    conf = load_yaml_config(
        str((Path(__file__).parent / "conf.yaml").resolve())
    )

    llm = _create_llm_use_conf(llm_type, conf)
    _llm_cache[llm_type] = llm
    return llm