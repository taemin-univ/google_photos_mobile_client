#!/usr/bin/env python3
"""
Debug script to check if collections are in the cache
"""
import os
from pathlib import Path
from gpmc import Client
from gpmc.db import Storage

# Initialize client
try:
    client = Client()
    print(f"✓ Client initialized")
    print(f"  Cache directory: {client.cache_dir}")
    print(f"  Database path: {client.db_path}")
    
    # Check if database exists
    if client.db_path.exists():
        print(f"✓ Database exists")
        
        # Check collections in database
        with Storage(client.db_path) as storage:
            collections = storage.get_collections()
            print(f"\nFound {len(collections)} collections in cache:")
            
            if collections:
                for i, col in enumerate(collections[:10], 1):
                    print(f"  {i}. '{col.title}' (key: {col.collection_media_key[:20]}..., items: {col.total_items})")
                
                # Try to find "아린"
                arin_album = storage.get_collection_by_title("아린")
                if arin_album:
                    print(f"\n✓ Found '아린' album in cache!")
                    print(f"  Key: {arin_album.collection_media_key}")
                    print(f"  Items: {arin_album.total_items}")
                else:
                    print(f"\n✗ '아린' album NOT found in cache")
                    
                # Try to find "New 아린"
                new_arin_album = storage.get_collection_by_title("New 아린")
                if new_arin_album:
                    print(f"\n✓ Found 'New 아린' album in cache!")
                    print(f"  Key: {new_arin_album.collection_media_key}")
                else:
                    print(f"\n✗ 'New 아린' album NOT found in cache")
            else:
                print("  No collections found in cache!")
                print("\n⚠ This means cache needs to be updated or initialized")
                print("  Run: client.update_cache(show_progress=True)")
    else:
        print(f"✗ Database does not exist at {client.db_path}")
        print("  Cache needs to be initialized")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
