from dotenv import load_dotenv
load_dotenv()  # Load environment variables FIRST

import os
from pymongo import MongoClient, errors
from bson import ObjectId
from constants import *
from ui_elements import show_error, show_success
import pandas as pd
import atexit
import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import re
import shutil

# MongoDB Connection Variables
client = None
db = None

def ensure_data_directories():
    """Ensure data directories exist"""
    os.makedirs(EXCEL_DATA_PATH, exist_ok=True)
    os.makedirs(MONGODB_DATA_PATH, exist_ok=True)

def initialize_db():
    """Initialize MongoDB connection"""
    global client, db
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB_NAME]
        # Test the connection
        client.server_info()
        return True
    except errors.ConnectionFailure as e:
        show_error(f"Could not connect to MongoDB: {str(e)}")
        return False
    except Exception as e:
        show_error(f"Database error: {str(e)}")
        return False

def ensure_collection(collection_name):
    """Ensure a collection exists in MongoDB"""
    if db is not None and collection_name not in db.list_collection_names():
        db.create_collection(collection_name)

def load_data(data_type):
    """Load data from JSON file"""
    if data_type not in MONGODB_COLLECTIONS:
        print(f"[ERROR] Unknown data type: {data_type}")
        return None

    filename = os.path.join(MONGODB_DATA_PATH, f"{MONGODB_COLLECTIONS[data_type]}.json")
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"[DEBUG] Loaded {len(data)} items from {filename}")
            return data
        else:
            print(f"[DEBUG] {filename} not found, returning empty list")
            return []
    except Exception as e:
        print(f"[ERROR] Error loading data from {filename}: {str(e)}")
        return None

def save_data(data_type, data):
    """Save data to both MongoDB and JSON file"""
    if data_type not in MONGODB_COLLECTIONS:
        print(f"[ERROR] Unknown data type for saving: {data_type}")
        return False

    try:
        # Save to JSON file in MongoDB data path
        filename = os.path.join(MONGODB_DATA_PATH, f"{MONGODB_COLLECTIONS[data_type]}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[DEBUG] Saved {len(data)} items to {filename}")
        
        # Save to MongoDB if connection is available
        if db is not None:
            collection = db[MONGODB_COLLECTIONS[data_type]]
            # Clear existing data
            collection.delete_many({})
            # Insert new data
            if data:
                collection.insert_many(data)
            print(f"[DEBUG] Saved {len(data)} items to MongoDB {MONGODB_COLLECTIONS[data_type]} collection")
        
        # Export to Excel after saving to JSON and MongoDB
        export_to_excel(data_type)
        
        return True
    except Exception as e:
        print(f"[ERROR] Error saving data: {str(e)}")
        import traceback
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return False

def export_to_excel(data_type):
    """Export data to Excel file"""
    if data_type not in EXCEL_FILES:
        print(f"[ERROR] Unknown data type for Excel export: {data_type}")
        return False

    try:
        data = load_data(data_type)
        if data is None:
            return False

        df = pd.DataFrame(data)
        excel_path = EXCEL_FILES[data_type]
        df.to_excel(excel_path, index=False)
        print(f"[DEBUG] Exported data to {excel_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error exporting to Excel: {str(e)}")
        return False

def import_from_excel(data_type):
    """Import data from Excel file"""
    if data_type not in EXCEL_FILES:
        print(f"[ERROR] Unknown data type for Excel import: {data_type}")
        return False

    try:
        excel_path = EXCEL_FILES[data_type]
        if not os.path.exists(excel_path):
            print(f"[DEBUG] Excel file not found: {excel_path}")
            return False

        df = pd.read_excel(excel_path)
        data = df.to_dict('records')
        
        # Save the imported data
        return save_data(data_type, data)
    except Exception as e:
        print(f"[ERROR] Error importing from Excel: {str(e)}")
        return False

def load_credentials():
    """Load credentials from file"""
    try:
        with open('hookah_credentials.txt', 'r') as f:
            return f.read().strip().split(',')
    except FileNotFoundError:
        return None

def save_credentials(username, password):
    """Save credentials to file"""
    try:
        with open('hookah_credentials.txt', 'w') as f:
            f.write(f"{username},{password}")
        return True
    except Exception as e:
        show_error(f"Error saving credentials: {str(e)}")
        return False

def insert_document(collection_name, document):
    """Insert a single document into a collection"""
    if db is None:
        show_error("Database connection not available")
        return None
    try:
        collection = db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except Exception as e:
        show_error(f"Error inserting document: {str(e)}")
        return None

def update_document(collection_name, document_id, update_data):
    """Update a document in a collection"""
    if db is None:
        show_error("Database connection not available")
        return False
    try:
        collection = db[collection_name]
        result = collection.update_one(
            {'_id': ObjectId(document_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        show_error(f"Error updating document: {str(e)}")
        return False

def delete_document(collection_name, document_id):
    """Delete a document from a collection"""
    if db is None:
        show_error("Database connection not available")
        return False
    try:
        collection = db[collection_name]
        result = collection.delete_one({'_id': ObjectId(document_id)})
        return result.deleted_count > 0
    except Exception as e:
        show_error(f"Error deleting document: {str(e)}")
        return False

def get_document(collection_name, document_id):
    """Get a single document by ID"""
    if db is None:
        show_error("Database connection not available")
        return None
    try:
        collection = db[collection_name]
        document = collection.find_one({'_id': ObjectId(document_id)})
        if document:
            document['_id'] = str(document['_id'])
        return document
    except Exception as e:
        show_error(f"Error getting document: {str(e)}")
        return None

def get_next_id(data_type):
    """Generate the next available ID for a data type"""
    data = load_data(data_type)
    if data is None:
        return "1"
    
    if not data:
        return "1"

    # Ensure IDs are treated as strings when checking for maximum
    if data_type == 'sales':
        # Assuming sales IDs are sequential numbers as strings
        max_id = 0
        for item in data:
            try:
                # Convert to int for comparison, handle potential non-numeric IDs gracefully
                item_id = int(item.get('id', 0))
                if item_id > max_id:
                    max_id = item_id
            except ValueError:
                # Ignore items with non-integer IDs for max calculation
                pass
        return str(max_id + 1)

    # For other data types, assume IDs are strings and find the max numeric part
    # This is a simplified approach, adjust if IDs have different formats
    max_numeric_id = 0
    for item in data:
        item_id_str = item.get('id', '0')
        # Try to extract a leading numeric part from the string ID
        numeric_part_match = re.match(r'^\d+', item_id_str)
        if numeric_part_match:
            numeric_part = int(numeric_part_match.group(0))
            if numeric_part > max_numeric_id:
                max_numeric_id = numeric_part
    
    # If no numeric IDs were found or data is empty, start from 1
    if max_numeric_id == 0 and data:
         # If there's data but no numeric IDs were found, return a default or handle as needed
         # For simplicity, let's still increment from 0 if no numeric part was found in any ID
         return str(len(data) + 1) # Fallback to count if no parsable IDs


    return str(max_numeric_id + 1)

def format_date(date):
    """Format date to string"""
    if isinstance(date, datetime):
        return date.strftime('%Y-%m-%d %H:%M:%S')
    return date

def validate_data(data_type, data):
    """Validate data before saving"""
    required_fields = {
        'products': ['name', 'category', 'price', 'quantity', 'status'],
        'inventory': ['name', 'category', 'quantity', 'min_quantity', 'location'],
        'suppliers': ['name', 'contact', 'email', 'phone', 'status'],
        'sales': ['items', 'total', 'date']
    }
    
    if data_type not in required_fields:
        return False
    
    for field in required_fields[data_type]:
        if field not in data:
            return False
    
    return True

def search_data(data_type, query):
    """Search data by query"""
    data = load_data(data_type)
    if not query:
        return data
    
    results = []
    query = query.lower()
    
    for item in data:
        for value in item.values():
            if isinstance(value, str) and query in value.lower():
                results.append(item)
                break
    
    return results

def filter_data(data_type, filters):
    """Filter data by criteria"""
    data = load_data(data_type)
    if not filters:
        return data
    
    results = data
    for key, value in filters.items():
        results = [item for item in results if item.get(key) == value]
    
    return results

def close_connection():
    """Close the MongoDB connection"""
    global client
    if client is not None:
        client.close()

def import_excel_to_db(file_path, collection_name):
    """Import data from Excel file to MongoDB"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        # Insert data into MongoDB
        collection = get_collection(collection_name)
        if collection:
            collection.insert_many(data)
            return True
    except Exception as e:
        print(f"Error importing data: {str(e)}")
        return False

def get_collection(collection_name):
    """Get a MongoDB collection"""
    if db is None:
        show_error("Database connection not available")
        return None
    try:
        return db[collection_name]
    except Exception as e:
        show_error(f"Error getting collection: {str(e)}")
        return None

def save_data(collection_name, data):
    """Save data to MongoDB collection"""
    try:
        collection = get_collection(collection_name)
        if collection is not None:
            # Clear existing data
            collection.delete_many({})
            # Insert new data
            if data:
                collection.insert_many(data)
            return True
    except Exception as e:
        print(f"Error saving data: {str(e)}")
    return False

def load_data(collection_name):
    """Load data from MongoDB collection"""
    try:
        collection = get_collection(collection_name)
        if collection is not None:
            # Get all documents and remove _id field
            documents = list(collection.find({}, {'_id': 0}))
            return documents
    except Exception as e:
        print(f"Error loading data: {str(e)}")
    return []

def delete_document(collection_name, document_id):
    """Delete a document from MongoDB collection"""
    try:
        collection = get_collection(collection_name)
        if collection is not None:
            result = collection.delete_one({'_id': document_id})
            return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
    return False

# Initialize database connection when module loads
if initialize_db():
    # Initialize collections
    collections = ['products', 'suppliers', 'employees', 'sales']
    for collection in collections:
        ensure_collection(collection)
else:
    show_error("Failed to initialize database connection")

# Close the connection when the program exits
atexit.register(close_connection)
