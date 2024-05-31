# unify.py
# Main script that uses the various modules to perform operations with Langfuse.

from users import UserManager
from traces import TraceManager
from metadata import MetadataManager
from tags import TagManager

from langfuse.decorators import observe, langfuse_context
from langfuse.openai import openai # OpenAI integration

class UnifyLangfuse:
    unify_client = openai.OpenAI(base_url="https://api.unify.ai/v0/")


def main():
    user_manager = UserManager()
    trace_manager = TraceManager()
    metadata_manager = MetadataManager()
    tag_manager = TagManager()

    # Example usage
    user_trace = user_manager.create_trace_for_user('user-id')
    print(f"User Trace: {user_trace}")

    trace_with_metadata = trace_manager.create_trace_with_metadata({'key': 'value'})
    print(f"Trace with Metadata: {trace_with_metadata}")

    metadata_manager.update_metadata({'key': 'new_value'})
    print("Metadata updated.")

    tag_manager.add_tags(['tag1', 'tag2'])
    print("Tags added.")

if __name__ == '__main__':
    main()
