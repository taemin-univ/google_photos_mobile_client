"""
Test for deletion item parsing functionality.
"""
import sys
from pathlib import Path

# Add parent directory to path to allow direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from gpmc.db_update_parser import _parse_deletion_item


class TestDeletionParser(unittest.TestCase):
    """Test deletion item parsing."""

    def test_parse_deletion_type_1_media(self):
        """Test parsing type 1 deletion (media item)."""
        deletion_data = {
            "1": {
                "1": 1,
                "2": {
                    "1": "media_key_123"
                }
            }
        }
        deletion_type, item_key = _parse_deletion_item(deletion_data)
        self.assertEqual(deletion_type, 1)
        self.assertEqual(item_key, "media_key_123")

    def test_parse_deletion_type_4_collection(self):
        """Test parsing type 4 deletion (collection)."""
        deletion_data = {
            "1": {
                "1": 4,
                "5": {
                    "2": "collection_key_456"
                }
            }
        }
        deletion_type, item_key = _parse_deletion_item(deletion_data)
        self.assertEqual(deletion_type, 4)
        self.assertEqual(item_key, "collection_key_456")

    def test_parse_deletion_type_6_collection(self):
        """Test parsing type 6 deletion (collection)."""
        deletion_data = {
            "1": {
                "1": 6,
                "7": {
                    "1": "collection_key_789"
                }
            }
        }
        deletion_type, item_key = _parse_deletion_item(deletion_data)
        self.assertEqual(deletion_type, 6)
        self.assertEqual(item_key, "collection_key_789")

    def test_parse_deletion_unknown_type(self):
        """Test parsing unknown deletion type."""
        deletion_data = {
            "1": {
                "1": 99  # Unknown type
            }
        }
        deletion_type, item_key = _parse_deletion_item(deletion_data)
        self.assertEqual(deletion_type, 0)
        self.assertIsNone(item_key)


if __name__ == '__main__':
    unittest.main()
