import copy
import logging
import types
from typing import List, Optional

from packaging.version import Version
from wrapt import wrap_function_wrapper

from langfuse import Langfuse
from langfuse.client import StatefulGenerationClient
from langfuse.decorators import langfuse_context
from langfuse.utils import _get_timestamp
from langfuse.utils.langfuse_singleton import LangfuseSingleton

class UnifyDefinition:
    model: Optional[str]
    provider: Optional[str]
    module: str
    object: str
    method: str
    type: str
    sync: bool

    def __init__(self, module: str, object: str, method: str, sync: bool, model: Optional[str] = None, provider: Optional[str] = None):
        self.module = module
        self.object = object
        self.method = method
        self.sync = sync
        self.model = model
        self.provider = provider

# Has yet to be added: model@provider setting and taking it into account in tracing. 
# It has to be added in UNIFY_METHODS_V0, methods: "set_model", "set_provider".

UNIFY_METHODS_V0 = [
    UnifyDefinition(
        module="unify.chat", # modules are required for tracing
        object="ChatBot", # object is required for tracing
        method="run", # methods are required for tracing
        sync=True,
    ),
    UnifyDefinition(
        module="unify.chat",
        object="ChatBot",
        method="set_model",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.chat",
        object="ChatBot",
        method="set_provider",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.client",
        object="Unify",
        method="generate",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.client",
        object="AsyncUnify",
        method="generate",
        sync=False,
    ),
    UnifyDefinition(
        module="unify.client",
        object="Unify",
        method="set_model",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.client",
        object="AsyncUnify",
        method="set_model",
        sync=False,
    ),
    UnifyDefinition(
        module="unify.client",
        object="Unify",
        method="set_provider",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.client",
        object="AsyncUnify",
        method="set_provider",
        sync=False,
    ),
]