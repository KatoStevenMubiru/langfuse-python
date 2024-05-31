# unify.py
# Main script that uses the various modules to perform operations with Langfuse.
import importlib
import sys
from typing import Optional
# del sys.modules['openai']
# sys.modules['openai'] = __import__('langfuse.openai', fromlist=[None]).openai
from langfuse.utils.langfuse_singleton import LangfuseSingleton

if importlib.util.find_spec('langfuse.openai') is not None:
    openai = __import__('langfuse.openai', fromlist=[None]).openai
    sys.modules['openai']

import unify
from langfuse import Langfuse
from langfuse.openai import wrap_function_wrapper, _wrap, _wrap_async

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
        module="unify.clients",
        object="Unify",
        method="generate",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.clients",
        object="AsyncUnify",
        method="generate",
        sync=False,
    ),
    UnifyDefinition(
        module="unify.clients",
        object="Unify",
        method="set_model",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.clients",
        object="AsyncUnify",
        method="set_model",
        sync=False,
    ),
    UnifyDefinition(
        module="unify.clients",
        object="Unify",
        method="set_provider",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.clients",
        object="AsyncUnify",
        method="set_provider",
        sync=False,
    ),
]

class UnifyLangfuse:
    _langfuse: Optional[Langfuse] = None

    def initialize(self):
        self._langfuse = LangfuseSingleton().get(
            public_key=unify.langfuse_public_key,
            secret_key=unify.langfuse_secret_key,
            host=unify.langfuse_host,
            debug=unify.langfuse_debug,
            enabled=unify.langfuse_enabled,
            sdk_integration="unify",
        )

        return self._langfuse

    def flush(cls):
        cls._langfuse.flush()

    def register_tracing(self):
        resources = UNIFY_METHODS_V0

        for resource in resources:
            wrap_function_wrapper(
                resource.module,
                f"{resource.object}.{resource.method}",
                _wrap(resource, self.initialize)
                if resource.sync
                else _wrap_async(resource, self.initialize),
            )

        setattr(unify, "langfuse_public_key", None)
        setattr(unify, "langfuse_secret_key", None)
        setattr(unify, "langfuse_host", None)
        setattr(unify, "langfuse_debug", None)
        setattr(unify, "langfuse_enabled", True)
        setattr(unify, "flush_langfuse", self.flush)


modifier = UnifyLangfuse()
modifier.register_tracing()