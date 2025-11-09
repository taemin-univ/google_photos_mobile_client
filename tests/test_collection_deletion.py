"""
Test for collection deletion functionality.
This test verifies that deleted collections are properly removed from the cache.
"""
import sys
from pathlib import Path

# Add parent directory to path to allow direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import tempfile
import os
from gpmc.db import Storage
from gpmc.models import CollectionItem


class TestCollectionDeletion(unittest.TestCase):
    """Test collection deletion functionality."""

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

    def test_delete_collections_single(self):
        """Test deleting a single collection."""
        # Create test collections
        collection1 = CollectionItem(
            collection_media_key='key_1',
            collection_album_id='album_1',
            title='Album 1',
            total_items=5,
            type=1,
            sort_order=0,
            is_custom_ordered=False
        )
        
        collection2 = CollectionItem(
            collection_media_key='key_2',
            collection_album_id='album_2',
            title='Album 2',
            total_items=10,
            type=1,
            sort_order=0,
            is_custom_ordered=False
        )

        # Insert collections
        with Storage(self.db_path) as storage:
            storage.update_collections([collection1, collection2])

        # Verify both exist
        with Storage(self.db_path) as storage:
            collections = storage.get_collections()
            self.assertEqual(len(collections), 2)

        # Delete one collection
        with Storage(self.db_path) as storage:
            storage.delete_collections(['key_1'])

        # Verify only one remains
        with Storage(self.db_path) as storage:
            collections = storage.get_collections()
            self.assertEqual(len(collections), 1)
            self.assertEqual(collections[0].collection_media_key, 'key_2')

    def test_delete_collections_multiple(self):
        """Test deleting multiple collections at once."""
        # Create test collections
        collections = [
            CollectionItem(
                collection_media_key=f'key_{i}',
                collection_album_id=f'album_{i}',
                title=f'Album {i}',
                total_items=i * 5,
                type=1,
                sort_order=0,
                is_custom_ordered=False
            )
            for i in range(1, 6)
        ]

        # Insert collections
        with Storage(self.db_path) as storage:
            storage.update_collections(collections)

        # Verify all exist
        with Storage(self.db_path) as storage:
            result = storage.get_collections()
            self.assertEqual(len(result), 5)

        # Delete multiple collections
        with Storage(self.db_path) as storage:
            storage.delete_collections(['key_1', 'key_3', 'key_5'])

        # Verify correct ones remain
        with Storage(self.db_path) as storage:
            result = storage.get_collections()
            self.assertEqual(len(result), 2)
            remaining_keys = {c.collection_media_key for c in result}
            self.assertEqual(remaining_keys, {'key_2', 'key_4'})

    def test_delete_collections_empty_list(self):
        """Test that deleting an empty list doesn't cause errors."""
        # Create a test collection
        collection = CollectionItem(
            collection_media_key='key_1',
            collection_album_id='album_1',
            title='Album 1',
            total_items=5,
            type=1,
            sort_order=0,
            is_custom_ordered=False
        )

        with Storage(self.db_path) as storage:
            storage.update_collections([collection])

        # Delete empty list (should be no-op)
        with Storage(self.db_path) as storage:
            storage.delete_collections([])

        # Verify collection still exists
        with Storage(self.db_path) as storage:
            collections = storage.get_collections()
            self.assertEqual(len(collections), 1)

    def test_delete_collections_nonexistent(self):
        """Test deleting collections that don't exist (should not error)."""
        # Create a test collection
        collection = CollectionItem(
            collection_media_key='key_1',
            collection_album_id='album_1',
            title='Album 1',
            total_items=5,
            type=1,
            sort_order=0,
            is_custom_ordered=False
        )

        with Storage(self.db_path) as storage:
            storage.update_collections([collection])

        # Try to delete a non-existent collection
        with Storage(self.db_path) as storage:
            storage.delete_collections(['nonexistent_key'])

        # Verify original collection still exists
        with Storage(self.db_path) as storage:
            collections = storage.get_collections()
            self.assertEqual(len(collections), 1)
            self.assertEqual(collections[0].collection_media_key, 'key_1')

    def test_delete_collections_by_album_id(self):
        """Test deleting collections by album_id instead of media_key."""
        # Create test collections
        collection1 = CollectionItem(
            collection_media_key='media_key_1',
            collection_album_id='album_id_1',
            title='Album 1',
            total_items=5,
            type=1,
            sort_order=0,
            is_custom_ordered=False
        )
        
        collection2 = CollectionItem(
            collection_media_key='media_key_2',
            collection_album_id='album_id_2',
            title='Album 2',
            total_items=10,
            type=1,
            sort_order=0,
            is_custom_ordered=False
        )

        # Insert collections
        with Storage(self.db_path) as storage:
            storage.update_collections([collection1, collection2])

        # Verify both exist
        with Storage(self.db_path) as storage:
            collections = storage.get_collections()
            self.assertEqual(len(collections), 2)

        # Delete one collection by album_id
        with Storage(self.db_path) as storage:
            storage.delete_collections(['album_id_1'])

        # Verify only one remains
        with Storage(self.db_path) as storage:
            collections = storage.get_collections()
            self.assertEqual(len(collections), 1)
            self.assertEqual(collections[0].collection_media_key, 'media_key_2')
            self.assertEqual(collections[0].collection_album_id, 'album_id_2')


if __name__ == '__main__':
    unittest.main()
