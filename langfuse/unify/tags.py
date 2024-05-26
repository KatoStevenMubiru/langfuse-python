# tags.py
# This module handles operations related to tags using Langfuse.

from langfuse.decorators import langfuse_context, observe
from langfuse import Langfuse

class TagManager:
    def __init__(self):
        self.langfuse = Langfuse()

    @observe()
    def add_tags(self, tags):
        """
        Add tags to the current trace.

        :param tags: A list of tags.
        """
        langfuse_context.update_current_trace(tags=tags)
