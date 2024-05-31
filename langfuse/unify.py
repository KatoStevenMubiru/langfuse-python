# unify.py
# Main script that uses the various modules to perform operations with Langfuse.
import importlib
import sys
# del sys.modules['openai']
# sys.modules['openai'] = __import__('langfuse.openai', fromlist=[None]).openai

if importlib.util.find_spec('langfuse.openai') is not None:
    openai = __import__('langfuse.openai', fromlist=[None]).openai
    sys.modules['openai']

import unify

class OpenAILangfuse:
    _langfuse: Optional[Langfuse] = None

    def initialize(self):
        self._langfuse = LangfuseSingleton().get(
            public_key=openai.langfuse_public_key,
            secret_key=openai.langfuse_secret_key,
            host=openai.langfuse_host,
            debug=openai.langfuse_debug,
            enabled=openai.langfuse_enabled,
            sdk_integration="openai",
        )

        return self._langfuse

    def flush(cls):
        cls._langfuse.flush()

    def register_tracing(self):
        resources = OPENAI_METHODS_V1 if _is_openai_v1() else OPENAI_METHODS_V0

        for resource in resources:
            wrap_function_wrapper(
                resource.module,
                f"{resource.object}.{resource.method}",
                _wrap(resource, self.initialize)
                if resource.sync
                else _wrap_async(resource, self.initialize),
            )

        setattr(openai, "langfuse_public_key", None)
        setattr(openai, "langfuse_secret_key", None)
        setattr(openai, "langfuse_host", None)
        setattr(openai, "langfuse_debug", None)
        setattr(openai, "langfuse_enabled", True)
        setattr(openai, "flush_langfuse", self.flush)


modifier = OpenAILangfuse()
modifier.register_tracing()