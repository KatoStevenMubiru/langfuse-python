# Langfuse-Unify Integration

This script integrates Langfuse with Unify, allowing for seamless usage tracking and cost management of OpenAI models used within Unify.

## Overview

The integration involves overriding Unify's OpenAI import with Langfuse's OpenAI integration, tracking model usage and cost, and handling the `model@provider` format used by Unify.

## File Structure

- **`unifyKSM.py`**: Main script that implements the integration.
- **`unify` module**: The Unify module which contains the methods that will be integrated.
- **`langfuse` module**: The Langfuse module which includes the client, decorators, and utilities used for integration.

## Key Components

### Classes

- **UnifyDefinition**: Defines the methods from Unify that will be integrated.
- **UnifyArgsExtractor**: Extracts arguments for Unify methods.
- **LangfuseUnifyIntegration**: Main class that handles the integration of Langfuse with Unify.

### Methods

- **`generate`**: Method that overrides Unify's `generate` method to use Langfuse's OpenAI integration and track usage and cost.

## Logging

Logging is configured to capture information at the INFO level. Logs include information about the model and provider being used and any errors that occur.

## Exception Handling

Exception handling is implemented to log errors during API calls or tracking, ensuring robustness.

## Usage

To use the integration, simply run the `unifyKSM.py` script. An example usage is provided at the end of the script:

```python
if __name__ == "__main__":
    langfuse_unify = LangfuseUnifyIntegration()
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

bash
```
pip install unify langfuse
```
Place the unifyKSM.py script in your working directory.

Running the Script

Run the script using Python:

bash
```python unifyKSM.py
License
```
## This project is licensed under the MIT License.






