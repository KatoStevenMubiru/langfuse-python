import requests
from langfuse.decorators import observe

@observe()
def query_unify(query_text: str, num_results: int = 5) -> dict:
    """Queries the Unify API with the given query text and returns the results."""

    headers = {
        "Authorization": f"Bearer {YOUR_UNIFY_API_KEY}",
        "Content-Type": "application/json",
    }

    # Construct the request payload based on Unify API's requirements
    payload = {
        "query": query_text,
        "num_results": num_results,
        # ... other parameters you want to include ...
    }

    response = requests.post(
        "https://api.unify.com/v1/search",  # Replace with the actual Unify API endpoint
        json=payload,
        headers=headers,
    )

    response.raise_for_status()  # Raise an exception if the request failed

    data = response.json()
    return data
