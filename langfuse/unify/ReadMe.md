# Unify Package

## Overview
The `unify` package is designed to manage user traces, metadata, and tags within a unified context. It provides functionalities to create traces for users, add metadata to traces, and manage tags associated with these traces. The package is modular and consists of the following components:

- `UserManager`: Manages user-related trace operations.
- `TraceManager`: Handles trace creation and management.
- `MetadataManager`: Manages metadata associated with traces.
- `TagManager`: Manages tags associated with traces.
- `UnifiedContext`: Provides a context that integrates user traces, metadata, and tags.

## File Structure
The package consists of the following files:
- `__init__.py`: Initializes the package.
- `users.py`: Contains the `UserManager` class.
- `traces.py`: Contains the `TraceManager` class.
- `metadata.py`: Contains the `MetadataManager` class.
- `tags.py`: Contains the `TagManager` class.
- `unify.py`: Contains the `UnifiedContext` class.
- `test_unify.py`: Contains unit tests for the package.

`