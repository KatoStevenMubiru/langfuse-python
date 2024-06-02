# test_unify.py
# This module contains unit tests for the modules in the unify package.

import unittest
from users import UserManager
from traces import TraceManager
from metadata import MetadataManager
from tags import TagManager

class TestUnify(unittest.TestCase):

    def setUp(self):
        # Setup code runs before each test method.
        self.user_manager = UserManager()
        self.trace_manager = TraceManager()
        self.metadata_manager = MetadataManager()
        self.tag_manager = TagManager()

    def test_create_trace_for_user(self):
        # Test creating a trace for a user.
        user_id = 'test-user'
        trace = self.user_manager.create_trace_for_user(user_id)
        self.assertIsNotNone(trace, "Trace should not be None")
        print(f"Trace for user {user_id}: {trace}")

    def test_create_trace_with_metadata(self):
        # Test creating a trace with metadata.
        metadata = {'key': 'value'}
        trace = self.trace_manager.create_trace_with_metadata(metadata)
        self.assertIsNotNone(trace, "Trace should not be None")
        self.assertEqual(trace.metadata, metadata, "Metadata should match the input")
        print(f"Trace with metadata {metadata}: {trace}")

    def test_update_user_trace(self):
        # Test updating a user trace.
        user_id = 'test-user'
        self.user_manager.update_user_trace(user_id)
        # You might need to check the internal state of the context or the result of an operation.

    def test_update_trace_metadata(self):
        # Test updating trace metadata.
        metadata = {'key': 'new_value'}
        self.metadata_manager.update_metadata(metadata)
        # Check if the metadata has been updated correctly.

    def test_add_tags(self):
        # Test adding tags to a trace.
        tags = ['tag1', 'tag2']
        self.tag_manager.add_tags(tags)
        # Check if the tags have been added correctly.

if __name__ == '__main__':
    unittest.main()
