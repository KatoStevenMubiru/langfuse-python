# metadata.py
# This module handles operations related to metadata using Langfuse.

from langfuse.decorators import langfuse_context, observe
from langfuse import Langfuse

class MetadataManager:
    def __init__(self):
        self.langfuse = Langfuse()

    @observe()
    def update_metadata(self, metadata):
        """
        Update the current trace with the specified metadata.

        :param metadata: A dictionary of metadata.
        """
        langfuse_context.update_current_trace(metadata=metadata)
