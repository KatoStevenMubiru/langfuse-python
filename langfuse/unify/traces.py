# traces.py
# This module handles trace-related operations using Langfuse.

from langfuse.decorators import langfuse_context, observe
from langfuse import Langfuse

class TraceManager:
    def __init__(self):
        self.langfuse = Langfuse()

    def create_trace_with_metadata(self, metadata):
        """
        Create a trace with the specified metadata.

        :param metadata: A dictionary of metadata.
        :return: The created trace object.
        """
        trace = self.langfuse.trace(metadata=metadata)
        return trace

    @observe()
    def update_trace_metadata(self, metadata):
        """
        Update the current trace with the specified metadata.

        :param metadata: A dictionary of metadata.
        """
        langfuse_context.update_current_trace(metadata=metadata)
