import pytest
from unittest.mock import patch, MagicMock
from unify import main

# Fixture to mock the managers used in the unify module
@pytest.fixture
def mock_managers():
    with patch('unify.UserManager') as mock_user_manager, \
         patch('unify.TraceManager') as mock_trace_manager, \
         patch('unify.MetadataManager') as mock_metadata_manager, \
         patch('unify.TagManager') as mock_tag_manager:
        
        mock_user_manager.return_value.create_trace_for_user.return_value = 'user-trace-id'
        mock_trace_manager.return_value.create_trace_with_metadata.return_value = 'trace-with-metadata'
        yield mock_user_manager, mock_trace_manager, mock_metadata_manager, mock_tag_manager

# Test the main functionality in unify.py
def test_main_functionality(mock_managers):
    mock_user_manager, mock_trace_manager, mock_metadata_manager, mock_tag_manager = mock_managers
    
    # Run the main function
    with patch('builtins.print') as mock_print:
        main()

    # Assertions to check if the right methods were called with expected arguments
    mock_user_manager.return_value.create_trace_for_user.assert_called_once_with('user-id')
    mock_trace_manager.return_value.create_trace_with_metadata.assert_called_once_with({'key': 'value'})
    mock_metadata_manager.return_value.update_metadata.assert_called_once_with({'key': 'new_value'})
    mock_tag_manager.return_value.add_tags.assert_called_once_with(['tag1', 'tag2'])

    # Check print outputs
    mock_print.assert_any_call("User Trace: user-trace-id")
    mock_print.assert_any_call("Trace with Metadata: trace-with-metadata")
    mock_print.assert_any_call("Metadata updated.")
    mock_print.assert_any_call("Tags added.")

# Run the tests
if __name__ == "__main__":
    pytest.main()