"""If you use the unifyai Python package, you can use the Langfuse drop-in replacement to get full logging by changing only the import.

```diff
- from unify import Unify
+ from langfuse.unify import Unify
```

Langfuse automatically tracks:

- All prompts/completions with support for streaming, async and functions
- Latencies
- API Errors
- Model usage (tokens) and cost (USD)

The integration is fully interoperable with the `observe()` decorator and the low-level tracing SDK.

See docs for more details: https://langfuse.com/docs/integrations/openai
"""

from wrapt import resolve_path
from types import MethodType
from typing import Optional, List, Dict, Generator, AsyncGenerator
from langfuse.openai import (
    openai,
    modifier,
    OPENAI_METHODS_V1,
    wrap_function_wrapper,
    _wrap,
    _wrap_async,
    OpenAiDefinition,
    auth_check,
    _filter_image_data
)
from langfuse.utils.langfuse_singleton import LangfuseSingleton
from unify.exceptions import status_error_map

try:
    import unify
except ImportError:
    raise ModuleNotFoundError(
        "Please install unify to use this feature: 'pip install unifyai'"
    )

from unify import Unify, AsyncUnify, ChatBot

LANGFUSE_DATA = [
    OpenAiDefinition(
        module="langfuse",
        object="openai",
        method="_get_langfuse_data_from_default_response",
        type="",
        sync=False
    )
]

def unify_initialize(self):
    self._langfuse = LangfuseSingleton().get(
        public_key=unify.langfuse_public_key,
        secret_key=unify.langfuse_secret_key,
        host=unify.langfuse_host,
        debug=unify.langfuse_debug,
        enabled=unify.langfuse_enabled,
        sdk_integration="unify",
    )
    return self._langfuse


def unify_register_tracing(self):
    for resource in OPENAI_METHODS_V1:
        parent, attribute, wrapper = resolve_path(
            resource.module,
            f"{resource.object}.{resource.method}"
        )

        # revert to original function
        original = wrapper.__wrapped__
        setattr(parent, attribute, original)

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


modifier.initialize = MethodType(unify_initialize, modifier)
modifier.register_tracing = MethodType(unify_register_tracing, modifier)
modifier.register_tracing()


class Unify(Unify):
    def __init__(
        self,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        super().__init__(endpoint, model, provider, api_key)
        if modifier._langfuse is None:
            modifier.initialize()

        self.c1 = 0.0
        self.c2 = 0.0
        self.total_cost = 0.0

        # manually ingest cost,
        for resource in LANGFUSE_DATA:
            wrap_function_wrapper(
                resource.module,
                f"{resource.object}.{resource.method}",
                self.update_cost
            )

    def generate_completion(self, endpoint, messages, max_tokens, stream, **kwargs):
        self.c1 = self.get_credit_balance()

        chat_completion = self.client.chat.completions.create(
            model=endpoint,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
            stream=stream,
            name="Unify-generation",
            metadata={
                "model": self.model,
                "provider": self.provider,  # todo: update trace metadata after call (see set_provider)
                "endpoint": self.endpoint,
            },
            **kwargs,
        )

        return chat_completion

    def update_cost(self, wrapped, instance, args, kwargs):
        self.c2 = self.get_credit_balance()
        self.total_cost = self.c1 - self.c2
        def wrapper(*args, **kwargs):
            # add usage total_costs
            # use provider.input_cost, provider.output_cost when available
            model, completion, usage = wrapped(*args, **kwargs)
            usage["total_cost"] = self.total_cost

            return model, completion, usage

        return wrapper(*args, **kwargs)


    def _generate_stream(
        self,
        messages: List[Dict[str, str]],
        endpoint: str,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Generator[str, None, None]:
        try:
            chat_completion = self.generate_completion(
                endpoint, messages, max_tokens, True, **kwargs
            )

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
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        try:
            chat_completion = self.generate_completion(
                endpoint, messages, max_tokens, False, **kwargs
            )

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
        if modifier._langfuse is None:
            modifier.initialize()

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
        **kwargs,
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
        **kwargs,
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

        if modifier._langfuse is None:
            modifier.initialize()


unify.Unify = Unify
unify.AsyncUnify = AsyncUnify
unify.ChatBot = ChatBot
