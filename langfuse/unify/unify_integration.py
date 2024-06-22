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

from typing import Optional, List, Dict, Generator, AsyncGenerator
from unify.exceptions import status_error_map
from langfuse.utils.langfuse_singleton import LangfuseSingleton
from langfuse.openai import openai, OpenAILangfuse

try:
    import unify
except ImportError:
    raise ModuleNotFoundError(
        "Please install unify to use this feature: 'pip install unifyai'"
    )

from unify import Unify, AsyncUnify, ChatBot


def new_setattr(name, value):
    if name in [
        "langfuse_public_key",
        "langfuse_secret_key",
        "langfuse_host",
        "langfuse_debug",
        "langfuse_enabled",
        "flush_langfuse",
    ]:
        setattr(unify, name, value)
        setattr(openai, name, value)
    else:
        setattr(unify, name, value)


unify.__setattr__ = new_setattr


class UnifyLangfuse(OpenAILangfuse):
    _langfuse: Optional[LangfuseSingleton] = None

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

    def reassign_tracing(self):
        setattr(unify, "langfuse_public_key", openai.langfuse_public_key)
        setattr(unify, "langfuse_secret_key", openai.langfuse_secret_key)
        setattr(unify, "langfuse_host", openai.langfuse_host)
        setattr(unify, "langfuse_debug", openai.langfuse_debug)
        setattr(unify, "langfuse_enabled", openai.langfuse_enabled)
        setattr(unify, "flush_langfuse", openai.flush_langfuse)


OpenAILangfuse.initialize = UnifyLangfuse.initialize
modifier = UnifyLangfuse()
modifier.reassign_tracing()


class Unify(Unify):
    def __init__(
        self,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        super().__init__(endpoint, model, provider, api_key)

    def generate_completion(self, endpoint, messages, max_tokens, stream, **kwargs):
        chat_completion = self.client.chat.completions.create(
            model=endpoint,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
            stream=stream,
            name="Unify-generation",
            metadata={
                "model": self.model,
                "provider": self.provider,
                "endpoint": self.endpoint,
            },
            **kwargs,
        )
        return chat_completion

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


unify.Unify = Unify
unify.AsyncUnify = AsyncUnify
unify.ChatBot = ChatBot
