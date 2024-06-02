import os
import logging
import copy
from unify import Unify
from langfuse import Langfuse
from langfuse.client import StatefulGenerationClient
from langfuse.decorators import langfuse_context
from langfuse.utils import _get_timestamp
from langfuse.utils.langfuse_singleton import LangfuseSingleton
from langfuse.openai import openai  # Overriding Unify's OpenAI import

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

# Define the methods from Unify that will be integrated
UNIFY_METHODS = [
    UnifyDefinition(
        module="unify",
        object="Unify",
        method="generate",
        type="chat",
        sync=True,
    ),
]

class UnifyArgsExtractor:
    """
    Class to extract arguments for Unify methods.
    """
    def __init__(self, module, object, method, *args, **kwargs):
        self.module = module
        self.object = object
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def extract(self):
        # Implement argument extraction logic if needed
        return self.args, self.kwargs

class LangfuseUnifyIntegration:
    """
    Class to integrate Langfuse with Unify.
    """
    def __init__(self):
        # Using singleton pattern to ensure single instance
        self.langfuse_client = LangfuseSingleton.get_instance()
        self.unify = Unify()

    @langfuse_context
    def generate(self, model: str, *args, **kwargs):
        try:
            # Parse the model@provider format
            model_name, provider = model.split('@')
            
            # Log the model and provider
            log.info(f"Using model: {model_name}, provider: {provider}")

            # Call Unify's generate method
            response = self.unify.generate(model=model_name, *args, **kwargs)

            # Track usage and cost
            tokens_used = response['usage']['total_tokens']
            cost_usd = response['usage']['total_cost']
            self.langfuse_client.track_usage(model=model_name, tokens=tokens_used, cost_usd=cost_usd)

            return response
        except Exception as e:
            log.error(f"Error in generate method: {e}")
            raise

# Example usage
if __name__ == "__main__":
    langfuse_unify = LangfuseUnifyIntegration()
    try:
        response = langfuse_unify.generate(model="gpt-3.5@openai", prompt="Hello, world!")
        print(response)
    except Exception as e:
        log.error(f"Error during example usage: {e}")
