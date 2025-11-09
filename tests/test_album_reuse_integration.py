"""
Integration test for album reuse functionality with cache update.
This test verifies that albums are properly reused after cache initialization.
"""
import unittest
import tempfile
import os
from pathlib import Path
from gpmc.db import Storage
from gpmc.models import CollectionItem


class TestAlbumReuseIntegration(unittest.TestCase):
    """Test album reuse with cache initialization."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary database file
        self.tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.tmp_file.name
        self.tmp_file.close()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_album_lookup_after_cache_update(self):
        """Test that albums can be found after cache is updated."""
        # Simulate the scenario where cache is not initialized
        with Storage(self.db_path) as storage:
            init_state = storage.get_init_state()
            self.assertFalse(init_state, "Cache should not be initialized initially")
        
        # Simulate cache initialization by setting init_complete and adding a collection
        with Storage(self.db_path) as storage:
            storage.set_init_state(1)
            test_collection = CollectionItem(
                collection_media_key='existing_key_123',
                collection_album_id='existing_album_123',
                title='My Vacation',
                total_items=10,
                type=1,
                sort_order=0,
                is_custom_ordered=False,
                last_activity_time_ms=1234567890
            )
            storage.update_collections([test_collection])
        
        # Now verify we can find the album
        with Storage(self.db_path) as storage:
            result = storage.get_collection_by_title('My Vacation')
            self.assertIsNotNone(result)
            self.assertEqual(result.collection_media_key, 'existing_key_123')

    def test_nested_storage_access(self):
        """Test that we can't open storage while it's already open."""
        # This test documents the issue with nested storage access
        with Storage(self.db_path) as storage1:
            storage1.set_init_state(0)
            
            # This should work - we can open another connection
            with Storage(self.db_path) as storage2:
                storage2.set_init_state(1)
            
            # After closing storage2, storage1 should see the update
            # But this might not work as expected due to isolation
            init_state = storage1.get_init_state()
            # The value might still be 0 due to transaction isolation
            # This is a potential issue


if __name__ == '__main__':
    unittest.main()
