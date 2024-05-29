class UnifyDefinition:
    endpoint: str
    model: str
    provider: str
    module: str
    object: str
    method: str
    type: str
    sync: bool

    def __init__(self, module: str, object: str, method: str, sync: bool):
        self.module = module
        self.object = object
        self.method = method
        self.sync = sync

UNIFY_METHODS_V0 = [
    UnifyDefinition(
        module="unify.chat", # modules are required for tracing
        object="ChatBot", # object is required for tracing
        method="run", # methods are required for tracing
        sync=True,
    ),
    UnifyDefinition(
        module="unify.client",
        object="Unify",
        method="generate",
        sync=True,
    ),
    UnifyDefinition(
        module="unify.client",
        object="AsyncUnify",
        method="generate",
        sync=False,
    ),
]