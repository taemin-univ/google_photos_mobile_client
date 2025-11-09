import base64

from .models import MediaItem, CollectionItem
from .utils import int64_to_float, int32_to_float, fixed32_to_float, urlsafe_base64


def _parse_media_item(d: dict) -> MediaItem:
    """Parse a single media item from the raw data."""

    dedup_key = next((d["2"]["21"][key] for key in d["2"]["21"] if key.startswith("1")), "")
    if not isinstance(dedup_key, str):
        try:
            dedup_key = urlsafe_base64(base64.b64encode(d["2"]["13"]["1"]).decode())
        except Exception as e:
            raise RuntimeError("Error parsing dedup_key") from e

    origin_map = {
        1: "self",
        3: "partner",
        4: "shared",
    }

    item = MediaItem(
        media_key=d["1"],
        caption=next((d["2"][key] for key in d["2"] if key.startswith("3")), "") or None,
        file_name=d["2"]["4"],
        dedup_key=dedup_key,
        is_canonical=not any(prop.get("1") == 27 for prop in d["2"]["5"]),
        type=d["5"]["1"],
        collection_id=d["2"]["1"]["1"],
        size_bytes=d["2"]["10"],
        timezone_offset=d["2"].get("8", 0),
        utc_timestamp=d["2"]["7"],
        server_creation_timestamp=d["2"]["9"],
        upload_status=d["2"]["11"],
        quota_charged_bytes=d["2"]["35"]["2"],
        origin=origin_map[d["2"]["30"]["1"]],
        content_version=d["2"]["26"],
        trash_timestamp=d["2"]["16"].get("3", 0),
        is_archived=d["2"]["29"]["1"] == 1,
        is_favorite=d["2"]["31"]["1"] == 1,
        is_locked=d["2"]["39"]["1"] == 1,
        is_original_quality=d["2"]["35"]["3"] == 2,
    )

    if d["17"].get("1"):
        item.latitude = fixed32_to_float(d["17"]["1"]["1"])
        item.longitude = fixed32_to_float(d["17"]["1"]["2"])
    if d["17"].get("5"):
        item.location_name = d["17"]["5"]["2"]["1"]
        item.location_id = d["17"]["5"]["3"]

    if d["5"].get("2"):
        # photo
        item.is_edited = "4" in d["5"]["2"]
        item.remote_url = d["5"]["2"]["1"]["1"]
        item.width = d["5"]["2"]["1"]["9"]["1"]
        item.height = d["5"]["2"]["1"]["9"]["2"]
        if d["5"]["2"]["1"]["9"].get("5"):
            item.make = d["5"]["2"]["1"]["9"]["5"].get("1")
            item.model = d["5"]["2"]["1"]["9"]["5"].get("2")
            item.aperture = d["5"]["2"]["1"]["9"]["5"].get("4") and int32_to_float(d["5"]["2"]["1"]["9"]["5"]["4"])
            item.shutter_speed = d["5"]["2"]["1"]["9"]["5"].get("5") and int32_to_float(d["5"]["2"]["1"]["9"]["5"]["5"])
            item.iso = d["5"]["2"]["1"]["9"]["5"].get("6")
            item.focal_length = d["5"]["2"]["1"]["9"]["5"].get("7") and int32_to_float(d["5"]["2"]["1"]["9"]["5"]["7"])

    if d["5"].get("3"):
        # video
        item.remote_url = d["5"]["3"]["2"]["1"]
        if d["5"]["3"].get("4"):
            item.duration = d["5"]["3"]["4"].get("1")
            item.width = d["5"]["3"]["4"].get("4")
            item.height = d["5"]["3"]["4"].get("5")
        item.capture_frame_rate = d["5"]["3"].get("6", {}).get("4") and int64_to_float(d["5"]["3"]["6"]["4"])
        item.encoded_frame_rate = d["5"]["3"].get("6", {}).get("5") and int64_to_float(d["5"]["3"]["6"]["5"])

    if d["5"].get("5", {}).get("2", {}).get("4"):
        # micro video
        item.is_micro_video = True
        item.duration = d["5"]["5"]["2"]["4"]["1"]
        item.micro_video_width = d["5"]["5"]["2"]["4"]["4"]
        item.micro_video_height = d["5"]["5"]["2"]["4"]["5"]

    return item


def _parse_deletion_item(d: dict) -> tuple[int, str | None]:
    """
    Parse a single deletion item from the raw data.
    
    Returns:
        tuple[int, str | None]: (deletion_type, item_key)
            - type 1: media item deletion
            - type 2: collection deletion (primary type)
            - type 4: collection deletion (variant 1)
            - type 6: collection deletion (variant 2)
    """
    import logging
    
    try:
        deletion_type = d["1"]["1"]
        
        # Log all non-type-1 deletions to help debug
        if deletion_type != 1:
            logging.info(f"Deletion type {deletion_type} found, full structure: {d}")
        
        if deletion_type == 1:
            # Type 1 - media item deletion
            # Media deletions have path d["1"]["2"]["1"]
            if "2" in d["1"] and "1" in d["1"]["2"]:
                return (1, d["1"]["2"]["1"])
            else:
                logging.warning(f"Type 1 deletion with unexpected structure: {d}")
        elif deletion_type == 2:
            # Type 2 - collection deletion (uses collection_media_key)
            if "3" in d["1"] and "1" in d["1"]["3"]:
                return (2, d["1"]["3"]["1"])
            logging.warning(f"Type 2 deletion with unexpected structure: {d}")
        elif deletion_type == 4:
            # Collection deletion (type 4) - likely uses album_id
            if "5" in d["1"] and "2" in d["1"]["5"]:
                return (4, d["1"]["5"]["2"])
            logging.warning(f"Type 4 deletion with unexpected structure: {d}")
        elif deletion_type == 6:
            # Collection deletion (type 6) - likely uses media_key
            if "7" in d["1"] and "1" in d["1"]["7"]:
                return (6, d["1"]["7"]["1"])
            logging.warning(f"Type 6 deletion with unexpected structure: {d}")
        else:
            logging.info(f"Unknown deletion type {deletion_type}: {d}")
            
    except Exception as e:
        logging.error(f"Error parsing deletion item: {e}, data: {d}")
    
    return (0, None)


def _parse_collection_item(d: dict) -> CollectionItem:
    """Parse a single collection item from the raw data."""
    return CollectionItem(
        collection_media_key=d["1"],
        collection_album_id=d.get("4", {}).get("2", {}).get("3", ""),
        cover_item_media_key=d.get("2", {}).get("17", {}).get("1"),
        start=d.get("2", {}).get("10", {}).get("6", {}).get("1"),
        end=d.get("2", {}).get("10", {}).get("7", {}).get("1"),
        last_activity_time_ms=d.get("2", {}).get("10", {}).get("10"),
        title=d.get("2", {}).get("5", "Untitled"),
        total_items=d.get("2", {}).get("7", 0),
        type=d.get("2", {}).get("8", 0),
        sort_order=d.get("19", {}).get("1", 0),
        is_custom_ordered=d.get("19", {}).get("2", 0) == 1,
    )


# def _parse_envelope_item(d: dict) -> EnvelopeItem:
#     """Parse a single envelope item from the raw data."""
#     return EnvelopeItem(media_key=d["1"]["1"], hint_time_ms=d["2"])


def _get_items_list(data: dict, key: str) -> list[dict]:
    """Helper to get a list of items from the data, handling single item case."""
    items = data["1"].get(key, [])
    return [items] if isinstance(items, dict) else items


def parse_db_update(data: dict) -> tuple[str, str | None, list[MediaItem], list[CollectionItem], list[str], list[str]]:
    """
    Parse the library state from the raw data.
    
    Returns:
        tuple: (state_token, next_page_token, remote_media, collections, 
                media_keys_to_delete, collection_keys_to_delete)
    """
    next_page_token = data["1"].get("1", "")
    state_token = data["1"].get("6", "")

    # Parse media items
    remote_media = []
    media_items = _get_items_list(data, "2")
    for d in media_items:
        try:
            remote_media.append(_parse_media_item(d))
        except Exception as e:
            # Log the error but continue parsing other items
            import logging
            media_key = d.get("1", "unknown")
            logging.warning(f"Failed to parse media item (key: {media_key}): {type(e).__name__}: {e}")
            continue

    # Parse collections (albums)
    collections = []
    collection_items = _get_items_list(data, "3")
    for d in collection_items:
        try:
            collections.append(_parse_collection_item(d))
        except Exception as e:
            # Log the error but continue parsing other items
            import logging
            collection_key = d.get("1", "unknown")
            logging.warning(f"Failed to parse collection item (key: {collection_key}): {type(e).__name__}: {e}")
            continue

    # Parse deletions (both media items and collections)
    media_keys_to_delete = []
    collection_keys_to_delete = []
    deletions = _get_items_list(data, "9")
    for d in deletions:
        try:
            deletion_type, item_key = _parse_deletion_item(d)
            if item_key:
                if deletion_type == 1:
                    # Media item deletion
                    media_keys_to_delete.append(item_key)
                elif deletion_type in (2, 4, 6):
                    # Collection deletion (type 2 is the primary collection deletion type)
                    collection_keys_to_delete.append(item_key)
        except Exception as e:
            # Log the error but continue parsing other deletions
            import logging
            deletion_type_raw = d.get("1", {}).get("1", "unknown")
            logging.warning(f"Failed to parse deletion item (type: {deletion_type_raw}): {type(e).__name__}: {e}")

    # envelopes = _get_items_list(data, "12")
    # for d in envelopes:
    #     _parse_envelope_item(d)

    return state_token, next_page_token, remote_media, collections, media_keys_to_delete, collection_keys_to_delete
