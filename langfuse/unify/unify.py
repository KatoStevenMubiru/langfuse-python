import os
import logging
from typing import Optional, Dict, List

import requests
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe
from unify import Unify  # Import the Unify library

# Load environment variables (e.g., API key)
load_dotenv()
UNIFY_API_KEY = os.getenv("UNIFY_API_KEY")

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
        self.langfuse = Langfuse()  # Initialize Langfuse client

    @observe(name="query_unify")
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
            return response
        except Exception as e:
            self.langfuse.log_error(
                e,
                f"Unify API query failed for query: {query_text}",
                metadata={"query_text": query_text, "num_results": num_results, **kwargs},
            )
            return None

    def get_endpoint_data(self) -> List[Dict]:
        """Fetches and returns information about available Unify API endpoints.

        Returns:
            A list of dictionaries, each containing information about an endpoint.
        """
        # TODO: Implement this method to fetch endpoint data from the Unify API
        # This would likely involve making an API call to a specific Unify endpoint
        # that provides details about available models and their capabilities.
        pass
