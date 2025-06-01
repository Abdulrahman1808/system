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

# MongoDB Connection Variables
client = None
db = None

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
    filename = f"{data_type}.json"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(data_type, data):
    """Save data to both MongoDB and JSON file"""
    try:
        # Save to JSON file
        filename = f"{data_type}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[DEBUG] Saved {len(data)} items to {filename}")
        
        # Save to MongoDB if connection is available
        if db is not None:
            collection = db[data_type]
            # Clear existing data
            collection.delete_many({})
            # Insert new data
            if data:
                collection.insert_many(data)
            print(f"[DEBUG] Saved {len(data)} items to MongoDB {data_type} collection")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error saving data: {str(e)}")
        import traceback
        print(f"[TRACEBACK] {traceback.format_exc()}")
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
    """Get next available ID for a data type"""
    data = load_data(data_type)
    if not data:
        return 1
    # Convert all ids to int safely, ignore non-convertible ids
    ids = []
    for item in data:
        try:
            ids.append(int(item.get('id', 0)))
        except (ValueError, TypeError):
            ids.append(0)
    return max(ids) + 1

def import_from_excel():
    """Import data from Excel files and merge with existing data"""
    try:
        # Import products
        if os.path.exists('hookah_products.xlsx'):
            df = pd.read_excel('hookah_products.xlsx')
            df.columns = df.columns.str.lower()
            excel_products = df.to_dict('records')
            existing_products = load_data('products') or []
            merged_products = merge_data(existing_products, excel_products, 'products')
            save_data('products', merged_products)
            print(f"[DEBUG] Imported {len(merged_products)} products")

        # Import inventory
        if os.path.exists('hookah_inventory.xlsx'):
            df = pd.read_excel('hookah_inventory.xlsx')
            df.columns = df.columns.str.lower()
            excel_inventory = df.to_dict('records')
            existing_inventory = load_data('inventory') or []
            merged_inventory = merge_data(existing_inventory, excel_inventory, 'inventory')
            save_data('inventory', merged_inventory)
            print(f"[DEBUG] Imported {len(merged_inventory)} inventory items")

        # Import suppliers
        if os.path.exists('suppliers.xlsx'):
            df = pd.read_excel('suppliers.xlsx')
            df.columns = df.columns.str.lower()
            excel_suppliers = df.to_dict('records')
            existing_suppliers = load_data('suppliers') or []
            merged_suppliers = merge_data(existing_suppliers, excel_suppliers, 'suppliers')
            save_data('suppliers', merged_suppliers)
            print(f"[DEBUG] Imported {len(merged_suppliers)} suppliers")

        # Import sales
        if os.path.exists('hookah_sales.xlsx'):
            df = pd.read_excel('hookah_sales.xlsx')
            df.columns = df.columns.str.lower()
            excel_sales = df.to_dict('records')
            existing_sales = load_data('sales') or []
            merged_sales = merge_data(existing_sales, excel_sales, 'sales')
            save_data('sales', merged_sales)
            print(f"[DEBUG] Imported {len(merged_sales)} sales")

        # Import employees
        if os.path.exists('hookah_employees.xlsx'):
            df = pd.read_excel('hookah_employees.xlsx')
            df.columns = df.columns.str.lower()
            excel_employees = df.to_dict('records')
            existing_employees = load_data('employees') or []
            merged_employees = merge_data(existing_employees, excel_employees, 'employees')
            save_data('employees', merged_employees)
            print(f"[DEBUG] Imported {len(merged_employees)} employees")

    except Exception as e:
        print(f"[ERROR] Error importing data: {str(e)}")
        import traceback
        print(f"[TRACEBACK] {traceback.format_exc()}")

def merge_data(existing_data, excel_data, data_type):
    """Merge Excel data with existing data, handling conflicts"""
    merged_data = existing_data.copy()
    for excel_item in excel_data:
        # Check if item exists by both id and name
        existing_item = next((item for item in merged_data if item.get('id') == excel_item.get('id') and item.get('name') == excel_item.get('name')), None)
        if existing_item:
            # If all fields match, skip
            if all(existing_item.get(k) == excel_item.get(k) for k in excel_item.keys()):
                continue
            # If fields differ, prompt user
            conflict_fields = [k for k in excel_item.keys() if existing_item.get(k) != excel_item.get(k)]
            prompt_message = f"Item '{excel_item.get('name')}' exists with different {', '.join(conflict_fields)}. Update existing record?"
            if messagebox.askyesno("Conflict", prompt_message):
                existing_item.update(excel_item)
            else:
                # Open editing window by default
                open_edit_window(existing_item, data_type)
        else:
            # If no match, add as new
            merged_data.append(excel_item)
    return merged_data

def open_edit_window(item, data_type):
    """Open editing window for the item based on data type"""
    if data_type == 'products':
        # Open product editing window
        # Example: product_manager.edit_product(item)
        pass
    elif data_type == 'inventory':
        # Open inventory editing window
        # Example: inventory_manager.edit_inventory(item)
        pass
    elif data_type == 'employees':
        # Open employee editing window
        # Example: manage_employees.edit_employee(item)
        pass
    elif data_type == 'suppliers':
        # Open supplier editing window
        # Example: manage_suppliers.edit_supplier(item)
        pass
    elif data_type == 'sales':
        # Open sales editing window
        # Example: record_sale.edit_sale(item)
        pass
    else:
        print(f"[ERROR] Unknown data type: {data_type}")

def export_to_excel():
    """Export data to Excel files"""
    # Export products
    products = load_data('products')
    if products:
        df = pd.DataFrame(products)
        df.to_excel('hookah_products.xlsx', index=False)
    
    # Export inventory
    inventory = load_data('inventory')
    if inventory:
        df = pd.DataFrame(inventory)
        df.to_excel('hookah_inventory.xlsx', index=False)
    
    # Export suppliers
    suppliers = load_data('suppliers')
    if suppliers:
        df = pd.DataFrame(suppliers)
        df.to_excel('suppliers.xlsx', index=False)
    
    # Export sales
    sales = load_data('sales')
    if sales:
        df = pd.DataFrame(sales)
        df.to_excel('hookah_sales.xlsx', index=False)
        
    # Export employees
    employees = load_data('employees')
    if employees:
        df = pd.DataFrame(employees)
        df.to_excel('hookah_employees.xlsx', index=False)

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
