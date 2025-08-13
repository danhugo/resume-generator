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
    "ats_analyst": "gemini-2.5-flash",
    "resume_generator": "gemini-2.5-flash",

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
        str((Path(__file__).parent / "llm_config.yaml").resolve())
    )

    llm = _create_llm_use_conf(llm_type, conf)
    _llm_cache[llm_type] = llm
    return llm