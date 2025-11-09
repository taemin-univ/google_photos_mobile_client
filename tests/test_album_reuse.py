"""
Test for album reuse functionality.
This test verifies that the add_to_album method properly reuses existing albums
when found in the cache.
"""
import unittest
import tempfile
import os
from pathlib import Path
from gpmc.db import Storage
from gpmc.models import CollectionItem


class TestAlbumReuse(unittest.TestCase):
    """Test album reuse functionality."""

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

    def test_get_collection_by_title_not_found(self):
        """Test get_collection_by_title when collection doesn't exist."""
        with Storage(self.db_path) as storage:
            result = storage.get_collection_by_title('NonExistent')
            self.assertIsNone(result)

    def test_get_collection_by_title_found(self):
        """Test get_collection_by_title when collection exists."""
        # Create a test collection
        test_collection = CollectionItem(
            collection_media_key='test_key_123',
            collection_album_id='album_id_123',
            title='Test Album',
            total_items=5,
            type=1,
            sort_order=0,
            is_custom_ordered=False,
            cover_item_media_key='cover_key_123',
            start=1000000,
            end=2000000,
            last_activity_time_ms=1234567890
        )

        # Insert the collection
        with Storage(self.db_path) as storage:
            storage.update_collections([test_collection])

        # Retrieve it by title
        with Storage(self.db_path) as storage:
            result = storage.get_collection_by_title('Test Album')
            self.assertIsNotNone(result)
            self.assertEqual(result.collection_media_key, 'test_key_123')
            self.assertEqual(result.title, 'Test Album')
            self.assertEqual(result.total_items, 5)

    def test_get_collection_by_title_multiple_with_same_name(self):
        """Test get_collection_by_title returns most recent when multiple exist."""
        # Create two collections with the same name but different activity times
        collection1 = CollectionItem(
            collection_media_key='key_1',
            collection_album_id='album_1',
            title='Duplicate Album',
            total_items=5,
            type=1,
            sort_order=0,
            is_custom_ordered=False,
            last_activity_time_ms=1000000000
        )
        
        collection2 = CollectionItem(
            collection_media_key='key_2',
            collection_album_id='album_2',
            title='Duplicate Album',
            total_items=10,
            type=1,
            sort_order=0,
            is_custom_ordered=False,
            last_activity_time_ms=2000000000  # More recent
        )

        # Insert both collections
        with Storage(self.db_path) as storage:
            storage.update_collections([collection1, collection2])

        # Retrieve by title - should get the most recent one
        with Storage(self.db_path) as storage:
            result = storage.get_collection_by_title('Duplicate Album')
            self.assertIsNotNone(result)
            self.assertEqual(result.collection_media_key, 'key_2')
            self.assertEqual(result.total_items, 10)
            self.assertEqual(result.last_activity_time_ms, 2000000000)

    def test_get_collection_by_title_case_sensitive(self):
        """Test that get_collection_by_title is case-sensitive."""
        test_collection = CollectionItem(
            collection_media_key='test_key',
            collection_album_id='album_id',
            title='MyAlbum',
            total_items=5,
            type=1,
            sort_order=0,
            is_custom_ordered=False
        )

        with Storage(self.db_path) as storage:
            storage.update_collections([test_collection])

        # Test exact match
        with Storage(self.db_path) as storage:
            result = storage.get_collection_by_title('MyAlbum')
            self.assertIsNotNone(result)

        # Test case mismatch - should not find
        with Storage(self.db_path) as storage:
            result = storage.get_collection_by_title('myalbum')
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
