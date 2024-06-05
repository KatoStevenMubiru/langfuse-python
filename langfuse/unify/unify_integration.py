import os
import logging
from unify import unify
from wrapt import wrap_function_wrapper
from langfuse import Langfuse
from langfuse.client import StatefulGenerationClient
from langfuse.decorators import langfuse_context, observe
from langfuse.utils.langfuse_singleton import LangfuseSingleton
from langfuse.openai import openai, OpenAiDefinition, auth_check, _filter_image_data  # Overriding Unify's OpenAI import

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("langfuse.unify")

class UnifyDefinition:
    """
    Class to define Unify method specifications for integration.
    """
    def __init__(self, module: str, object: str, method: str, type: str, sync: bool):
        self.module = module
        self.object = object
        self.method = method
        self.type = type
        self.sync = sync

class LangfuseUnifyIntegration:
    """
    Class to integrate Langfuse with Unify, enhancing functionality with usage tracking.
    """
    def __init__(self, api_key):
        # Initialize Langfuse client
        self.langfuse_client = LangfuseSingleton.get_instance()
        # Initialize Unify with the provided API key
        self.unify = Unify(api_key=api_key)
    @observe()
    def generate(self, model: str, *args, **kwargs):
        try:
            # Parse the model@provider format
            model_name, provider = model.split('@')
            log.info(f"Using model: {model_name}, provider: {provider}")

            # Call Unify's generate method
            response = self.unify.generate(model=model_name, *args, **kwargs)

            # Extract usage and cost from the response if available
            tokens_used = response.get('usage', {}).get('total_tokens', 0)
            cost_usd = response.get('usage', {}).get('total_cost', 0.0)
            self.langfuse_client.track_usage(model=model_name, tokens=tokens_used, cost_usd=cost_usd)

            return response
        except Exception as e:
            log.error(f"Error in generate method: {e}")
            raise

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

# Example usage
if __name__ == "__main__":
    # Retrieve the UNIFY_KEY from the environment variables
    api_key = os.getenv("UNIFY_API_KEY")
    if not api_key:
        raise EnvironmentError("UNIFY_KEY environment variable not set")

    # Instantiate the integration class with the API key
    langfuse_unify = LangfuseUnifyIntegration(api_key)
    try:
        # Example call to the generate method
        response = langfuse_unify.generate(model="gpt-3.5@openai", prompt="Hello, world!")
        print(response)
    except Exception as e:
        log.error(f"Error during example usage: {e}")
