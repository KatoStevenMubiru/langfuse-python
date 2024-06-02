# Langfuse-Unify Integration

This script integrates Langfuse with Unify, allowing for seamless usage tracking and cost management of OpenAI models used within Unify.

## Overview

The integration involves overriding Unify's OpenAI import with Langfuse's OpenAI integration, tracking model usage and cost, and handling the `model@provider` format used by Unify.

## File Structure

- **`unify.py`**: Main script that implements the integration.
- **`unify` module**: The Unify module which contains the methods that will be integrated.
- **`langfuse` module**: The Langfuse module which includes the client, decorators, and utilities used for integration.

## Key Components

### Classes

- **UnifyDefinition**: Defines the methods from Unify that will be integrated.
- **LangfuseUnifyIntegration**: Main class that handles the integration of Langfuse with Unify.

### Methods

- **`generate`**: Method that overrides Unify's `generate` method to use Langfuse's OpenAI integration and track usage and cost.

## Logging

Logging is configured to capture information at the INFO level. Logs include information about the model and provider being used and any errors that occur.

## Exception Handling

Exception handling is implemented to log errors during API calls or tracking, ensuring robustness.

## Environment Variable

The `UNIFY_KEY` environment variable must be set with your Unify API key. This is required for authentication with the Unify service.

## Usage

To use the integration, ensure the `UNIFY_KEY` environment variable is set, and then run the `unify.py` script. An example usage is provided at the end of the script:

```python
if __name__ == "__main__":
    api_key = os.getenv("UNIFY_KEY")
    if not api_key:
        raise EnvironmentError("UNIFY_KEY environment variable not set")

    langfuse_unify = LangfuseUnifyIntegration(api_key)
    try:
        response = langfuse_unify.generate(model="gpt-3.5@openai", prompt="Hello, world!")
        print(response)
    except Exception as e:
        log.error(f"Error during example usage: {e}")
```
## Requirements

Ensure that the unify and langfuse modules are installed and properly configured in your environment.

Installation

Install the required modules:

## bash
```
pip install unify langfuse
Place the unify.py script in your working directory.
```
## Set the UNIFY_KEY environment variable:

## bash
```
export UNIFY_KEY=your_unify_api_key
```

Run the script using Python:

## bash
```
python unify.py
```
License

This project is licensed under the MIT License.

