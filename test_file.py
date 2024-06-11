# from langfuse.unify import unify
# from langfuse.unify import openai
from langfuse.UnifyLangfuse import unify, UnifyLangfuse
from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe
import os
from dotenv import load_dotenv

load_dotenv()

print(unify.langfuse_enabled)
path = os.environ["PATH"]
unify.langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
unify.langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
unify.langfuse_host = os.getenv("LANGFUSE_HOST")
unify_api_key = os.getenv("UNIFY_API_KEY")
print(unify.langfuse_host)

from langfuse.decorators import langfuse_context, observe
langfuse = UnifyLangfuse().initialize()
client = unify.Unify(endpoint="gpt-3.5-turbo@openai", api_key=unify_api_key)

# @observe() # decorator to automatically create trace and nest generations
def main(country: str, user_id: str, **kwargs) -> str:
    # nested generation 1: use openai to get capital of country
    global client
    client.set_provider("openai")
    capital = client.generate(messages=[
          {"role": "system", "content": "You are a Geography teacher helping students learn the capitals of countries. Output only the capital when being asked."},
          {"role": "user", "content": country}])
    capital_input = capital.choices[0].text["content"]
    # nested generation 2: use openai to write poem on capital
    poem = client.generate(
       messages=[
          {"role": "system", "content": "You are a poet. Create a poem about a city."},
          {"role": "user", "content": capital_input}]
    )
 
    # rename trace and set attributes (e.g., medatata) as needed
    langfuse_context.update_current_trace(
        name="City poem generator",
        session_id="1234",
        user_id=user_id,
        tags=["tag1", "tag2"],
        public=True,
        metadata = {
        "env": "development",
        },
        release = "v0.0.21"
    )
 
    return poem.choices[0].text["content"]
 
# create random trace_id, could also use existing id from your application, e.g. conversation id
trace_id = "0"
 
# run main function, set your own id, and let Langfuse decorator do the rest
print(main("Bulgaria", "admin", langfuse_observation_id=trace_id))