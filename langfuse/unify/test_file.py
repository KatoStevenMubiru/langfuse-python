# from langfuse.unify import unify
# from langfuse.unify import openai
from unify_integration import unify
import os
from dotenv import load_dotenv

load_dotenv()
print(f"LangFuse auth_check: {unify.auth_check()}")
print(f"LangFuse Enabled: {unify.langfuse_enabled}")
path = os.environ["PATH"]
unify.langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
unify.langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
unify.langfuse_host = os.getenv("LANGFUSE_HOST")
unify_api_key = os.getenv("UNIFY_API_KEY")
print(f"LangFuse host: {unify.langfuse_host}")

client = unify.Unify(
    endpoint="mistral-7b-instruct-v0.2@fireworks-ai", api_key=unify_api_key
)


# @observe()  # decorator to automatically create trace and nest generations
def main(country: str, user_id: str, **kwargs) -> str:
    # nested generation 1: use openai to get capital of country
    global client
    capital = client.generate(
        messages=[
            {
                "role": "system",
                "content": "You are a Geography teacher helping students learn the capitals of countries. Output only the capital when being asked.",
            },
            {"role": "user", "content": country},
        ]
    )
    print(capital)
    capital_input = capital
    # nested generation 2: use openai to write poem on capital
    poem = client.generate(
        messages=[
            {
                "role": "system",
                "content": "You are a poet. Create a poem about a city.",
            },
            {"role": "user", "content": capital_input},
        ]
    )

    # rename trace and set attributes (e.g., medatata) as needed
    # langfuse_context.update_current_trace(
    #     name="City poem generator",
    #     session_id="1234",
    #     user_id=user_id,
    #     tags=["tag1", "tag2"],
    #     public=True,
    #     metadata={
    #         "env": "development",
    #     },
    #     release="v0.0.21",
    # )

    return poem


# create random trace_id, could also use existing id from your application, e.g. conversation id
trace_id = "0"

# run main function, set your own id, and let Langfuse decorator do the rest
print(main("Bulgaria", "admin", langfuse_observation_id=trace_id))
