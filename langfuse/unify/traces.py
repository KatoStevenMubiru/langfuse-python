# traces.py
# This module handles trace-related operations using Langfuse.

from langfuse.decorators import langfuse_context, observe
from langfuse import Langfuse
from typing import Optional

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
        
    @observe()
    def update_current_observation(self,
        *,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        metadata: Optional[Any] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        release: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
        completion_start_time: Optional[datetime] = None,
        model: Optional[str] = None,
        model_parameters: Optional[Dict[str, MapValue]] = None,
        usage: Optional[Union[BaseModel, ModelUsage]] = None,
        prompt: Optional[PromptClient] = None,
        public: Optional[bool] = None,
    ):
        """Update parameters for the current observation within an active trace context.

        This method dynamically adjusts the parameters of the most recent observation on the observation stack.
        It allows for the enrichment of observation data with additional details such as input parameters, output results, metadata, and more,
        enhancing the observability and traceability of the execution context.

        Note that if a param is not available on a specific observation type, it will be ignored.

        Shared params:
            - `input` (Optional[Any]): The input parameters of the trace or observation, providing context about the observed operation or function call.
            - `output` (Optional[Any]): The output or result of the trace or observation
            - `name` (Optional[str]): Identifier of the trace or observation. Useful for sorting/filtering in the UI.
            - `metadata` (Optional[Any]): Additional metadata of the trace. Can be any JSON object. Metadata is merged when being updated via the API.
            - `start_time` (Optional[datetime]): The start time of the observation, allowing for custom time range specification.
            - `end_time` (Optional[datetime]): The end time of the observation, enabling precise control over the observation duration.
            - `version` (Optional[str]): The version of the trace type. Used to understand how changes to the trace type affect metrics. Useful in debugging.

        Trace-specific params:
            - `user_id` (Optional[str]): The id of the user that triggered the execution. Used to provide user-level analytics.
            - `session_id` (Optional[str]): Used to group multiple traces into a session in Langfuse. Use your own session/thread identifier.
            - `release` (Optional[str]): The release identifier of the current deployment. Used to understand how changes of different deployments affect metrics. Useful in debugging.
            - `tags` (Optional[List[str]]): Tags are used to categorize or label traces. Traces can be filtered by tags in the Langfuse UI and GET API.
            - `public` (Optional[bool]): You can make a trace public to share it via a public link. This allows others to view the trace without needing to log in or be members of your Langfuse project.

        Span-specific params:
            - `level` (Optional[SpanLevel]): The severity or importance level of the observation, such as "INFO", "WARNING", or "ERROR".
            - `status_message` (Optional[str]): A message or description associated with the observation's status, particularly useful for error reporting.

        Generation-specific params:
            - `completion_start_time` (Optional[datetime]): The time at which the completion started (streaming). Set it to get latency analytics broken down into time until completion started and completion duration.
            - `model_parameters` (Optional[Dict[str, MapValue]]): The parameters of the model used for the generation; can be any key-value pairs.
            - `usage` (Optional[Union[BaseModel, ModelUsage]]): The usage object supports the OpenAi structure with {promptTokens, completionTokens, totalTokens} and a more generic version {input, output, total, unit, inputCost, outputCost, totalCost} where unit can be of value "TOKENS", "CHARACTERS", "MILLISECONDS", "SECONDS", or "IMAGES". Refer to the docs on how to automatically infer token usage and costs in Langfuse.
            - `prompt`(Optional[PromptClient]): The prompt object used for the generation.

        Returns:
            None

        Raises:
            ValueError: If no current observation is found in the context, indicating that this method was called outside of an observation's execution scope.

        Note:
            - This method is intended to be used within the context of an active observation, typically within a function wrapped by the @observe decorator.
            - It updates the parameters of the most recently created observation on the observation stack. Care should be taken in nested observation contexts to ensure the updates are applied as intended.
            - Parameters set to `None` will not overwrite existing values for those parameters. This behavior allows for selective updates without clearing previously set information.
        """

        langfuse_context.update_current_observation(input=input,
        output=output,
        name=name,
        version=version,
        metadata=metadata,
        start_time=start_time,
        end_time=end_time,
        release=release,
        tags=tags,
        user_id=user_id,
        session_id=session_id,
        level=level,
        status_message=status_message,
        completion_start_time=completion_start_time,
        model=model,
        model_parameters=model_parameters,
        usage=usage,
        prompt=prompt,
        public=public)
