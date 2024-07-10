# Langfuse x Unify Integration

[Unify](https://unify.ai/) is your central platform for LLM deployment. 🚀

With Unify, you can automatically **find and deploy with the best LLM endpoint** for the [metrics you care about](https://unify.ai/benchmarks), **all with a single API**!

If you use the Unify Python package, you can use the Langfuse drop-in replacement to get full logging by changing only the import.

```diff
- from unify import Unify
+ from langfuse.unify import Unify
```

This requires you to have the unify package installed
```
pip install unifyai
```
## Features
Langfuse automatically tracks:

All prompts/completions with support for streaming, async and functions
Latencies
API Errors
Model usage (tokens) and cost (USD)

## Example Usage:

```python
from langfuse.unify import Unify
from langfuse.decorators import observe
## Set Environment Variables
unify.langfuse_secret_key = os.environ["LANGFUSE_SECRET_KEY"]
unify.langfuse_public_key = os.environ["LANGFUSE_PUBLIC_KEY"]
unify.langfuse_host = os.environ["LANGFUSE_HOST"]
unify_api_key = os.environ["UNIFY_KEY"]

@observe()
def story():
    unify = Unify(endpoint="llama-3-70b-chat@ttft", api_key=unify_api_key)
    response = unify.generate(
        messages=[
            {"role": "system", "content": "You are a great storyteller."},
            {"role": "user", "content": "Once upon a time in a galaxy far, far away..."}
        ],
    )
    return response

@observe()
def main():
    return story()

main()
```
