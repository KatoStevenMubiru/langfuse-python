import importlib
import sys
import logging
from collections import OrderedDict
from wrapt import wrap_function_wrapper
from typing import Optional
from langfuse.utils.langfuse_singleton import LangfuseSingleton
from langfuse.decorators import langfuse_context, observe
from langfuse import Langfuse

from langfuse.openai import _wrap_async, _wrap, _langfuse_wrapper, _is_openai_v1


# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("langfuse.unify")

# Conditional import for langfuse.openai
if importlib.util.find_spec('langfuse.openai') is not None:
    openai = __import__('langfuse.openai', fromlist=[None]).openai
    sys.modules['openai']

import unify

class UnifyDefinition:
    model: Optional[str]
    provider: Optional[str]
    module: str
    object: str
    method: str
    type: str
    sync: bool
    type: str

    def __init__(self, module: str, object: str, method: str, sync: bool, model: Optional[str] = None, provider: Optional[str] = None, type: Optional[str] = None):
        self.module = module
        self.object = object
        self.method = method
        self.sync = sync
        self.model = model
        self.provider = provider
        self.type = type

UNIFY_METHODS_V0 = [
    UnifyDefinition(
        module="unify.chat",
        object="ChatBot",
        method="run",
        sync=True,
        type="chat",
    ),
    UnifyDefinition(
        module="unify.chat",
        object="ChatBot",
        method="set_endpoint",
        sync=True,
        type="chat",
    ),
    UnifyDefinition(
        module="unify.clients",
        object="Unify",
        method="generate",
        sync=True,
        type="completion",
    ),
    UnifyDefinition(
        module="unify.clients",
        object="AsyncUnify",
        method="generate",
        sync=False,
        type="completion",
    ),
    UnifyDefinition(
        module="unify.clients",
        object="Unify",
        method="set_endpoint",
        sync=True,
        type="completion",
    ),
    UnifyDefinition(
        module="unify.clients",
        object="AsyncUnify",
        method="set_endpoint",
        sync=False,
        type="completion",
    ),
]

LANGFUSE_DATA = [
    UnifyDefinition(
        module="langfuse",
        object="openai",
        method="_get_langfuse_data_from_kwargs",
        sync=False
    )
]

GENERATION_DATA = [    
    UnifyDefinition(
        module="unify.clients",
        object="Unify",
        method="generate",
        sync=True,
        type="completion",
    ),
    UnifyDefinition(
        module="unify.clients",
        object="AsyncUnify",
        method="generate",
        sync=False,
        type="completion",
    ),
    UnifyDefinition(
        module="unify.chat",
        object="ChatBot",
        method="run",
        sync=True,
        type="chat",
    ),
]

def update_generation_name(wrapped, instance, args, kwargs):
    def wrapper(*args, **kwargs):
        generation, is_nested_trace = wrapped(*args, **kwargs)
        generation["name"] = "Unify-generation"

        return generation, is_nested_trace

    return wrapper(*args, **kwargs)


for resource in LANGFUSE_DATA:
    wrap_function_wrapper(
        resource.module,
        f"{resource.object}.{resource.method}",
        update_generation_name
    )


class Completion(object):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, value)


def wrap_unify_outputs(wrapped, instance, args, kwargs):
    def wrapper(*args, **kwargs):
        usage = None
        if resource.type == "completion":
            choices = Completion({"text": wrapped(*args, **kwargs)})
            output_dict = Completion({"choices": [choices], "usage": usage})
        if resource.type == "chat":
            choices = Completion({"text": {"role": "assisstant", "content": wrapped(*args, **kwargs)}})
            output_dict = Completion({"choices": [choices], "usage": usage})
        return output_dict
    return wrapper(*args, **kwargs)


for resource in GENERATION_DATA:
    wrap_function_wrapper(
        resource.module,
        f"{resource.object}.{resource.method}",
        wrap_unify_outputs
    )


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

    # @observe()
    # def generate(self, model: str, *args, **kwargs):
    #     try:
    #         # Parse the model@provider format
    #         model_name, provider = model.split('@')
    #         log.info(f"Using model: {model_name}, provider: {provider}")

    #         # Call Unify's generate method
    #         response = unify.generate(model=model_name, *args, **kwargs)

    #         # Extract usage and cost from the response if available
    #         tokens_used = response.get('usage', {}).get('total_tokens', 0)
    #         cost_usd = response.get('usage', {}).get('total_cost', 0.0)
    #         self._langfuse.track_usage(model=model_name, tokens=tokens_used, cost_usd=cost_usd)

    #         return response
    #     except Exception as e:
    #         log.error(f"Error in generate method: {e}")
    #         raise

    def register_tracing(self):
        resources = UNIFY_METHODS_V0

        for resource in resources:
            wrap_function_wrapper(
                resource.module,
                f"{resource.object}.{resource.method}",
                _wrap(resource, self.initialize) if resource.sync else _wrap_async(resource, self.initialize)
            )

        setattr(unify, "langfuse_public_key", None)
        setattr(unify, "langfuse_secret_key", None)
        setattr(unify, "langfuse_host", None)
        setattr(unify, "langfuse_debug", None)
        setattr(unify, "langfuse_enabled", True)
        setattr(unify, "flush_langfuse", self.flush)

    # def _wrap(self, resource, initialize):
    #     def wrapper(original_function):
    #         def wrapped(*args, **kwargs):
    #             initialize()
    #             return original_function(*args, **kwargs)
    #         return wrapped
    #     return wrapper

    # def _wrap_async(self, resource, initialize):
    #     async def wrapper(original_function):
    #         async def wrapped(*args, **kwargs):
    #             initialize()
    #             return await original_function(*args, **kwargs)
    #         return wrapped
    #     return wrapper

modifier = UnifyLangfuse()
modifier.register_tracing()
