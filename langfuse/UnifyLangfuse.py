import importlib
import sys
import logging
from typing import Optional
from langfuse.utils.langfuse_singleton import LangfuseSingleton
from langfuse.decorators import langfuse_context
from langfuse import Langfuse
import unify

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("langfuse.unify")

# Conditional import for langfuse.openai
if importlib.util.find_spec('langfuse.openai') is not None:
    openai = __import__('langfuse.openai', fromlist=[None]).openai
    sys.modules['openai']

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

UNIFY_METHODS_V0 = [
    UnifyDefinition(
        module="unify.chat",
        object="ChatBot",
        method="run",
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

    @lobserve()
    def generate(self, model: str, *args, **kwargs):
        try:
            # Parse the model@provider format
            model_name, provider = model.split('@')
            log.info(f"Using model: {model_name}, provider: {provider}")

            # Call Unify's generate method
            response = unify.generate(model=model_name, *args, **kwargs)

            # Extract usage and cost from the response if available
            tokens_used = response.get('usage', {}).get('total_tokens', 0)
            cost_usd = response.get('usage', {}).get('total_cost', 0.0)
            self._langfuse.track_usage(model=model_name, tokens=tokens_used, cost_usd=cost_usd)

            return response
        except Exception as e:
            log.error(f"Error in generate method: {e}")
            raise

    def register_tracing(self):
        resources = UNIFY_METHODS_V0

        for resource in resources:
            wrap_function_wrapper(
                resource.module,
                f"{resource.object}.{resource.method}",
                self._wrap(resource) if resource.sync else self._wrap_async(resource)
            )

        setattr(unify, "langfuse_public_key", None)
        setattr(unify, "langfuse_secret_key", None)
        setattr(unify, "langfuse_host", None)
        setattr(unify, "langfuse_debug", None)
        setattr(unify, "langfuse_enabled", True)
        setattr(unify, "flush_langfuse", self.flush)

    def _wrap(self, resource, initialize):
        def wrapper(original_function):
            def wrapped(*args, **kwargs):
                initialize()
                return original_function(*args, **kwargs)
            return wrapped
        return wrapper

    def _wrap_async(self, resource, initialize):
        async def wrapper(original_function):
            async def wrapped(*args, **kwargs):
                initialize()
                return await original_function(*args, **kwargs)
            return wrapped
        return wrapper

modifier = UnifyLangfuse()
modifier.register_tracing()
