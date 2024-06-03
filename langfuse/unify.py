# unify.py
# Main script that uses the various modules to perform operations with Langfuse.
from typing import Optional, List, Dict, Generator, AsyncGenerator

from wrapt import wrap_function_wrapper

from langfuse.utils.langfuse_singleton import LangfuseSingleton

from langfuse import Langfuse
from unify.exceptions import status_error_map
from langfuse.openai import openai, OpenAiDefinition, _wrap, _wrap_async

try:
    import unify
except ImportError:
    raise ModuleNotFoundError(
        "Please install unify to use this feature: 'pip install unifyai'"
    )

from unify import Unify, AsyncUnify, ChatBot

class Unify(Unify):
    def __init__(
            self,
            endpoint: Optional[str] = None,
            model: Optional[str] = None,
            provider: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        super().__init__(endpoint, model, provider, api_key)

    def generate_completion(self, endpoint, messages, max_tokens, stream):
        chat_completion = self.client.chat.completions.create(
            model=endpoint,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
            stream=stream,
        )

        return chat_completion

    def _generate_stream(
            self,
            messages: List[Dict[str, str]],
            endpoint: str,
            max_tokens: Optional[int] = None
    ) -> Generator[str, None, None]:
        try:
            chat_completion = self.generate_completion(endpoint, messages, max_tokens, True,)

            for chunk in chat_completion:
                content = chunk.choices[0].delta.content  # type: ignore[union-attr]
                self.set_provider(chunk.model.split("@")[-1])  # type: ignore[union-attr]
                if content is not None:
                    yield content
        except openai.APIStatusError as e:
            raise status_error_map[e.status_code](e.message) from None

    def _generate_non_stream(
        self,
        messages: List[Dict[str, str]],
        endpoint: str,
        max_tokens: Optional[int] = None
    ) -> str:
        try:
            chat_completion = self.generate_completion(endpoint, messages, max_tokens, False,)

            self.set_provider(
                chat_completion.model.split(  # type: ignore[union-attr]
                    "@",
                )[-1]
            )

            return chat_completion.choices[0].message.content.strip(" ")  # type: ignore # noqa: E501, WPS219
        except openai.APIStatusError as e:
            raise status_error_map[e.status_code](e.message) from None

class AsyncUnify(AsyncUnify):
    def __init__(
            self,
            endpoint: Optional[str] = None,
            model: Optional[str] = None,
            provider: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        super().__init__(endpoint, model, provider, api_key)

    async def async_generate_completion(self, endpoint, messages, max_tokens, stream):
        chat_completion = await self.client.chat.completions.create(
                model=endpoint,
                messages=messages,  # type: ignore[arg-type]
                max_tokens=max_tokens,
                stream=stream,
            )

        return chat_completion

    async def _generate_stream(
        self,
        messages: List[Dict[str, str]],
        endpoint: str,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        try:
            async_stream = self.async_generate_completion(
                endpoint,
                messages,  # type: ignore[arg-type]
                max_tokens,
                True,
            )
            async for chunk in async_stream:  # type: ignore[union-attr]
                self.set_provider(chunk.model.split("@")[-1])
                yield chunk.choices[0].delta.content or ""
        except openai.APIStatusError as e:
            raise status_error_map[e.status_code](e.message) from None

    async def _generate_non_stream(
        self,
        messages: List[Dict[str, str]],
        endpoint: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        try:
            async_response = self.async_generate_completion(
                endpoint,
                messages,  # type: ignore[arg-type]
                max_tokens,
                True,
            )
            self.set_provider(async_response.model.split("@")[-1])  # type: ignore
            return async_response.choices[0].message.content.strip(" ")  # type: ignore # noqa: E501, WPS219
        except openai.APIStatusError as e:
            raise status_error_map[e.status_code](e.message) from None

class ChatBot(ChatBot):
    class ChatBot:  # noqa: WPS338
        """Agent class represents an LLM chat agent."""

        def __init__(
                self,
                endpoint: Optional[str] = None,
                model: Optional[str] = None,
                provider: Optional[str] = None,
                api_key: Optional[str] = None,
        ) -> None:
            super().__init__(endpoint, model, provider, api_key)
            self._client = Unify(
                api_key=api_key,
                endpoint=endpoint,
                model=model,
                provider=provider,
            )


UNIFY_METHODS_V0 = [
    OpenAiDefinition(
        module="langfuse.unify", # modules are required for tracing
        object="ChatBot", # object is required for tracing
        method="run", # methods are required for tracing
        type="chat",
        sync=True,
    ),
    OpenAiDefinition(
        module="langfuse.unify",
        object="Unify",
        method="generate_completion",
        type="chat",
        sync=True,
    ),
    OpenAiDefinition(
        module="unify.clients",
        object="AsyncUnify",
        method="generate",
        type="chat",
        sync=False,
    ),
]

LANGFUSE_DATA = [
    OpenAiDefinition(
        module="langfuse",
        object="openai",
        method="_get_langfuse_data_from_kwargs",
        type="",
        sync=False
    )
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

    def get_trace_id(self, wrapped, instance, args, kwargs):
        # To update Openai-generation to unify-generation
        def wrapper(*args, **kwargs):
            generation, is_nested_trace = wrapped(*args, **kwargs)
            trace_id = generation["trace_id"]
            langfuse = args[1]
            print(langfuse.trace(id=trace_id))

            return generation, is_nested_trace

        return wrapper(*args, **kwargs)

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

        for resource in LANGFUSE_DATA:
            wrap_function_wrapper(
                resource.module,
                f"{resource.object}.{resource.method}",
                self.get_trace_id
            )

        setattr(unify, "langfuse_public_key", None)
        setattr(unify, "langfuse_secret_key", None)
        setattr(unify, "langfuse_host", None)
        setattr(unify, "langfuse_debug", None)
        setattr(unify, "langfuse_enabled", True)
        setattr(unify, "flush_langfuse", self.flush)

# Perform on UNIFY_METHODS_V0
modifier = UnifyLangfuse()
modifier.register_tracing()
