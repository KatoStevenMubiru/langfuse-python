"""If you use the unifyai Python package, you can use the Langfuse drop-in replacement to get full logging by changing only the import.

```diff
- import unify
+ from langfuse.unify import unify
```

Langfuse automatically tracks:

- All prompts/completions with support for streaming, async and functions
- Latencies
- API Errors
- Model usage (tokens) and cost (USD)

The integration is fully interoperable with the `observe()` decorator and the low-level tracing SDK.

See docs for more details: https://langfuse.com/docs/integrations/openai
"""
from wrapt import wrap_function_wrapper
from langfuse.openai import OpenAiDefinition, auth_check, _filter_image_data

try:
    import unify
except ImportError:
    raise ModuleNotFoundError(
        "Please install unify to use this feature: 'pip install unifyai'"
    )

LANGFUSE_DATA = [
    OpenAiDefinition(
        module="langfuse",
        object="openai",
        method="_get_langfuse_data_from_kwargs",
        type="",
        sync=False
    )
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
