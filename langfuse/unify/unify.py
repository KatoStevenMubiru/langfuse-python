import os
import logging
from typing import Optional, Dict, List

from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe
from unify import Unify  # Import the Unify library

# Load environment variables (e.g., API key)
load_dotenv()
UNIFY_API_KEY = os.getenv("UNIFY_API_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifyClient:
    """A client for interacting with the Unify API, integrated with Langfuse for LLM observability."""

    def __init__(self, api_key: str, base_url: str = "https://api.unify.com/v1"):
        """Initializes the UnifyClient.

        Args:
            api_key: Your Unify API key.
            base_url: The base URL for the Unify API (default: "https://api.unify.com/v1").
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.unify = Unify(api_key=api_key)  # Initialize Unify client
        self.langfuse = Langfuse(
            secret_key=LANGFUSE_SECRET_KEY,
            public_key=LANGFUSE_PUBLIC_KEY,
            host=LANGFUSE_HOST,
            flush_at=5,
            flush_interval=10000
        )  # Initialize Langfuse client with batching

    @observe(name="query_unify", as_type="generation")
    def query(self, query_text: str, num_results: int = 5, **kwargs) -> Optional[Dict]:
        """Sends a query to the Unify API and returns the results.

        Args:
            query_text: The text to query the Unify API with.
            num_results: The maximum number of results to return.
            **kwargs: Additional query parameters for the Unify API.

        Returns:
            A dictionary containing the query results, or None if the request failed.
        """
        try:
            response = self.unify.query(
                query_text, 
                model=kwargs.get("model", None),  # Pass model if provided
                num_results=num_results
            )
            self.langfuse.log_event(
                "unify_response_received",
                {"status": "success", "results_count": len(response.get("results", []))},
            )
            self.langfuse.flush()  # Ensure logs are sent immediately for quick visibility
            return response
        except Exception as e:
            self.langfuse.log_error(
                e,
                f"Unify API query failed for query: {query_text}",
                metadata={"query_text": query_text, "num_results": num_results, **kwargs},
            )
            self.langfuse.flush()  # Ensure logs are sent immediately for quick visibility
            return None

    @observe(name="get_endpoint_data")
    def get_endpoint_data(self) -> List[Dict]:
        """Fetches and returns information about available Unify API endpoints.

        Returns:
            A list of dictionaries, each containing information about an endpoint.
        """
        try:
            # TODO: Implement this method to fetch endpoint data from the Unify API
            # This would likely involve making an API call to a specific Unify endpoint
            # that provides details about available models and their capabilities.
            data = []  # Placeholder for the actual data retrieval logic
            self.langfuse.log_event("endpoints_retrieved", {"endpoint_count": len(data)})
            self.langfuse.flush()  # Ensure logs are sent immediately for quick visibility
            return data
        except Exception as e:
            self.langfuse.log_error(e, {"context": "fetching endpoint data"})
            self.langfuse.flush()  # Ensure logs are sent immediately for quick visibility
            return []

# Example usage:
# unify_client = UnifyClient(api_key=UNIFY_API_KEY)
# result = unify_client.query("example query")
# print(result)
