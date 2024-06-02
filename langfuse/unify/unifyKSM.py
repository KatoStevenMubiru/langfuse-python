import os
import logging
import copy
from unify import Unify
from langfuse import Langfuse
from langfuse.client import StatefulGenerationClient
from langfuse.decorators import langfuse_context
from langfuse.utils import _get_timestamp
from langfuse.utils.langfuse_singleton import LangfuseSingleton

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
    Class to extract relevant arguments from Unify API calls for Langfuse tracing and monitoring.
    """
    def __init__(self, **kwargs):
        self.args = kwargs

    def get_langfuse_args(self):
        """
        Prepare arguments for Langfuse tracing.
        """
        return self.args

    def get_unify_args(self):
        """
        Prepare arguments for Unify API call.
        """
        return self.args

def _langfuse_wrapper(func):
    """
    Decorator to wrap Unify methods for integration with Langfuse.
    """
    def wrapper(*args, **kwargs):
        unify_args_extractor = UnifyArgsExtractor(**kwargs)
        langfuse_args = unify_args_extractor.get_langfuse_args()
        unify_args = unify_args_extractor.get_unify_args()
        return func(*args, **unify_args, **langfuse_args)
    return wrapper

class UnifyIntegration:
    """
    Handles the integration between Unify API and Langfuse for enhanced monitoring and tracing.
    """
    def __init__(self, api_key):
        """
        Initialize the Unify client with the provided API key.
        """
        self.unify_client = Unify(api_key=api_key)

    @_langfuse_wrapper
    def generate_response(self, model_id, provider_id, input_text, stream=False):
        """
        Generate a response from a specified model and provider using the Unify API.
        """
        endpoint = f"{model_id}@{provider_id}"
        try:
            response = self.unify_client.generate(endpoint, input_text, stream=stream)
            log.info(f"Response retrieved from {endpoint}: {response}")
            return response
        except Exception as e:
            log.error(f"Error querying Unify API: {str(e)}")
            raise

def main():
    """
    Main function to demonstrate the usage of the UnifyIntegration class.
    """
    api_key = os.getenv("UNIFY_KEY")
    if not api_key:
        raise ValueError("UNIFY_KEY environment variable not set")

    unify_integration = UnifyIntegration(api_key)
    model_id = "mistral-7b-instruct-v0.2"
    provider_id = "fireworks-ai"
    input_text = "Explain who Newton was and his entire theory of gravitation."

    response = unify_integration.generate_response(model_id, provider_id, input_text, stream=True)
    print(response)

if __name__ == "__main__":
    main()