# unify.py
# Main script that uses the various modules to perform operations with Langfuse.

from users import UserManager
from traces import TraceManager
from metadata import MetadataManager
from tags import TagManager

class UnifyDefinition:
    endpoint: str
    model: str
    provider: str
    module: str
    object: str
    method: str
    type: str
    sync: bool

    def __init__(self, module: str, object: str, method: str, type: str, sync: bool):
        self.endpoint = endpoint
        self.model = model
        self.provider = provider
        self.module = module
        self.object = object
        self.method = method
        self.type = type
        self.sync = sync

UNIFY_METHODS_V0 = [
    UnifyDefinition(
        module="unify.chat",
        object="ChatBot",
        method="run",
        type="chat",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.client",
        object="Unify",
        method="generate",
        type="completion",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.client",
        object="AsyncUnify",
        method="generate",
        type="completion",
        sync=False,
    ),
]

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
