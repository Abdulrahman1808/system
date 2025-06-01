import customtkinter as ctk
from tkinter import ttk, messagebox
from ui_elements import show_error, show_success
from data_handler import load_data, save_data, get_next_id, import_from_excel
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label
)

class InventoryManager:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.inventory = load_data("inventory") or []

    def refresh_inventory(self):
        """Refresh the inventory list from database and update display"""
        try:
            # Import data from Excel before loading from JSON
            import_from_excel()

            # Load inventory from database
            self.inventory = load_data("inventory") or []
            print(f"[DEBUG] Loaded inventory count: {len(self.inventory)}")
            print(f"[DEBUG] Loaded inventory: {self.inventory}")
            
            # Refresh the display
            self.manage_inventory()
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"[TRACEBACK] {traceback_str}")
            show_error(f"Error refreshing inventory: {str(e)}", self.current_language)

    def manage_inventory(self):
        """Create a modern inventory management interface"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create main container
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = create_styled_frame(main_frame, style='card')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        back_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("back", "Back"),
            style='outline',
            command=self.back_callback
        )
        back_button.pack(side='left', padx=20, pady=20)
        
        title_label = create_styled_label(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("manage_inventory", "Manage Inventory"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Add refresh button
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_inventory
        )
        refresh_button.pack(side='right', padx=20, pady=20)
        
        # Summary cards
        summary_frame = create_styled_frame(main_frame, style='card')
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Calculate summary data
        total_items = len(self.inventory)
        low_stock = len([i for i in self.inventory if i.get('quantity', 0) < i.get('min_quantity', 0)])
        out_of_stock = len([i for i in self.inventory if i.get('quantity', 0) <= 0])
        
        # Create summary cards
        summary_cards = [
            ("total_items", "Total Items", total_items),
            ("low_stock", "Low Stock", low_stock),
            ("out_of_stock", "Out of Stock", out_of_stock)
        ]
        
        for i, (key, default_text, value) in enumerate(summary_cards):
            card = create_styled_frame(summary_frame, style='card')
            card.pack(side='left', expand=True, fill='both', padx=10, pady=10)
            
            label = create_styled_label(
                card,
                text=self.LANGUAGES[self.current_language].get(key, default_text),
                style='subheading'
            )
            label.pack(pady=(10, 5))
            
            value_label = create_styled_label(
                card,
                text=str(value),
                style='heading'
            )
            value_label.pack(pady=(0, 10))
        
        # Search and filter section
        search_frame = create_styled_frame(main_frame, style='card')
        search_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        search_entry = create_styled_entry(
            search_frame,
            placeholder_text=self.LANGUAGES[self.current_language].get("search_inventory", "Search inventory...")
        )
        search_entry.pack(side='left', padx=20, pady=20, fill='x', expand=True)
        
        filter_button = create_styled_button(
            search_frame,
            text=self.LANGUAGES[self.current_language].get("filter", "Filter"),
            style='outline'
        )
        filter_button.pack(side='right', padx=20, pady=20)
        
        add_button = create_styled_button(
            search_frame,
            text=self.LANGUAGES[self.current_language].get("add_item", "Add Item"),
            style='primary',
            command=self.add_item
        )
        add_button.pack(side='right', padx=20, pady=20)
        
        # Inventory table (scrollable)
        table_frame = create_styled_frame(main_frame, style='card')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Use CTkScrollableFrame for the inventory list
        scrollable_table = ctk.CTkScrollableFrame(table_frame, orientation='vertical')
        scrollable_table.pack(fill='both', expand=True)
        
        # Table headers
        headers = [
            ("item_name", "Item Name"),
            ("category", "Category"),
            ("quantity", "Quantity"),
            ("min_quantity", "Min Quantity"),
            ("location", "Location"),
            ("actions", "Actions")
        ]
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                scrollable_table,
                text=self.LANGUAGES[self.current_language].get(key, default_text),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        # Inventory list
        for i, item in enumerate(self.inventory, 1):
            # Item details
            name_label = create_styled_label(
                scrollable_table,
                text=item.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            
            category_label = create_styled_label(
                scrollable_table,
                text=item.get('category', ''),
                style='body'
            )
            category_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            
            quantity_label = create_styled_label(
                scrollable_table,
                text=str(item.get('quantity', 0)),
                style='body'
            )
            quantity_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            
            min_quantity_label = create_styled_label(
                scrollable_table,
                text=str(item.get('min_quantity', 0)),
                style='body'
            )
            min_quantity_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
            
            location_label = create_styled_label(
                scrollable_table,
                text=item.get('location', ''),
                style='body'
            )
            location_label.grid(row=i, column=4, padx=10, pady=10, sticky='w')
            
            # Action buttons
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=5, padx=10, pady=10, sticky='w')
            
            edit_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                style='outline',
                width=80,
                command=lambda i=item: self.edit_item(i)
            )
            edit_button.pack(side='left', padx=5)
            
            delete_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                style='outline',
                width=80,
                command=lambda i=item: self.delete_item(i)
            )
            delete_button.pack(side='left', padx=5)

    def add_item(self):
        """Add a new inventory item"""
        # Create a new window for adding item
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get("add_item", "Add Item"))
        dialog.geometry("400x500")
        
        # Create scrollable frame for the form content
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Item form
        form_frame = create_styled_frame(scrollable_form_frame, style='card') # Use styled frame inside scrollable
        form_frame.pack(fill='both', expand=True) # Removed padx, pady as they are on the scrollable frame
        
        # Name
        name_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("item_name", "Item Name"),
            style='subheading'
        )
        name_label.pack(pady=(20, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Category
        category_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("category", "Category"),
            style='subheading'
        )
        category_label.pack(pady=(0, 5))
        
        category_entry = create_styled_entry(form_frame)
        category_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Quantity
        quantity_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("quantity", "Quantity"),
            style='subheading'
        )
        quantity_label.pack(pady=(0, 5))
        
        quantity_entry = create_styled_entry(form_frame)
        quantity_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Min Quantity
        min_quantity_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("min_quantity", "Min Quantity"),
            style='subheading'
        )
        min_quantity_label.pack(pady=(0, 5))
        
        min_quantity_entry = create_styled_entry(form_frame)
        min_quantity_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Location
        location_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("location", "Location"),
            style='subheading'
        )
        location_label.pack(pady=(0, 5))
        
        location_entry = create_styled_entry(form_frame)
        location_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.save_item(
                dialog,
                name_entry.get(),
                category_entry.get(),
                int(quantity_entry.get() or 0),
                int(min_quantity_entry.get() or 0),
                location_entry.get()
            )
        )
        save_button.pack(pady=20)

    def edit_item(self, item):
        """Edit an existing inventory item"""
        # Create a new window for editing item
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get("edit_item", "Edit Item"))
        dialog.geometry("400x500")
        
        # Create scrollable frame for the form content
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Item form
        form_frame = create_styled_frame(scrollable_form_frame, style='card') # Use styled frame inside scrollable
        form_frame.pack(fill='both', expand=True) # Removed padx, pady as they are on the scrollable frame
        
        # Name
        name_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("item_name", "Item Name"),
            style='subheading'
        )
        name_label.pack(pady=(20, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.insert(0, item.get('name', ''))
        name_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Category
        category_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("category", "Category"),
            style='subheading'
        )
        category_label.pack(pady=(0, 5))
        
        category_entry = create_styled_entry(form_frame)
        category_entry.insert(0, item.get('category', ''))
        category_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Quantity
        quantity_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("quantity", "Quantity"),
            style='subheading'
        )
        quantity_label.pack(pady=(0, 5))
        
        quantity_entry = create_styled_entry(form_frame)
        quantity_entry.insert(0, str(item.get('quantity', 0)))
        quantity_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Min Quantity
        min_quantity_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("min_quantity", "Min Quantity"),
            style='subheading'
        )
        min_quantity_label.pack(pady=(0, 5))
        
        min_quantity_entry = create_styled_entry(form_frame)
        min_quantity_entry.insert(0, str(item.get('min_quantity', 0)))
        min_quantity_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Location
        location_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("location", "Location"),
            style='subheading'
        )
        location_label.pack(pady=(0, 5))
        
        location_entry = create_styled_entry(form_frame)
        location_entry.insert(0, item.get('location', ''))
        location_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.update_item(
                dialog,
                item,
                name_entry.get(),
                category_entry.get(),
                int(quantity_entry.get() or 0),
                int(min_quantity_entry.get() or 0),
                location_entry.get()
            )
        )
        save_button.pack(pady=20)
        
        # Cancel button
        cancel_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("cancel", "Cancel"),
            style='outline',
            command=dialog.destroy
        )
        cancel_button.pack(pady=20)

    def save_item(self, dialog, name, category, quantity, min_quantity, location):
        """Save a new inventory item"""
        if not name or not category or quantity < 0 or min_quantity < 0:
            show_error(self.LANGUAGES[self.current_language].get("invalid_item", "Please fill all fields correctly"), self.current_language)
            return

        new_item = {
            'id': get_next_id('inventory'),
            'name': name,
            'category': category,
            'quantity': quantity,
            'min_quantity': min_quantity,
            'location': location
        }
        
        self.inventory.append(new_item)
        save_data("inventory", self.inventory)
        dialog.destroy()
        self.manage_inventory()
        show_success(self.LANGUAGES[self.current_language].get("item_added", "Item added successfully"), self.current_language)

    def update_item(self, dialog, item, name, category, quantity, min_quantity, location):
        """Update an existing inventory item"""
        if not name or not category or quantity < 0 or min_quantity < 0:
            show_error(self.LANGUAGES[self.current_language].get("invalid_item", "Please fill all fields correctly"), self.current_language)
            return

        item.update({
            'name': name,
            'category': category,
            'quantity': quantity,
            'min_quantity': min_quantity,
            'location': location
        })
        
        save_data("inventory", self.inventory)
        dialog.destroy()
        self.manage_inventory()
        show_success(self.LANGUAGES[self.current_language].get("item_updated", "Item updated successfully"), self.current_language)

    def delete_item(self, item):
        """Delete an inventory item"""
        self.inventory.remove(item)
        save_data("inventory", self.inventory)
        self.manage_inventory()
        show_success(self.LANGUAGES[self.current_language].get("item_deleted", "Item deleted successfully"), self.current_language)
