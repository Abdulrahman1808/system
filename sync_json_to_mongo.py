import os
import json
from pymongo import MongoClient
from constants import MONGODB_URI, MONGODB_DB_NAME

JSON_PATH = os.path.join('mongodb_data', 'inventory.json')
COLLECTION_NAME = 'inventory'

# --- Sync JSON to MongoDB ---
def sync_json_to_mongo():
    if not os.path.exists(JSON_PATH):
        print(f"JSON file not found: {JSON_PATH}")
        return
    # Load JSON
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]
    collection = db[COLLECTION_NAME]
    updated = 0
    for item in data:
        item_id = item.get('id')
        if item_id is None:
            continue
        # Find by id
        db_item = collection.find_one({'id': item_id})
        if db_item:
            update_fields = {}
            if 'carton_count' in item and item.get('carton_count') != db_item.get('carton_count'):
                update_fields['carton_count'] = item.get('carton_count')
            if 'units_per_carton' in item and item.get('units_per_carton') != db_item.get('units_per_carton'):
                update_fields['units_per_carton'] = item.get('units_per_carton')
            if update_fields:
                collection.update_one({'id': item_id}, {'$set': update_fields})
                updated += 1
    print(f"[MongoDB] Updated {updated} items in MongoDB from inventory.json.")

if __name__ == "__main__":
    sync_json_to_mongo() 