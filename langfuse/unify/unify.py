import requests
from langfuse import Langfuse
from langfuse.decorators import observe
import os
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, List
from unify import Unify

# Load environment variables (e.g., API key)
load_dotenv()
UNIFY_API_KEY = os.getenv("UNIFY_API_KEY")

# Set up logging for debugging and error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifyClient:
    """A client for interacting with the Unify API."""

    def __init__(self, api_key: str, base_url: str = "https://api.unify.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        self.langfuse = Langfuse()  # Initialize Langfuse client

    @observe(name="query_unify")  # Trace this function with Langfuse
    def query(self, query_text: str, num_results: int = 5, **kwargs) -> Optional[Dict]:
        """Sends a query to the Unify API and returns the results.

        Args:
            query_text: The text to query the Unify API with.
            num_results: The maximum number of results to return.
            **kwargs: Additional query parameters for the Unify API.

        Returns:
            A dictionary containing the query results, or None if the request failed.
        """
        endpoint = "/search"  # Default endpoint; can be changed for other API calls
        url = f"{self.base_url}{endpoint}"

        payload = {
            "query": query_text,
            "num_results": num_results,
            **kwargs  # Include any additional query parameters
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            self.langfuse.log_event(
                "unify_response_received",
                {"status_code": response.status_code, "results_count": len(data.get("results", []))},
            )  # Log response details to Langfuse
            return data
        except requests.exceptions.RequestException as e:
            self.langfuse.log_error(
                e,
                f"Unify API request failed for query: {query_text}",
                metadata={"url": url, "payload": payload},  # Log error details
            )
            return None

    def get_endpoint_data(self) -> List[Dict]:
        """Fetches and returns information about available Unify API endpoints.

        Returns:
            A list of dictionaries, each containing information about an endpoint (e.g., name, description).
        """
        # ... Your implementation to fetch endpoint data from Unify API ...
        pass  # Placeholder for now
