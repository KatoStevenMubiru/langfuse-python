# users.py
# This module handles user-related operations using Langfuse.

from langfuse.decorators import langfuse_context, observe
from langfuse import Langfuse

class UserManager:
    def __init__(self):
        self.langfuse = Langfuse()

    def create_trace_for_user(self, user_id):
        """
        Create a trace for the specified user.

        :param user_id: The ID of the user.
        :return: The created trace object.
        """
        trace = self.langfuse.trace(user_id=user_id)
        return trace

    @observe()
    def update_user_trace(self, user_id):
        """
        Update the current trace with the specified user ID.

        :param user_id: The ID of the user.
        """
        langfuse_context.update_current_trace(user_id=user_id)
