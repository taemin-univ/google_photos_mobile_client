import unittest
from pathlib import Path
from gpmc import Client, utils


class TestUpload(unittest.TestCase):
    def setUp(self):
        self.image_file_path = "media/image.png"
        self.image_sha1_hash_b64 = "bjvmULLYvkVj8jWVQFu1Pl98hYA="
        self.image_sha1_hash_hxd = "6e3be650b2d8be4563f23595405bb53e5f7c8580"
        self.directory_path = "C:/Users/admin/Pictures"
        self.mkv_file_path = "media/sample_640x360.mkv"
        self.client = Client()
    def test_restore_from_trash(self):
        """Test restore from trash."""
        dedup_key = utils.urlsafe_base64(self.image_sha1_hash_b64)
        output = self.client.api.restore_from_trash([dedup_key])
        print(output)

    def test_get_download_urls(self):
        """Test get library data."""
        output = self.client.api.get_download_urls("AF1QipOD9PerDX6wrOoWHZKt0361PlyACUJrm8H4NHI")
        print(output)

    def test_set_archived(self):
        """Test get library data."""
        dedup_key = utils.urlsafe_base64(self.image_sha1_hash_b64)
        self.client.api.set_archived([dedup_key], is_archived=False)

    def test_set_favorite(self):
        """Test get library data."""
        dedup_key = utils.urlsafe_base64(self.image_sha1_hash_b64)
        self.client.api.set_favorite(dedup_key, is_favorite=False)

    def test_get_thumbnail(self):
        """Test get library data."""
        self.client.api.get_thumbnail("AF1QipOD9PerDX6wrOoWHZKt0361PlyACUJrm8H4NHI", width=500)

    def test_cache_upate(self):
        """Test get library data."""
        self.client.update_cache()

    def test_set_caption(self):
        """Test filter."""
        dedup_key = utils.urlsafe_base64(self.image_sha1_hash_b64)
        self.client.api.set_item_caption(dedup_key=dedup_key, caption="foobar")

    def test_filter(self):
        """Test filter."""
        response = self.client.upload(target=self.directory_path, filter_exp="copy", filter_ignore_case=True, filter_regex=True)
        print(response)

    def test_add_to_album(self):
        """Test add to album."""
        response = self.client.add_to_album(
            media_keys=["AF1QipPQJJlcp_XbcSuZojLHg19NLkMiziqdjp2FS-6X", "AF1QipMvXu56uuldoyflKD60lctos9u-8BJ_luropFcZ"],
            album_name="TEST",
            show_progress=True,
        )
        print(response)

    def test_move_to_trash(self):
        """Test move to trash."""
        response = self.client.move_to_trash(sha1_hashes=self.image_sha1_hash_hxd)
        print(response)

    def test_image_upload(self):
        """Test image upload."""
        media_key = self.client.upload(target=self.image_file_path, force_upload=True, show_progress=True, saver=True, use_quota=True)
        print(media_key)

    def test_directory_uplod(self):
        """Test directory upload."""
        media_key = self.client.upload(target=self.directory_path, threads=5, show_progress=True)
        print(media_key)

    def test_image_upload_with_hash(self):
        """Test media upload with precalculated hash."""
        hash_pair = {Path(self.image_file_path): self.image_sha1_hash_b64}
        media_key = self.client.upload(target=hash_pair, force_upload=True, show_progress=True)
        print(media_key)

    def test_mkv_upload(self):
        """Test mkv upload."""
        media_key = self.client.upload(target=self.mkv_file_path, force_upload=True, show_progress=True)
        print(media_key)

    def test_hash_check_b64(self):
        """Test hash check b64"""
        if media_key := self.client.get_media_key_by_hash(self.image_sha1_hash_b64):
            print(media_key)
        else:
            print("No remote media with matching hash found.")

    def test_hash_check_hxd(self):
        """Test hash check hxd"""
        if media_key := self.client.get_media_key_by_hash(self.image_sha1_hash_hxd):
            print(media_key)
        else:
            print("No remote media with matching hash found.")

    def test_get_collections(self):
        """Test retrieving collections (albums) from local cache."""
        from gpmc.db import Storage
        
        # First, update the cache to ensure we have collection data
        print("\n=== Updating cache to fetch collections ===")
        self.client.update_cache(show_progress=True)
        
        # Retrieve collections from the database
        print("\n=== Retrieving collections from database ===")
        with Storage(self.client.db_path) as storage:
            # Get all collections
            collections = storage.get_collections()
            
            if collections:
                print(f"\nFound {len(collections)} collection(s):")
                for i, collection in enumerate(collections[:5], 1):  # Show first 5
                    print(f"\n{i}. {collection.title}")
                    print(f"   - Collection Media Key: {collection.collection_media_key}")
                    print(f"   - Album ID: {collection.collection_album_id}")
                    print(f"   - Total Items: {collection.total_items}")
                    print(f"   - Type: {collection.type}")
                    print(f"   - Custom Ordered: {collection.is_custom_ordered}")
                    if collection.cover_item_media_key:
                        print(f"   - Cover Item: {collection.cover_item_media_key}")
                
                if len(collections) > 5:
                    print(f"\n... and {len(collections) - 5} more collection(s)")
                
                # Test retrieving a specific collection
                if collections:
                    print("\n=== Testing get_collection_by_id ===")
                    first_collection = collections[0]
                    retrieved = storage.get_collection_by_id(first_collection.collection_media_key)
                    if retrieved:
                        print(f"✓ Successfully retrieved collection: {retrieved.title}")
                    else:
                        print("✗ Failed to retrieve collection by ID")
            else:
                print("No collections found in the database.")
                print("This may be normal if you have no albums in your Google Photos.")


if __name__ == "__main__":
    unittest.main()
