import json
import logging
from enum import Enum
from typing import Any, Dict, Optional, Type

from pydantic import create_model

from app.models.tools import (
    AgentInput,
    AlgoliaInput,
    BingSearchInput,
    BrowserInput,
    ChatGPTInput,
    CodeInterpreterInput,
    # E2BCodeExecutorInput,
    FunctionInput,
    GPTVisionInput,
    HandOffInput,
    HTTPInput,
    MetaphorSearchInput,
    OpenapiInput,
    PubMedInput,
    ReplicateInput,
    TTS1Input,
    WolframInput,
    ZapierInput,
)
from app.tools.agent import Agent
from app.tools.algolia import Algolia
from app.tools.bing_search import BingSearch, LCBingSearch
from app.tools.browser import Browser, LCBrowser
from app.tools.chatgpt import get_chatpgt_tool
from app.tools.code_interpreter import CodeInterpreter

# from app.tools.e2b import E2BCodeExecutor
from app.tools.function import Function
from app.tools.gpt_vision import GPTVision
from app.tools.hand_off import HandOff
from app.tools.http import LCHttpTool
from app.tools.metaphor import MetaphorSearch
from app.tools.openapi import Openapi
from app.tools.pubmed import PubMed
from app.tools.replicate import Replicate
from app.tools.tts_1 import TTS1
from app.tools.wolfram_alpha import WolframAlpha
from app.tools.zapier import ZapierNLA

TOOL_TYPE_MAPPING = {
    "AGENT": {"class": Agent, "schema": AgentInput},
    "ALGOLIA": {"class": Algolia, "schema": AlgoliaInput},
    "BING_SEARCH": {
        "class": LCBingSearch,
        "schema": BingSearchInput,
    },
    "METAPHOR": {
        "class": MetaphorSearch,
        "schema": MetaphorSearchInput,
    },
    "PUBMED": {
        "class": PubMed,
        "schema": PubMedInput,
    },
    "ZAPIER_NLA": {"class": ZapierNLA, "schema": ZapierInput},
    "OPENAPI": {"class": Openapi, "schema": OpenapiInput},
    "CHATGPT_PLUGIN": {"class": get_chatpgt_tool, "schema": ChatGPTInput},
    "REPLICATE": {"class": Replicate, "schema": ReplicateInput},
    "WOLFRAM_ALPHA": {"class": WolframAlpha, "schema": WolframInput},
    # "CODE_EXECUTOR": {"class": E2BCodeExecutor, "schema": E2BCodeExecutorInput},
    "CODE_EXECUTOR": {"class": CodeInterpreter, "schema": CodeInterpreterInput},
    "BROWSER": {"class": LCBrowser, "schema": BrowserInput},
    "GPT_VISION": {"class": GPTVision, "schema": GPTVisionInput},
    "TTS_1": {"class": TTS1, "schema": TTS1Input},
    "HAND_OFF": {"class": HandOff, "schema": HandOffInput},
    "FUNCTION": {"class": Function, "schema": FunctionInput},
    "HTTP": {"class": LCHttpTool, "schema": HTTPInput},
}

OSS_TOOL_TYPE_MAPPING = {"BROWSER": Browser, "BING_SEARCH": BingSearch}


def create_pydantic_model_from_object(obj: Dict[str, Any]) -> Any:
    fields = {}
    type_mapping = {
        "string": str,
        "integer": int,
        "boolean": bool,
    }
    for key, value in obj.items():
        if isinstance(value, dict):
            type = value.get("type")
            if not type:
                logging.warning(f"Type not found for {key}, defaulting to string")
            if "enum" in value:
                enum_values = value["enum"]
                enum_name = f"{key.capitalize()}Enum"
                field_type = Enum(enum_name, enum_values)
            else:
                field_type = type_mapping.get(type, str)
        else:
            field_type = type_mapping.get(value, str)

        fields[key] = (field_type, ...)
    return create_model("DynamicModel", **fields)


def create_tool(
    tool_class: Type[Any],
    name: str,
    description: str,
    args_schema: Any,
    metadata: Optional[Dict[str, Any]],
    return_direct: Optional[bool],
    session_id: str = None,
) -> Any:
    if metadata:
        metadata = json.loads(metadata)
        metadata["sessionId"] = session_id
    return tool_class(
        name=name,
        description=description,
        args_schema=args_schema,
        metadata=metadata,
        return_direct=return_direct,
    )
